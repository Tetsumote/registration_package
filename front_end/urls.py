from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls import url


from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="home.html"),name='home'),
    path('profileList/', TemplateView.as_view(template_name="profile.html"), name="profile_list"),
]
