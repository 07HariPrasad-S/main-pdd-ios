from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    name=models.CharField(max_length=225)
    username=models.CharField(max_length=225)
    passwords=models.CharField(max_length=225)
    mobile_phone=models.CharField(max_length=225,default="xxxx")
    email=models.EmailField(max_length=225,default="xxxx")
    POSITION = models.CharField(max_length=100,default="xxxx")

    def _str_(self):
        return self.user.username
 
class PDFFile(models.Model):
    pdf_file = models.FileField(upload_to='pdfs')
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="pdfs")
    def _str_(self):
        return self.title
    
class MP3File(models.Model):
    mp3_file = models.FileField(upload_to='mp3s')
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="mp3s")
    def _str_(self):
        return self.title
    
class Favorite(models.Model):
    mp3file = models.ForeignKey(MP3File, on_delete=models.CASCADE, related_name="favorites")
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="favorites")

    def __str__(self):
        return f"{self.user.user.username} - {self.mp3file.title}"
