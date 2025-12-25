from django.core.exceptions import ValidationError
from django.db import models

SERVICE_TYPE_CHOICES = [
    ('Builders', 'Builders'),
    ('Interior Designers', 'Interior Designers'),
    ('Architects', 'Architects'),
    ('Electric Solutions', 'Electric Solutions'),
    ('Bathware Suppliers', 'Bathware Suppliers'),
    ('Furniture Retailers', 'Furniture Retailers'),
    ('Garden Solutions', 'Garden Solutions'),
    ('Fabrications', 'Fabrications'),
    ('Others', 'Others'),
]

class User(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact = models.IntegerField()
    email = models.EmailField()
    city = models.CharField(max_length=50)
    create_password = models.CharField(max_length=50)
    confirm_password = models.CharField(max_length=50)
    user_type = models.CharField(max_length=20, choices=[('user', 'User'), ('service_provider', 'Service Provider')])

class UserProfile(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, unique=True)
    office_address = models.CharField(max_length=200)
    office_number = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=20)
    pan_number = models.CharField(max_length=20)
    service_type = models.CharField(max_length=100, choices=SERVICE_TYPE_CHOICES)
    company_description = models.TextField()
    # optional logo for the company/profile
    logo = models.ImageField(upload_to="Img/logo", blank=True, null=True)

    def __str__(self):
        return self.company_name
    

    # photo =models.ImageField()
class Product(models.Model):
    title = models.CharField(max_length=70)
    banner = models.ImageField(upload_to="Img/banner")
    
    def _str_(self):
        return self.title
    

class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    images = models.ImageField(upload_to="Img/images")


class ProfileImage(models.Model):
    """Images/photos uploaded for a UserProfile (service provider)."""
    profile = models.ForeignKey(UserProfile, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Img/profile')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.profile.company_name}"


class Rating(models.Model):
    """Star ratings provided by regular users for a UserProfile.

    Each (profile, user) pair is unique so a user can rate a profile once and update their rating.
    """
    profile = models.ForeignKey(UserProfile, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # expected 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('profile', 'user')

    def clean(self):
        """Ensure a user cannot rate their own profile."""
        if self.profile and self.user and self.profile.user_id == self.user_id:
            raise ValidationError("You cannot rate your own profile.")
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")

    def save(self, *args, **kwargs):
        # Run full validation before saving (defensive: prevents bypassing view checks)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} -> {self.profile.company_name}: {self.rating}★"