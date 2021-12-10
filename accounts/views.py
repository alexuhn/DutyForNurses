from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .forms import ProfileForm, ProfileUpdateForm, CustomUserChangeForm, CustomUserCreationForm
from .models import Profile
import datetime


@login_required
@require_safe
def profile(request, nurse_pk):
    # 남의 프로필을 보려는 경우 자신의 듀티로 리다이렉트
    if request.user.pk != nurse_pk:
        return redirect('schedule:personal', request.user.pk)

    nurse = get_object_or_404(get_user_model(), pk=nurse_pk)
    does_exist = False  # 프로필이 존재하는가

    if Profile.objects.filter(user_id=nurse_pk).exists():
        does_exist = True
        profile = Profile.objects.get(user_id=nurse_pk)

        # 경력과 나이를 햇수로 계산
        WEX = datetime.date.today() - profile.WEX 
        WEX = int(WEX.days // 365.25)
        age = datetime.date.today() - profile.DOB
        age = int(age.days // 365.25)
 
        context = {
            'nurse': nurse,
            'profile': profile,
            'WEX': WEX,
            'age': age,
            'does_exist': does_exist,
        }
        return render(request, 'accounts/profile.html', context)
    context = {
        'nurse': nurse,
        'does_exist': does_exist,
    }
    return render(request, 'accounts/profile.html', context)


@require_http_methods(['GET', 'POST'])
def update_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return redirect('accounts:profile', request.user.pk)
        else:
            form = ProfileUpdateForm(instance=request.user.profile)
        context = {
            'form': form,
        }
        return render(request, 'accounts/update_profile.html', context)
    return redirect('accounts:login')


@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated:
        return redirect('schedule:personal', request.user.pk)

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or 'schedule:personal', request.user.pk)
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)


def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('accounts:login')


@require_http_methods(['GET', 'POST'])
def signup(request):                                    
    if request.user.is_authenticated:
        return redirect('schedule:index')

    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_creation_form.is_valid() and profile_form.is_valid():
            user = user_creation_form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            auth_login(request, user)
            return redirect('accounts:profile', request.user.pk)
    else:
        user_creation_form = CustomUserCreationForm()
        profile_form = ProfileForm()
    context = {
        'user_creation_form': user_creation_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/signup.html', context)


@require_POST
def delete(request):
    if request.user.is_authenticated:
        request.user.delete()
        auth_logout(request)
    return redirect('schedule:index') 


@login_required
@require_http_methods(['GET', 'POST'])
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('schedule:index')
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/update.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('schedule:index')
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)