from django.contrib.auth import login
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import BadHeaderError, send_mail

from django.contrib.auth.models import User

from .forms import SignUpForm
from .tokens import account_activation_token

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
DEFAULT_ACTIVATION_REDIRECT = settings.DEFAULT_ACTIVATION_REDIRECT

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            userObj = form.cleaned_data
            username = userObj['username']
            email = userObj['email']
            if not (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):

                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                subject = 'Activate Your MySite Account'
                recipients = [user.email]
                sender = DEFAULT_FROM_EMAIL     

                html_message = render_to_string('account_activation_email.html',{
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                plain_message = strip_tags(html_message)


                send_mail(subject,plain_message,sender,recipients,html_message=html_message)


                return redirect('account_activation_sent')           
            else:
                validationMsg = 'You have account in our site with this email use login page to log in or reset password.'
                form = SignUpForm()
                return render(request,'registration/signup.html',{'form':form,'validationMsg':validationMsg})

    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect(DEFAULT_ACTIVATION_REDIRECT)
    else:
        return render(request, 'account_activation_invalid.html')

