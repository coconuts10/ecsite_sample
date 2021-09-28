from django.urls import path
from .views import (
    RegistUserView, HomeView, UserLoginView, UserLogoutView, UserView
)

app_name = 'accounts'
urlpatterns = [
    #as_view()とはDjangoのビューの条件を満たす関数を生成している。（クラスを関数化している）
    #ビューの条件を満たす関数とは、Djangoの標準ライブラリにある、view関連のライブラリを継承できているクラスであるということ
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('user/', UserView.as_view(), name='user')
]