from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, Http404
from .forms import Registrationform
from django.contrib.auth import authenticate,login as auth,logout
from django.urls import reverse_lazy
from django.core.serializers import serialize
from django.http import JsonResponse
from celery.result import AsyncResult

from django.contrib.auth.models import User
import os

from .models import PDFFile, Profile
from .forms import PDFUploadForm,FavoriteForm,ProfileUpdateForm
from django.core.exceptions import ObjectDoesNotExist
from .models import PDFFile,Profile,MP3File,Favorite

import random
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password


from django.contrib import messages
from django.utils.timezone import now

# Create your views here.

def login(request):
    if(request.POST):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth(request,user)
            profile=list(Profile.objects.filter(user=user).values('id', 'username','passwords'))
            return JsonResponse({"Status": True, "message": "Login successfully", "data": profile})
    return JsonResponse({"Status":False,"message":"Login failed","data":[]})

def signup(request):
    form=Registrationform()
    if(request.method=="POST"):
        form=Registrationform(request.POST)
        print(form.is_valid())
        if(form.is_valid()):
            #return redirect(reverse_lazy(""))
            print(form.cleaned_data['email'])
            otp = random.randint(1000, 9999)

            # Send OTP via email
            #send_mail(
             #      'Your OTP Code',
             
              #    f'Your OTP code is: {otp}',
               #   'your_email@gmail.com',  # Sender's email (matches EMAIL_HOST_USER in settings.py)
            
                #   [form.cleaned_data['email']],       # Receiver's email
                 #   fail_silently=False,
                #)
            print(form.cleaned_data)
            print("OTP:", otp)
            request.session['form_data'] = form.cleaned_data
            # Save the OTP to session or database for verification
            request.session['otp'] = otp
            return JsonResponse({"Status":True,"message":" Send otp for authentication","data":[{"otp":otp}]})
    else:
        print(form.errors) 
    return JsonResponse({"Status":"False","message":"failed to signup","data":[]})  
from django.http import JsonResponse
from .forms import Registrationform

def sigin_verification(request):
    if request.method == "POST":
        # Collect OTP parts
        print("Request POST data:", request.POST)
        otp = request.POST.get("otp", "")

        # Combine the OTP parts
        entered_otp = otp
        saved_otp = request.session.get('otp')

        print("Entered OTP:", entered_otp, "\nSaved OTP:", saved_otp)

        if str(entered_otp) == str(saved_otp):
            print("OTP verified successfully!")
            form_data = request.session.get('form_data')
            print("Form Data:", form_data)
            if form_data:
                form = Registrationform(form_data)
                if form.is_valid():
                    form.save()  # Save the form data to the database
                    profile=list(Profile.objects.filter(user=User.objects.get(username=form_data['username'])).values('id', 'username','passwords'))
                    # Clear the session data
                    del request.session['form_data']
                    del request.session['otp']
                    return JsonResponse({"Status": True, "message": "Recorded successfully", "data": [profile]})
                else:
                    return JsonResponse({"Status": False, "message": "Form data is invalid", "errors": [form.errors]})
            else:
                return JsonResponse({"Status": False, "message": "No form data found in session"})
        else:
            print("Invalid OTP")
            return JsonResponse({"Status": False, "message": "Invalid OTP"})
    else:
        return JsonResponse({"Status": False, "message": "Only POST requests are allowed"})


def single_upload(request):
    id = request.POST.get('id', '')
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.save(commit=False)
            profile = Profile.objects.get(id=id)
            pdf_file.user = profile
            pdf_file.title = pdf_file.pdf_file.name
            pdf_file.save()
            print("pdf_file:",pdf_file.title)
            return JsonResponse({"Status":True,"message":"sucessfully uploaded in db","data":[{"id":pdf_file.id,'title':pdf_file.title,'date':pdf_file.date}]})
        else:
            # Handle form errors
            print(request.POST,"\n",request.FILES)
            return JsonResponse({"Status":False,"message":"failed to upload in db","data":[]})



def logout_view(request):
    username = str(request.user)
    if request.method=="POST":
        logout(request)
        return JsonResponse({"Status": True, "message": "Logout Sucessfully","data":username})
    return JsonResponse({"Status": False, "message": "Logout failed","data":[]})



def send_otp(request):
    if request.method == "POST":
        # Get the receiver's email from the form input or user model
        receiver_email = request.POST.get('email')  # Example: from an input field named 'email'
            
        try:
            users = User.objects.filter(email=receiver_email)
            print(users)
            otp = random.randint(1000, 9999)

            #Send OTP via email
            #send_mail(
             #      'Your OTP Code',
              #     f'Your OTP code is: {otp}',
               #    'your_email@gmail.com',  # Sender's email (matches EMAIL_HOST_USER in settings.py)
                #   [receiver_email],       # Receiver's email
                 #   fail_silently=False,
                #)

            # Save the OTP to session or database for verification
            request.session['otp'] = otp
            request.session['receiver_email'] = receiver_email
            print(f"OTP: {otp}")
            return JsonResponse({"Status": True, "message": "email sent Sucessfully","data":{" your OTP":otp}})
        except User.DoesNotExist:
            return JsonResponse({"Status": True, "message": "email sent Failed","data":[]})
    return JsonResponse({"Status": False, "message": "email sent Failed","data":[]})


from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Profile

def delete_profile(request):
    id = request.POST.get('id', '')
    try:
        # Fetch the profile and related user instance
        profile = Profile.objects.get(id=id)
        user = profile.user
        
        # Delete the profile and the user account
        profile.delete()
        user.delete()
        
        return JsonResponse({"Status": True, "message": "Profile deleted successfully.","data":[{"username":profile.username,"password":profile.passwords}]})
    except Profile.DoesNotExist:
        return JsonResponse({"Status": False, "message": "Profile does not exist."})
    except Exception as e:
        return JsonResponse({"Status": False, "message": f"An error occurred: {str(e)}"})



def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp", "")
        
        # Combine the OTP parts
        entered_otp = otp
        saved_otp = request.session.get('otp')
        receiver_email = request.session.get('receiver_email')
        if str(entered_otp) == str(saved_otp):
            # OTP matches
            return JsonResponse({"Status": True, "message": "verify SUCESSFULLY","data":" redirect to reset password"})
        else:
            # OTP does not match
            return JsonResponse({"Status": False, "message": "verify Failed","data":"INVALID OTP"})

    return JsonResponse({"Status": False, "message": "verify Failed","data":"INVALID OTP"})

import json
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib import messages
from django.core.serializers import serialize
import json
from .models import User, Profile  # Ensure you import your models

def reset_password(request):
    if request.method == 'POST':
        print("POST request received")
        receiver_email = request.session.get('receiver_email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        print(f"Receiver Email: {receiver_email}")
        print(f"New Password: {new_password}")
        print(f"Confirm Password: {confirm_password}")

        # Validate email
        try:
            user = User.objects.filter(email=receiver_email).first()  # FIXED
            if not user:
                raise User.DoesNotExist

            profile = Profile.objects.filter(user=user).first()  # FIXED
            if not profile:
                return JsonResponse({"Status": False, "message": "User profile not found", "data": []})

            # Check if passwords match
            if new_password != confirm_password:
                print("Passwords do not match.")
                messages.error(request, "Passwords do not match.")
                return JsonResponse({"Status": False, "message": "Passwords do not match.", "data": []})

            # Update the user's password
            profile.passwords = new_password  # Assuming passwords field exists
            profile.save()
            user.password = make_password(new_password)  # Hash the password
            user.save()

            # Serialize profile data
            profile_data = json.loads(serialize("json", [profile]))[0]["fields"]
            print("Password updated successfully.")
            messages.success(request, "Password updated successfully.")
            return JsonResponse({"Status": True, "message": "Password updated successfully.", "data": profile_data})

        except User.DoesNotExist:
            print("No user found with this email.")
            messages.error(request, "No user found with this email.")
            return JsonResponse({"Status": False, "message": "No user found with this email", "data": []})





from django.forms.models import model_to_dict
from django.http import JsonResponse
# hari check
def file_list(request):
    id = request.POST.get('id', '')
    profile = Profile.objects.get(id=id)
    # Convert QuerySets to lists of dictionaries
    pdf_files = list(PDFFile.objects.filter(user=profile).values('id','user_id', 'title', 'pdf_file', 'date'))
    mp3_files = list(MP3File.objects.filter(user=profile).values('id', 'user_id','title', 'mp3_file', 'date'))

    return JsonResponse({
        "Status": True,
        "message": "Files retrieved successfully.",
        "data": [
            {"PDF Files": pdf_files},
            {"MP3 Files": mp3_files},
        ]
    })


 # hari check 
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from celery.result import AsyncResult
import time

from .models import Profile, PDFFile
from .tasks import convert_pdf_to_mp3_task

def Voicetype(request):
    id = request.POST.get('id', '')
    pdf_id = request.POST.get('pdf_id', '')
    profile = Profile.objects.get(id=id)
    pdf_file = get_object_or_404(PDFFile, id=pdf_id, user=profile)

    if request.method == 'POST':
        voice = request.POST.get("voiceType")
        pdf_path = pdf_file.pdf_file.path  # Get the absolute path to the file
        title = pdf_file.title.replace(".pdf", "")  # Assuming PDFFile has a title field
        
        try:
            voice_type = 'en-US-JennyNeural' if voice == "Female" else 'en-US-GuyNeural'
            
            # Start Celery task
            task = convert_pdf_to_mp3_task.delay(voice_type, pdf_path, title, profile.id)
            request.session['task_id'] = task.id  # Store task ID in session
            
            # Wait for the task to complete (polling mechanism)
            max_wait_time = 150  # Maximum wait time in seconds
            wait_interval = 3  # Time interval between each status check
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                task_result = AsyncResult(task.id)
                if task_result.ready():  # Check if task is completed
                    if task_result.successful():
                        return JsonResponse({
                            "Status": True,
                            "message": "Conversion completed successfully!",
                            "data": [{"selected_voice": voice}], # Assuming task returns MP3 file path
                        })
                    else:
                        return JsonResponse({
                            "Status": False,
                            "message": "Conversion failed.",
                            "error": str(task_result.result),
                            "task_id": task.id
                        })

                time.sleep(wait_interval)  # Wait before next check
                elapsed_time += wait_interval

            return JsonResponse({
                "Status": False,
                "message": "Conversion is taking too long. Please check later.",
                "task_id": task.id
            })

        except Exception as e:
            print("Error:", e)
            return JsonResponse({
                "Status": False,
                "message": "Conversion is taking too long. Please check later.",
                "task_id": task.id
            })


from django.http import JsonResponse


def profile(request):
    id = request.POST.get('id', '')
    users=Profile.objects.get(id=id)
    return JsonResponse({"Status":True,"message":"sucessfully uploaded in db","data":[{"id":users.id,'name':users.name,'username':users.username,'mobile_phone':users.mobile_phone,'email':users.email,'POSITION':users.POSITION}]})

def edit(request):
    id = request.POST.get('id', '')
    profile=Profile.objects.get(id=id)
    if request.method == 'POST':
        form=ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return JsonResponse({"Status":True,"message":"sucessfully uploaded in db","data":[{"id":profile.id,'name':profile.name,'username':profile.username,'mobile_phone':profile.mobile_phone,'email':profile.email,'POSITION':profile.POSITION}]})
        return JsonResponse({"Status":False,"message":"your have missing data fields","data":[]})
    return JsonResponse({"Status":False,"message":"failed to updated","data":[]})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def search(request):
    id = request.POST.get('id', '')
    query = request.POST.get('query', '')
    
    try:
        # Get the profile
        profile = get_object_or_404(Profile, id=id)
        
        # Filter PDFs and MP3s using the corrected `icontains` lookup
        pdffile = list(profile.pdfs.filter(title__icontains=query).values('id', 'pdf_file', 'title', 'date'))
        mp3file = list(profile.mp3s.filter(title__icontains=query).values('id', 'mp3_file', 'title', 'date'))
        
        return JsonResponse({
            "Status": True,
            "message": "Search completed successfully.",
            "data": [{"PDF FILES": pdffile, "MP3 FILES": mp3file}]
        })
    except Profile.DoesNotExist:
        return JsonResponse({"Status": False, "message": "Profile not found."})
    except Exception as e:
        return JsonResponse({"Status": False, "message": f"An error occurred: {str(e)}"})

def add_favorite(request):
    id = request.POST.get('id', '')
    mp3_id = request.POST.get('mp3_id', '')
    profile = Profile.objects.get(id=id)
    mp3 = MP3File.objects.get( id=mp3_id)
    Favorite.objects.create(user=profile, mp3file=mp3)
    mp3 = list(MP3File.objects.filter( id=mp3_id).values('id', 'mp3_file', 'title', 'date'))
    return JsonResponse({
            "Status": True,
            "message": "favorite added successfully.",
            "data": [{ "MP3 FILES": mp3}]
        })

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Profile, Favorite

def favorite(request):
    id = request.POST.get('id', '')
    profile = get_object_or_404(Profile, id=id)

    # Retrieve all Favorite objects for this user, including MP3 file details
    fav_mp3_files = Favorite.objects.filter(user=profile).select_related('mp3file')

    # Format the response data
    data = [
        {
            "id": fav.id,
            "title": fav.mp3file.title,
            "file_url": fav.mp3file.mp3_file.url if fav.mp3file.mp3_file else None,
            "date_added": fav.mp3file.date.strftime('%Y-%m-%d %H:%M:%S')
        }
        for fav in fav_mp3_files
    ]

    return JsonResponse({
        "status": True,
        "message": "Favorites retrieved successfully.",
        "data": data
    })
