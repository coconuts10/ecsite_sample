from django import forms
from .models import CartItems, Addresses
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.cache import cache

#forms.pyはlabelを付けるだけでも意味があるが、バリデーションや入力設定などもできる。
class CartUpdateForm(forms.ModelForm):
    quantity = forms.IntegerField(label='数量', min_value=1)
    id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = CartItems
        fields = ['quantity', 'id'] #ここでは利用するカラムを指定している。

    def clean(self):
        cleaned_data = super().clean()  #cleaned_dataはバリデートした後の値しか入らない。それに対して、Views.pyにあった、request.POST.get()はrequestの値をそのままとっているだけ。
        quantity = cleaned_data.get('quantity')
        id = cleaned_data.get('id')
        cart_item = get_object_or_404(CartItems, pk=id)
        if quantity > cart_item.product.stock:
            raise ValidationError(f'在庫数を超えています{cart_item.product.stock}以下にしてください')

class AddressInputForm(forms.ModelForm):
    address = forms.CharField(label='住所', widget=forms.TextInput(attrs={'size': '80'})) #attrsにより、HTMLのwidgetを修正することができる。

    class Meta:
        model = Addresses
        fields = ['zip_code', 'prefecture', 'address']
        labels = {
            'zip_code': '郵便番号',
            'prefecture': '都道府県',
        }

    def save(self): #今回addressテーブルはusersを外部キーで接続しているため、user情報も保存する必要がある。
                    #views.pyのform_validで取得したユーザー情報をここでテーブルに保存するようにsaveメソッドをオーバーライドしている。
        address = super().save(commit=False)
        address.user = self.user
        try:
            address.validate_unique()   #ユニークエラーが発生した場合、ValidationErrorとなる。
            address.save()
        except ValidationError as e:
            address = get_object_or_404(
                Addresses,
                user=self.user,
                prefecture=address.prefecture,
                zip_code=address.zip_code,
                address=address.address
            )
            pass
        cache.set(f'address_user_{self.user.id}', address)  #address_user_{self.user.id}にaddress情報を保存する。
        return address

