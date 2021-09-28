from django.shortcuts import render, redirect
from django.views.generic.base import (
    TemplateView, View
)
from django.views.generic.edit import (
    CreateView, FormView
)
from .forms import RegistForm, UserLoginForm
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView

# Create your views here.

class HomeView(TemplateView):
    template_name = 'home.html'

class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm


class  UserLoginView(LoginView):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm
    #LoginViewを継承することで、自分でnext_urlの定義をしなくても、その処理を行ってくれる。

    def form_valid(self, form):
        remember = form.cleaned_data['remember']    #cleaned_dataはフォームにて渡しているhtml上のnameを読み取っている。
        if remember:
            self.request.session.set_expiry(120000) #これをセットすることで、settings.pyでのSESSION_COOKIE_AGEではなく、こちらの値を優先する。
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    pass

#@method_decorator(login_required, name='dispatch')
class UserView(LoginRequiredMixin,TemplateView):
    template_name = 'user.html'

    #@method_decorator(login_required)   #dispatchを呼ぶとき、ログインしていないと処理ができなくさせた。
    def dispatch(self, *args, **kwargs):   #ディスパッチは、postだったらpostのgetだったらgetの処理を行う
        return super().dispatch(*args, **kwargs)

