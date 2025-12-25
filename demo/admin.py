from django.contrib import admin
from .models import User, UserProfile, ProfileImage, Product, Images, Rating


admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(ProfileImage)
admin.site.register(Product)
admin.site.register(Images)
admin.site.register(Rating)
