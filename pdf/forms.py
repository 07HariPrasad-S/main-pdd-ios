from django import forms
from .models import PDFFile
from django.contrib.auth.models import User
from .models import Profile, Favorite

class Registrationform(forms.ModelForm):
    first_name=forms.CharField(label="first_name",max_length=225, required=True)
    last_name=forms.CharField(label="last_name",max_length=225, required=True)
    username=forms.CharField(label='username' ,max_length=112 ,required=True)
    email=forms.EmailField(label='email' ,required=True)
    password=forms.CharField(label='password' ,max_length=112, required=True)

    class Meta:
        model=User
        fields=['first_name','last_name','username','email','password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                name=self.cleaned_data['first_name'] + ' ' + self.cleaned_data['last_name'],
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                passwords=self.cleaned_data['password'],
                mobile_phone="xxxx",  # You can modify this to accept mobile phone from the form if needed
                POSITION="xxxx"  # Default value, modify as needed
            )

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFFile
        fields = ['pdf_file']
    
    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf and not pdf.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        return pdf
    def save(self, commit=True):
        pdf = super().save(commit=False)
        pdf.title = pdf.pdf_file.name
        if commit:
            pdf.save()
        return pdf
class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = ['mp3file']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'name', 'username', 'mobile_phone', 'email', 'POSITION']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number','pattern':'[0-9]{10}'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'POSITION': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your position'}),
        }
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update the related User model
        user = profile.user  # Assuming Profile has a OneToOneField to User
        
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['name']  # Saving name as first_name in User model
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()  # Save User model first
            profile.save()  # Save Profile model
        
        return profile