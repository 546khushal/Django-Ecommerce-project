from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator, generate_token
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout

# Create your views here.
def sign(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        c_password = request.POST.get('pass2')

        if password != c_password:
            messages.warning(request, "Passwords do not match.")
            return redirect('/accounts/sign/')  # Correct redirect to the sign page

        try:
            # Check if the user already exists
            if User.objects.filter(username=email).exists():
                messages.info(request, "Email already exists.")
                return redirect('/accounts/sign/')  # Correct redirect to the sign page
                
        except Exception as identifier:
            pass

        # Create the new user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False
        user.save()

        email_subject = "Activate Your Account"
        message = render_to_string('accounts/activate.html', {
            'user': user,
            'domain': 'http://127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })

        email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
        email_message.send()

        messages.success(request, "Please activate your account via the email sent to you.")
        return redirect('/accounts/login/')  # Correct redirect to the login page

    return render(request, 'accounts/sign.html')

class ActivateAccountView(View):
    def get(self,request,uid64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uid64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activate Successfully")
            return redirect('/accounts/login/')
        return render( request,'accounts/activatefail.html')
    


def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get('email')
        userpassword = request.POST.get('pass1')
        user_obj = User.objects.filter(username=username).first()

        if not user_obj:
            messages.warning(request, "Email Not Found!")
            return redirect('/accounts/login')


        # Authenticate the user
        myuser = authenticate(username=username, password=userpassword)

        if myuser is not None:
                login(request, myuser)
                messages.success(request, "Login Successfully")
                return redirect('/')  # Redirect to the index page

        else:
            messages.warning(request, "Invalid Credentials")
            return redirect('/accounts/login')
        
    return render(request, 'accounts/login.html')





def handlelogout(request):
    logout(request)
    messages.info(request, "Account Logout! Login again")
    return redirect('/accounts/login')

def cart(request):
    return redirect('/')
