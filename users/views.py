from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django import forms
from .models import CustomUser
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from .tokens import account_activation_token


def activateEmail(request, user, to_email):
    mail_subject = "Activate your account"
    message = render_to_string('users/activate_account.html', {
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[to_email])

    if email.send():
        messages.success(request, f'Kindly check your inbox at {to_email} to activate your account')
    else:
        messages.error(request, f'Problem sending email to {to_email}, please check on the email and try again')
        
def account_activated(request):
    return render(request, 'users/account_activated.html', {'title': 'Account Activated'})

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')
        
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for confirming your email, you may now log in.")
        return redirect('account_activated')
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return render(request, 'users/account_activation_invalid.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return render(request, 'users/account_activation_sent.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form, 'title': 'Sign Up'})


def custom_logout(request):
    logout(request)
    return redirect('login')