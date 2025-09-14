from django.urls import path
from . import views

urlpatterns = [
    path('Login',views.login, name="Login"),
    path('Logout',views.logout_view, name="logout"),
    path('Signup',views.signup, name="Signup"),
    path('upload',views.single_upload, name="single_upload"),
    path('profile',views.profile, name="profile"),
    path('edit',views.edit, name="edit"),
  path('Voice', views.Voicetype, name='voice_type'),
    path('files', views.file_list, name='file_list'),
    path('sendotp', views.send_otp, name='sendotp'),
    path('verify', views.sigin_verification, name='verify'),
    path('verifyotp', views.verify_otp, name='verifyotp'),
    path('resetpassword', views.reset_password, name='resetpassword'),
     path('deleteprofile', views.delete_profile, name='delete_profile'),
     path('search', views.search, name='search'),
     path('addfavorite', views.add_favorite, name='add_favorite'),
     path('favorite', views.favorite, name='favorite'),
    path('privacy-policy',views.privacy,name='privacy'),
]

