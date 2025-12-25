"""
URL configuration for djangify_demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from demo import views
from django.contrib import admin
from django.conf.urls.static import static

from djangify_demo import settings

urlpatterns = [
    path('', views.index,name='index'),
    path('about.html/', views.about,name='about'),
    path('contact.html/', views.contact,name='contact'),
    path('createprof.html/', views.createprof,name='createprof'),
    path('editprofile.html/', views.editprofile,name='editprofile'),
    path('explore.html/', views.explore,name='explore'),
    path('inquiry.html/', views.inquiry,name='inquiry'),
    path('new.html/', views.new,name='new'),
    path('otp.html/', views.otp,name='otp'),
    path('test.html/', views.test,name='test'),
    path('trending.html/', views.trending,name='trending'),
    path('signup.html/', views.signup,name='signup'),
    path('choose.html/', views.choose,name='choose'),
    path('builderfeed.html/', views.builderfeed,name='builderfeed'),
    path('architectfeed.html/', views.architectfeed,name='architectfeed'),
    path('bathwarefeed.html/', views.bathwarefeed,name='bathwarefeed'),
    path('interiorfeed.html/', views.interiorfeed,name='interiorfeed'),
    path('furniturefeed.html/', views.furniturefeed,name='furniturefeed'),
    path('electricfeed.html/', views.electricfeed,name='electricfeed'),
    path('gardenfeed.html/', views.gardenfeed,name='gardenfeed'),
    path('fabricationsfeed.html/', views.fabricationsfeed,name='fabricationsfeed'),
    path('othersfeed.html/', views.othersfeed,name='othersfeed'),
    path('companyprofile.html/', views.companyprofile,name='companyprofile'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('edit_account.html/', views.edit_account, name='edit_account'),
    path('rate_profile/<int:pk>/', views.rate_profile, name='rate_profile'),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
  # Adjust the URL and view function as needed

    # path('accounts/', include('accounts.urls'))

]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)