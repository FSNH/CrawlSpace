from django import forms


# 继承forms.Form
class LoginForm(forms.Form):
    # 如果为空则报错
    username = forms.CharField(label="账 号：", min_length=3, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "输入帐号", 'autofocus': ''}))
    pwd = forms.CharField(label="密 码：", min_length=3, required=True,
                          widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "输入密码"}))
