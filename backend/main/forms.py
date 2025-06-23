from django import forms
from main.models import Cryptocurrency, User

class CryptocurrencyAdminForm(forms.ModelForm):
    # price = forms.DecimalField(
    #     label="Цена",
    #     max_digits=20,
    #     decimal_places=8,
    #     widget=forms.NumberInput(attrs={'step': '0.00000001'})
    # )

    class Meta:
        model = Cryptocurrency
        fields = "__all__"
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.00000001'})
        }

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "name"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
