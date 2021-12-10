from django import forms
from .models import Profile
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
import datetime


year = datetime.datetime.today().year  # 올해 년도

class ProfileForm(forms.ModelForm):
    name = forms.CharField(
        label='이름',
        widget=forms.TextInput(
            attrs={
                'maxlength': 10,
            }
        )
    )
    WEX = forms.DateField(
        label='경력 시작일',
        widget=forms.SelectDateWidget(years=range(1960, year + 1))
        )
    DOB = forms.DateField(
        label='생년월일',
        widget=forms.SelectDateWidget(years=range(1960, year + 1))
        )
    team = forms.IntegerField(label='팀',min_value = 0, initial=0)
    level = forms.IntegerField(
        label='레벨',
        max_value = 2,
        min_value = 0,
        initial=0
    )

    class Meta:
        model = Profile
        exclude = ('user', 'OFF', 'PTO',)


class ProfileUpdateForm(forms.ModelForm):
    name = forms.CharField(
        label='이름',
        widget=forms.TextInput(
            attrs={
                'maxlength': 10,
            }
        )
    )
    WEX = forms.DateField(
        label='경력 시작일',
        widget=forms.SelectDateWidget(years=range(1960, year + 1))
        )
    DOB = forms.DateField(
        label='생년월일',
        widget=forms.SelectDateWidget(years=range(1960, year + 1))
        )
    team = forms.IntegerField(label='팀',min_value = 0, widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    level = forms.IntegerField(
        label='레벨',
        max_value = 2,
        min_value = 0,
        widget=forms.NumberInput(attrs={'readonly':'readonly'})
    )

    class Meta:
        model = Profile
        exclude = ('user', 'OFF', 'PTO',)
        

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name',)


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields