from django.urls import path
from .views import (ProductListView, ProductDetailView, add_product, CartItemView,
                    CartDeleteView, CartUpdateView, InputAddressView, ConfirmOrderView,
                    OrderSuccessView)

app_name = 'stores'
urlpatterns = [
    path('product_list/', ProductListView.as_view(), name='product_list'),
    path('product_detail/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('add_product/', add_product, name='add_product'),  #add_productのURLにユーザーのブラウザ上でアクセスするわけではない。product_detail上で該当ボタンがクリックされたら、ajaxが起動して、裏でadd_product/にアクセスしてviews.pyを動かしている。
    path('cart_items/', CartItemView.as_view(), name='cart_items'),
    path('update_cart/<int:pk>', CartUpdateView.as_view(), name='update_cart'),
    path('delete_cart/<int:pk>', CartDeleteView.as_view(), name='delete_cart'),
    path('input_address/', InputAddressView.as_view(), name='input_address'),   #pkがないときと、
    path('input_address/<int:pk>', InputAddressView.as_view(), name='input_address'),   #pkがあるときの2パターンをひょうじすることができる。
    path('confirm_order/', ConfirmOrderView.as_view(), name='confirm_order'),
    path('order_success/', OrderSuccessView.as_view(), name='order_success'),
]