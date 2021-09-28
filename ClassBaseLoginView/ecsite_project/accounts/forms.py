from django import forms
from .models import Users
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm

class RegistForm(forms.ModelForm):
    username = forms.CharField(label='名前')
    age = forms.IntegerField(label='年齢', min_value=0)
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ['username', 'age', 'email', 'password']

    def save(self, commit=False):   #saveメソッドの編集はforms.pyで行う。
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'],user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

# class UserLoginForm(forms.Form):
#     email = forms.EmailField(label='メールアドレス')
#     password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
class UserLoginForm(AuthenticationForm):    #AuthenticationFormでuser情報を持っている。
    username = forms.EmailField(label='メールアドレス')   #ユーザー情報を一意に識別するもの
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False)  #ここはモデルは関係なく、フォーム上にセットしてチェックボックスなだけ。
