from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
#from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt

from cryptography.fernet import Fernet
import requests
import pymongo
#import pyrebase
import json

from .models import Lock, OTP, PreRegistration, ShareHistory, API, History

from django.contrib.auth import logout, login, authenticate



import math, random
def OTPgenerator():
    """Generates a random 4 digit OTP"""
    digits = '123456789'
    OTP = ''
    for i in range(4):
        OTP += digits[ math.floor(random.random() * 10) ]
    return OTP



def index(request):
    """Very Complex view, handles various tasks:
    1. Handles the Ajax reqeusts(POST) from index.html file.
    2. Fetches lock status from the database and displays it in index.html file.
    """
    #key = b'yGdG7zJ1XNB5BpHnlPDH3cBXSvWbcEw2AEjSg90XGQg='
    if request.user.is_authenticated:
        if request.is_ajax():
            if request.method == "POST":
                code = OTPgenerator()
                #cipher_suit = Fernet(key)
                #code = code.encode('utf-8')
                #cipher_text = cipher_suit.encrypt(code)
                #cipher_text = cipher_text.decode('utf-8')
                otp = OTP(
                    content=code,  
                    source=request.user,
                )
                otp.save()
                lock = Lock.objects.get(id=1)
                #lock.otp = cipher_text
                lock.otp = code
                lock.save()
                #code = code.decode("utf-8")
                #
                # Encript OTP here
                #
                return JsonResponse({'otp':code, 'time': otp.time, 'source':otp.source.username})
            else:
                return HttpResponse('Better luck nex time :-))')
        lock = Lock.objects.get(id=1)
        status = True
        if lock.status=="Locked":
            status = False
        elif lock.status=="Open" or lock.status=="Unlocked":
            status = True
        else:
            return render(request, "share_success.html", { 'msg':'Unable to fetch lock status, sorry for the inconvenience caused.' })
            #return HttpResponse('Lock status neither Locked nor Opened')
        return render(request, 'index.html', {'status':status})
    else:
        return redirect('login')



def user_pre_register(request):
    """Accepts an email through a POST request, generates a link for registration of the user and sends a email to the user to register thrgough the link."""
    if request.method == "POST":
        key1 = b'qbtG9yFj_qt_TBGIuMsZ5_WeZ4s-glu6IuwpNSA9wGw='
        emailaddress = request.POST['email']
        print(emailaddress)
        cipher_suit = Fernet(key1)
        emad = emailaddress.encode('utf-8')
        token = cipher_suit.encrypt(emad)
        token = token.decode("utf-8")
        link = "http://kyukey.ap-south-1.elasticbeanstalk.com/register/" + str(token)
        print(link)
        send_mail('KyuKey', link, "kyukey2020@gmail.com", [emailaddress,])
        email = PreRegistration(
            email=emailaddress,
            registered=False,
        )
        email.save()
        ### Mail sending with the registration link
        return render(request, 'share_success.html', { 'msg':'Email successfully sent.' })
        return HttpResponse('check-email for mail')
    else:
        return render(request, 'pre_register.html')

def user_register(request, id):
    """A complex view, handles various tasks:
    1. Displays a registration form by verifing the link through which the view is accessed.
    2. Registers a new user.
    """
    key1 = b'qbtG9yFj_qt_TBGIuMsZ5_WeZ4s-glu6IuwpNSA9wGw='
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        email = request.POST['email']
        if len(password) > 6:
            if password != password2:
                msg = "Entered Passwords do not match"
                return render(request, 'register.html', { 'msg': msg, 'email':email })
            else:
                try:
                    emails = PreRegistration.objects.filter(registered__exact=False)
                    for item in emails:
                        if email==item.email:
                            user = User.objects.create_user(username, email, password)
                            user.save()
                            item.registered = True
                            item.save()
                            user_auth = authenticate(request, username=username, password=password)
                            if user is not None:
                                login(request, user_auth)
                                return redirect('index')
                            else:
                                return HttpResponse('Unable to Signup, try again')
                except:
                    msg="Username already exists"
                    return render(request, 'register.html', { 'msg': msg, 'email':email })
        else:
            msg="Password length should be more than 6 digits"
            return render(request, 'register.html', { 'msg': msg, 'email':email })
    else: 
        try:
            id = id.encode("utf-8")
            cipher_suit = Fernet(key1)
            emailaddress = cipher_suit.decrypt(id)
            emailaddress = emailaddress.decode("utf-8")
            print(emailaddress)
            emails = PreRegistration.objects.filter(registered__exact=False)
            for item in emails:
                print(item.email, emailaddress)
                if item.email == emailaddress:
                    return render(request, 'register.html', { 'msg':"", 'email': item.email })
            else:
                return HttpResponse('Bad request (Either already registered or bad link)')
        except:
            return HttpResponse('Bad request, use the link proviced in the email to register.')

def user_login(request):
    """User login view."""
    if request.user.is_authenticated :
        return redirect('index')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', { 'msg': "Invalid Credentials" })
    else:
        return render(request, 'login.html')

def user_logout(request):
    """User Logout view"""
    logout(request)
    return redirect('index')


def share_sms(request, otp):
    """Used to send a SMS to share the generated OTP"""
    if request.method == "POST":
        number = request.POST['number']
        otp = request.POST['otp']

        url = "https://www.fast2sms.com/dev/bulk"

        querystring = {"authorization":"5hmO7ZbzyBnWwxgTCNGVcHvQa9DfequjK6LptkdSU2JrYi8RlsHh8DdCnkFUyA3wcSmxZMziEQgqNL9s",
                        "sender_id":"FSTSMS",
                        "language":"english",
                        "route":"qt",
                        "numbers":number,
                        "message":"21805",
                        "variables":"{BB}",
                        "variables_values":otp}

        headers = {
            'cache-control': "no-cache"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        history = ShareHistory(
            category="SMS",
            source=request.user.username,
            destination=number
        )
        history.save()
        return render(request, 'share_success.html', { 'msg':"SMS successfully sent." })
    else:
        return render(request, 'share_sms.html', {'otp': otp} )

def share_email(request, otp):
    """Used to send Email to share the generated OTP"""
    if request.method == "POST":
        email = request.POST['email']
        otp = request.POST['otp']
        content = "OTP for the lock is: "+ otp
        send_mail('KyuKey', content, "kyukey2020@gmail.com", [email,])
        history = ShareHistory(
            category="Email",
            source=request.user.username,
            destination=email
        )
        history.save()
        return render(request, "share_success.html", {'msg': "Email Successfully sent."})
    else:
        return render(request, 'share_email.html', {'otp': otp})


def lock_history(request):
    """Fetches lock history and displays it in history.html"""
    client = pymongo.MongoClient("mongodb+srv://subodhk:iitbhu@kyukey-fnmki.mongodb.net/test?retryWrites=true&w=majority")
    db = client["KyuKey"]
    col = db["lock_history"]
    pre_history = col.find({})
    he = 0
    for x in pre_history:
        he += 1
        print(x)
    print(he)
    pre_history = col.find({})
    return render(request, 'history.html', { 'history':pre_history, 'count':he })


################## APIs
def ld():
    lock = Lock.objects.get(id=1)
    #lock.otp = cipher_text
    lock.status = "Locked"
    lock.save()
    history = History(
        state = "Locked"
    )
    history.save()
    return str(lock.otp)

def sb():
    lock = Lock.objects.get(id=1)
    lock.status = "Unlocked"
    lock.save()
    history = History(
        state = "Unlocked"
    )
    history.save()
    return "success sb"

def lda():
    lock = Lock.objects.get(id=1)
    lock.status = "Locked"
    lock.save()
    history = History(
        state = "Locked"
    )
    history.save()
    return "success lda"


@csrf_exempt
def api_test(request):
    data = request.body
    data = data.decode("utf-8")
    if data=="ld":
        return HttpResponse(ld())
    elif data=="sb":
        return HttpResponse(sb())
    elif data=="lda":
        return HttpResponse(lda())
    return HttpResponse(data)
