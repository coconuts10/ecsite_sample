from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from .models import (Products, Carts, CartItems, Addresses, Orders, OrderItems)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.generic.edit import (
    UpdateView, CreateView, DeleteView
)
from django.urls import reverse_lazy
from .forms import CartUpdateForm, AddressInputForm
from django.core.cache import cache
from django.db import transaction

class ProductListView(LoginRequiredMixin, ListView):    #LoginRequiredMixinにより、ログインしないと、このクラスは呼ばれなくなる。
                                                        #ログインしていないときにこの画面を呼ぼうよしたら、settings.pyのLOGIN_URLのURLが呼ばれる。
    model =  Products
    template_name = os.path.join('stores', 'product_list.html')

    def get_queryset(self): #get_querysetはインスタンスの一覧を返すメソッド。このように、get_querysetをオーバーライドして使うことが一般的。
        query = super().get_queryset()
        product_type_name = self.request.GET.get('product_type_name') #product_type_nameはproduct_list.htmlから送られた情報を受け取っている
        product_name = self.request.GET.get('product_name')
        if product_type_name:
            query = query.filter(
                product_type__name=product_type_name    #左辺のproduct_type__nameは、produc_typesテーブルに紐づくnameを意味している（テーブル名はproduct_typesだが、produtcテーブル内のカラム名はproduct_type）
            )
        if product_name:
            query = query.filter(
                name = product_name
            )
        order_by_price = self.request.GET.get('order_by_price', 0)
        if order_by_price == '1':
            query = query.order_by('price')
        elif order_by_price == '2':
            query =query.order_by('-price')
        return query

    def get_context_data(self, **kwargs):   #get_context_dataはテンプレートに渡す変数を設定する。
        context = super().get_context_data(**kwargs)
        context['product_type_name'] = self.request.GET.get('product_type_name', '')
        context['product_name'] = self.request.GET.get('product_name', '')
        order_by_price = self.request.GET.get('order_by_price', 0)
        if order_by_price == '1':
            context['ascending'] = True
        elif order_by_price == '2':
            context['descending'] = True
        return context

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Products
    template_name = os.path.join('stores', 'product_detail.html')

    def get_context_data(self, **kwargs):   #**kwargsは辞書型であり、htmlから渡される引数のid:値を受け取る器
        context = super().get_context_data(**kwargs)
        context['is_added'] = CartItems.objects.filter(
            cart_id = self.request.user.id,
            product_id = kwargs.get('object').id
        ).first()
        return context

@login_required
def add_product(request):
    if request.is_ajax:
        product_id = request.POST.get('product_id') #product_idはproduct_detailのAJAXから送られている。
        quantity = request.POST.get('quantity') #request.POST.get()でテンプレートから送られたデータを取得する。
        product = get_object_or_404(Products, id=product_id)
        if int(quantity) > product.stock:
            response = JsonResponse({'message': '在庫数を超えています'})
            response.status_code = 403
            return response
        if int(quantity) <= 0:
            response = JsonResponse({'message': '0より大きい値を入力してください'})
            response.status_code = 403
            return response
        cart = Carts.objects.get_or_create(
            user=request.user
        )
        if all([product_id, cart, quantity]):
            CartItems.objects.save_item(
                quantity=quantity, product_id=product_id, cart=cart[0]
            )
            return JsonResponse({'message': '商品をカートに追加しました'})

class CartItemView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('stores', 'cart_items.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        query = CartItems.objects.filter(cart_id=user_id)
        total_price = 0
        items = []
        for item in query.all():
            total_price += item.quantity * item.product.price
            picture = item.product.productpictures_set.first()
            picture = picture.picture if picture else None
            in_stock = True if item.product.stock >= item.quantity else False
            tmp_item = {
                'quantity': item.quantity,
                'picture': picture,
                'name': item.product.name,
                'id': item.id,
                'price': item.product.price,
                'in_stock':in_stock
            }
            items.append(tmp_item)
        context['total_price'] = total_price
        context['items'] = items
        return context

class CartUpdateView(LoginRequiredMixin, UpdateView):   #UpdateView, CreateView, DeleteViewはテーブルのアップデートを行うためmodelを記載しておく
    template_name = os.path.join('stores','update_cart.html' )
    form_class = CartUpdateForm
    model = CartItems   #ここでインスタンス化しており、テンプレートでobjectで呼べる。urlの引数でpkも指定しているため、該当レコードが取り出せる。
    success_url = reverse_lazy('stores:cart_items')

class CartDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('stores', 'delete_cart.html')
    model = CartItems
    success_url = reverse_lazy('stores:cart_items')
    #'delete_cart.htmlでsubmitすると、ここでの処理が走る。（クラスベースビューだからあまりに簡単に実施されるが、関数ベースだとviews.pyやforms.pyなどでhttpリクエストを受けたことをトリガーにDBを削除する処理が行われる文を書いていた。）

class InputAddressView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('stores', 'input_address.html')
    form_class = AddressInputForm
    success_url = reverse_lazy('stores:confirm_order')

    def get(self, request, pk=None):
        cart = get_object_or_404(Carts, user_id=request.user.id)
        if not cart.cartitems_set.all():   #Cartsにはcartsitemsのカラムはない。_set.all()は、外部キーの参照元の方の情報を取得する。
                                            #ここでは、cartsitemsがcartsを紐づけているので、cartsitemsの情報を見ている。
            raise Http404('商品が入っていません')
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address = cache.get(f'address_user_{self.request.user.id}')
        pk = self.kwargs.get('pk')  #遷移元から渡された引数（pk）を入力
        address = get_object_or_404(Addresses, user_id=self.request.user.id, pk=pk) if pk else address  #pkを取得できている場合、その住所情報を渡す。
        if address:
            context['form'].fields['zip_code'].initial = address.zip_code
            context['form'].fields['prefecture'].initial = address.prefecture
            context['form'].fields['address'].initial = address.address
        context['addresses'] = Addresses.objects.filter(user=self.request.user).all() #インスタンス化したAddressesがobjectsであり、ここからフィルターして情報を取得する。
        return context

    def form_valid(self, form): #ｆｏｒｍ_validはデータがポストされたときに呼ばれる。今回、InputAddressViewではaddressesモデルを使用してるが、
                                #addressesはusersを外部キーで紐づけているため、httprequestからuser_idを取得する必要がある。
        form.user = self.request.user
        return super().form_valid(form)


class ConfirmOrderView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('stores', 'confirm_order.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address = cache.get(f'address_user_{self.request.user.id}')
        context['address'] = address
        cart = get_object_or_404(Carts, user_id=self.request.user.id)
        context['cart'] = cart  #ここでcartのidを取得
        total_price = 0
        items = []
        for item in cart.cartitems_set.all():   #取得したcartのidをもとに、cart_itemsの情報を取得
            total_price += item.quantity * item.product.price
            picture = item.product.productpictures_set.first()
            picture = picture.picture if picture else None
            tmp_item = {
                'quantity': item.quantity,
                'picture': picture,
                'name': item.product.name,
                'price': item.product.price,
                'id': item.id,
            }
            items.append(tmp_item)
        context['total_price'] = total_price
        context['items'] = items
        return context

    @transaction.atomic #関数内のDB更新処理の完全性を保証する。すべてOKだったら保存されるが、何かが失敗したら、更新前にロールバックする。
    def post(self, *args, **kwargs):
        context = self.get_context_data()   #上記get_context_dataにいれた値をここに入れることができる。（確認時にいれた値を入れられる）
        address = context.get('address')    #context.get()もcontext[]も値を取るのには変わらない
        cart = context.get('cart')
        total_price = context.get('total_price')
        if (not address) or (not cart) or(not total_price):
            raise Http404('注文処理でエラーが発生しました')
        for item in cart.cartitems_set.all():
            if item.quantity > item.product.stock:
                raise Http404('注文処理でエラーが発生しました')
        order = Orders.objects.insert_cart(cart, address, total_price)
        OrderItems.objects.insert_cart_items(cart, order)
        Products.objects.reduce_stock(cart)
        cart.delete()   #CASCADEなのcartitemsも削除される
        return redirect(reverse_lazy('stores:order_success'))

class OrderSuccessView(LoginRequiredMixin, TemplateView):

    template_name = os.path.join('stores', 'order_success.html')
