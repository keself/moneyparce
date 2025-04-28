from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import EmailVerificationCode
from django.conf import settings
import random

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
                      {'template_data' : template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password'],
        )
        if user is None:
            template_data['error'] = 'The username or password is inorrect.'
            return render(request, 'accounts/login.html',
                          {'template_data' : template_data})
        else:
            # Generate 6-digit code
            code = str(random.randint(100000, 999999))
            EmailVerificationCode.objects.create(user=user, code=code)

            # Send email
            send_mail(
                subject='Your Verification Code',
                message=f'Your verification code is {code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["elicadewoo1215@gmail.com"],
                fail_silently=False,
            )

            # Temporarily store user ID
            request.session['pre_2fa_user_id'] = user.id
            return redirect('accounts.verify_code')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})

    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save(commit=False)  # Save without committing
            user.email = form.cleaned_data.get('email')  # Explicitly set the email
            user.save()  # Now save the user with the email
            return redirect('home.index')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

def verify_code(request):
    template_data = {'title': 'Verify Code'}

    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('accounts.login')

    if request.method == 'GET':
        return render(request, 'accounts/two_factor.html', {'template_data': template_data})

    elif request.method == 'POST':
        code_entered = request.POST.get('code')
        print("Session user_id:", user_id)
        print("Code entered:", code_entered)
        try:
            user = User.objects.get(id=user_id)
            latest_code = EmailVerificationCode.objects.filter(user=user).latest('created_at')
            print("Actual code:", latest_code.code)
            print("Code expired?", latest_code.is_expired())
            if latest_code.code == code_entered and not latest_code.is_expired():
                auth_login(request, user)
                del request.session['pre_2fa_user_id']  # cleanup
                return redirect('home.index')
            else:
                template_data['error'] = 'Invalid or expired code.'
        except Exception as e:
            print("Error:", e)
            template_data['error'] = 'Invalid verification attempt.'

        return render(request, 'accounts/two_factor.html', {'template_data': template_data})
    
class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'accounts/password_reset_form.html'
