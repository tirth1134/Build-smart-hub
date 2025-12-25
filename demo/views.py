from django.shortcuts import render,redirect
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User, UserProfile, ProfileImage, SERVICE_TYPE_CHOICES
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q


def _render_service_feed(request, service_label, heading, background_image):
    """Render a category feed page with profiles filtered by service type.

    Supports GET parameters:
      - q: text search (company_name, company_description, user.city)
      - city: exact city filter
      - min_rating: minimum average rating (1-5)
      - page: page number for pagination
      - per_page: items per page
    """
    qs = UserProfile.objects.filter(service_type__iexact=service_label).select_related('user')
    # annotate averages and counts for filtering and display
    qs = qs.annotate(avg_rating=Avg('ratings__rating'), rating_count=Count('ratings'))

    # filters from query params
    q = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()

    if q:
        qs = qs.filter(Q(company_name__icontains=q) | Q(company_description__icontains=q) | Q(user__city__icontains=q))
    if city:
        qs = qs.filter(user__city__iexact=city)
    if min_rating:
        try:
            mr = float(min_rating)
            qs = qs.filter(avg_rating__gte=mr)
        except ValueError:
            pass

    # ordering: show higher rated first, then by company name
    qs = qs.order_by('-avg_rating', 'company_name')

    # pagination
    try:
        per_page = int(request.GET.get('per_page', 9))
    except (TypeError, ValueError):
        per_page = 9
    paginator = Paginator(qs, per_page)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    # for city filter dropdown
    cities = UserProfile.objects.filter(service_type__iexact=service_label).values_list('user__city', flat=True).distinct()

    context = {
        'profiles': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'page_heading': heading,
        'background_image': background_image,
        'query': q,
        'selected_city': city,
        'cities': [c for c in cities if c],
        'min_rating': min_rating,
    }
    return render(request, 'demo/Modified_files/service_feed.html', context)

def inquiry(request):
    response = ""
    if request.method == 'POST':
        message = request.POST.get('message')
        # Your logic to analyze the message and determine the response
        if message.lower() == 'hello':
            response = "Hi there! How can I assist you today?"
        else:
            response = "Thank you for your message. We will get back to you shortly."
    return render(request, 'demo/Modified_files/inquiry.html', {'response': response})
    
def builderfeed(request):
    return _render_service_feed(request, 'Builders', 'Builder Feed', 'assets/images/builder-feed.jpg')

def architectfeed(request):
    return _render_service_feed(request, 'Architects', 'Architect Feed', 'assets/images/architect-feed.jpg')

def bathwarefeed(request):
    return _render_service_feed(request, 'Bathware Suppliers', 'Bathware Feed', 'assets/images/bath-feed.jpg')

def interiorfeed(request):
    return _render_service_feed(request, 'Interior Designers', 'Interior Designer Feed', 'assets/images/interior-feed.jpg')

def furniturefeed(request):
    return _render_service_feed(request, 'Furniture Retailers', 'Furniture Feed', 'assets/images/furniture-feed.jpg')

def electricfeed(request):
    return _render_service_feed(request, 'Electric Solutions', 'Electric Solutions Feed', 'assets/images/electric-feed.jpg')

def gardenfeed(request):
    return _render_service_feed(request, 'Garden Solutions', 'Garden Solutions Feed', 'assets/images/garden-feed.jpg')

def fabricationsfeed(request):
    return _render_service_feed(request, 'Fabrications', 'Fabrications Feed', 'assets/images/fabrication-feed.jpg')

def othersfeed(request):
    return _render_service_feed(request, 'Others', 'Other Services Feed', 'assets/images/others-feed.jpg')

def index(request):
    return render(request, 'demo/Modified_files/index.html')

def choose(request):
    is_service_provider = request.session.get('is_service_provider', False)
    is_user = request.session.get('is_user', False)
    return render(request, 'demo/Modified_files/choose.html', {'is_service_provider': is_service_provider, 'is_user': is_user})

def about(request):
    return render(request, 'demo/Modified_files/about.html')

def contact(request):       
    return render(request, 'demo/Modified_files/contact.html')

def createprof(request):
    logged_in_username = request.session.get('logged_in_username')
    service_type_choices = SERVICE_TYPE_CHOICES
    valid_service_types = [choice[0] for choice in service_type_choices]

    if request.method == 'POST':
        # Extract form data from POST request
        company_name = request.POST.get('company_name')
        office_address = request.POST.get('office_address')
        office_number = request.POST.get('office_number')
        gst_number = request.POST.get('gst_number')
        pan_number = request.POST.get('pan_number')
        service_type = request.POST.get('service_type')
        company_description = request.POST.get('company_description')
        user_id = request.POST.get('user_id')
        # Create UserProfile object and save to the database
        # handle logo upload (optional)
        logo = request.FILES.get('logo')

        if service_type not in valid_service_types:
            messages.error(request, "Invalid service type selection.")
            context = {
                'user_id': user_id,
                'service_type_choices': service_type_choices,
                'selected_service_type': service_type,
            }
            return render(request, 'demo/Modified_files/createprof.html', context)

        # ensure user exists and is a service provider
        try:
            user_obj = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Invalid user.")
            return redirect('choose')

        if user_obj.user_type != 'service_provider':
            messages.error(request, "Only service providers can create profiles.")
            return redirect('choose')

        # prevent duplicate profile for same user
        if UserProfile.objects.filter(user_id=user_id).exists():
            messages.error(request, "A profile already exists for this user.")
            return redirect('companyprofile')

        user_profile = UserProfile(
            company_name=company_name,
            office_address=office_address,
            office_number=office_number,
            gst_number=gst_number,
            pan_number=pan_number,
            service_type=service_type,
            company_description=company_description,
            user_id=user_id,
            logo=logo,
        )
        user_profile.save()

        # handle uploaded profile photos (optional, allow multiple)
        if request.FILES:
            # form field name expected: photos (multiple files)
            photos = request.FILES.getlist('photos')
            for ph in photos:
                ProfileImage.objects.create(profile=user_profile, image=ph)
        request.session['logged_in_user_id'] = user_id

        # Redirect to a success page or another URL
        return redirect('choose')  # Replace 'success_page' with the URL name of your success page
    else:
        try:
            user = User.objects.get(name=logged_in_username)
            user_id = user.id  # Get the user ID
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('trending')  # Redirect to the login page or handle the error appropriately

        # Pass the user ID to the template context
        context = {
            'user_id': user_id,
            'service_type_choices': service_type_choices,
            'selected_service_type': service_type_choices[0][0] if service_type_choices else '',
        }
        # request.session['logged_in_user_id'] = user_id

        return render(request, 'demo/Modified_files/createprof.html', context)

def editprofile(request):
    logged_in_username = request.session.get('logged_in_username')
    service_type_choices = SERVICE_TYPE_CHOICES
    valid_service_types = [choice[0] for choice in service_type_choices]

    if not logged_in_username:
        messages.error(request, "Please login to edit your profile.")
        return redirect('trending')

    try:
        user = User.objects.get(name=logged_in_username)
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
        return redirect('trending')

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        messages.error(request, "No profile found. Create one first.")
        return redirect('createprof')

    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        office_address = request.POST.get('office_address')
        office_number = request.POST.get('office_number')
        gst_number = request.POST.get('gst_number')
        pan_number = request.POST.get('pan_number')
        service_type = request.POST.get('service_type')
        company_description = request.POST.get('company_description')
        logo = request.FILES.get('logo')

        if service_type not in valid_service_types:
            messages.error(request, "Invalid service type selection.")
            context = {
                'profile': profile,
                'photos': profile.images.all(),
                'service_type_choices': service_type_choices,
                'selected_service_type': service_type,
            }
            return render(request, 'demo/Modified_files/editprofile.html', context)

        profile.company_name = company_name
        profile.office_address = office_address
        profile.office_number = office_number
        profile.gst_number = gst_number
        profile.pan_number = pan_number
        profile.service_type = service_type
        profile.company_description = company_description
        if logo:
            profile.logo = logo
        profile.save()

        delete_photo_ids = request.POST.getlist('delete_photos')
        if delete_photo_ids:
            ProfileImage.objects.filter(profile=profile, id__in=delete_photo_ids).delete()

        new_photos = request.FILES.getlist('photos')
        for ph in new_photos:
            ProfileImage.objects.create(profile=profile, image=ph)

        request.session['logged_in_user_id'] = user.id
        messages.success(request, "Profile updated successfully.")
        return redirect('companyprofile')

    context = {
        'profile': profile,
        'photos': profile.images.all(),
        'service_type_choices': service_type_choices,
        'selected_service_type': profile.service_type,
    }
    return render(request, 'demo/Modified_files/editprofile.html', context)


def edit_account(request):
    """Allow a logged-in user to edit their basic account information."""
    logged_in_username = request.session.get('logged_in_username')

    if not logged_in_username:
        messages.error(request, "Please login to edit your account.")
        return redirect('trending')

    try:
        user = User.objects.get(name=logged_in_username)
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
        return redirect('trending')

    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        city = request.POST.get('city')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate unique username if it changed
        if name and name != user.name and User.objects.filter(name=name).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'demo/Modified_files/edit_account.html', {'user': user})

        # Validate password fields if provided
        if new_password:
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'demo/Modified_files/edit_account.html', {'user': user})
            user.create_password = new_password
            user.confirm_password = confirm_password

        # Update other fields
        if name:
            user.name = name
        if contact:
            try:
                user.contact = int(contact)
            except ValueError:
                messages.error(request, "Contact must be a number.")
                return render(request, 'demo/Modified_files/edit_account.html', {'user': user})
        if email:
            user.email = email
        if city:
            user.city = city

        user.save()
        # update session username if changed
        request.session['logged_in_username'] = user.name
        messages.success(request, "Account updated successfully.")
        return redirect('choose')

    return render(request, 'demo/Modified_files/edit_account.html', {'user': user})
# def createprof(request):
#     logged_in_username = request.session.get('logged_in_username')

#     if request.method == 'POST':
#         # Extract form data from POST request
#         company_name = request.POST.get('company_name')
#         office_address = request.POST.get('office_address')
#         office_number = request.POST.get('office_number')
#         gst_number = request.POST.get('gst_number')
#         pan_number = request.POST.get('pan_number')
#         service_type = request.POST.get('service_type')
#         company_description = request.POST.get('company_description')
#         user_id = request.POST.get('user_id')
        
#         # Create UserProfile object and save to the database
#         user_profile = UserProfile(
#             company_name=company_name,
#             office_address=office_address,
#             office_number=office_number,
#             gst_number=gst_number,
#             pan_number=pan_number,
#             service_type=service_type,
#             company_description=company_description,
#             user_id=user_id,
#         )
#         user_profile.save()
        
#         # Redirect to a success page or another URL
#         return redirect('choose')  # Replace 'success_page' with the URL name of your success page
#     else:
#         try:
#             user = User.objects.get(name=logged_in_username)
#             user_id = user.id  # Get the user ID
#         except User.DoesNotExist:
#             messages.error(request, "User does not exist.")
#             return redirect('trending')  # Redirect to the login page or handle the error appropriately

#         # Pass the user ID to the template context
#         context = {'user_id': user_id}
#         request.session['logged_in_user_id'] = user_id

#         return render(request, 'demo/Modified_files/createprof.html', context)

# def createprof(request):
#     logged_in_username = request.session.get('logged_in_username')

#     if request.method == 'POST':
#         if request.user.is_authenticated and request.user.user_type == 'service_provider':
#             existing_profile = Profile.objects.filter(user=request.user).exists()
#             if existing_profile:
#                 messages.error(request, "You have already created a profile.")
#                 return redirect('choose')  # Adjust the redirect as per your URL configuration
#             else:
#                 user_id = request.POST.get('user_id')  # Retrieve user_id from the form
#                 company_name = request.POST.get('company_name')
#                 office_address = request.POST.get('office_address')
#                 office_number = request.POST.get('office_number')
#                 gst_number = request.POST.get('gst_number')
#                 pan_number = request.POST.get('pan_number')
#                 service_type = request.POST.get('service_type')
#                 company_description = request.POST.get('company_description')
#                 # messages.info("save"),

#                 try:
#                     Profile.objects.create(
#                         user_id=user_id,  # Use the retrieved user_id
#                         company_name=company_name,
#                         office_address=office_address,
#                         office_number=office_number,
#                         gst_number=gst_number,
#                         pan_number=pan_number,
#                         service_type=service_type,
#                         company_description=company_description,
#                     )

#                     messages.success(request, "Profile created successfully.")
#                     return redirect('choose')  # Adjust the redirect as per your URL configuration
#                 except Exception as e:
#                     messages.error(request, f"An error occurred: {str(e)}")
#                     return redirect('choose')  # Adjust the redirect as per your URL configuration
#         else:
#             messages.error(request, "Only service providers can create profiles.")
#             return redirect('choose')  # Adjust the redirect as per your URL configuration
#     else:
#         try:
#             user = User.objects.get(name=logged_in_username)
#             user_id = user.id  # Get the user ID
#         except User.DoesNotExist:
#             messages.error(request, "User does not exist.")
#             return redirect('trending')  # Redirect to the login page or handle the error appropriately

#         # Pass the user ID to the template context
#         context = {'user_id': user_id}
#         return render(request, 'demo/Modified_files/createprof.html', context)
# def createprof(request):
#     logged_in_username = request.session.get('logged_in_username')

#     if request.method == 'POST':
#         if request.user.is_authenticated and request.user.user_type == 'service_provider':
#             existing_profile = Profile.objects.filter(user=request.user).exists()
#             if existing_profile:
#                 messages.error(request, "You have already created a profile.")
#                 return redirect('choose')  # Adjust the redirect as per your URL configuration
#             else:
#                 user_id = request.POST.get('user_id')
#                 company_name = request.POST.get('company_name')
#                 office_address = request.POST.get('office_address')
#                 office_number = request.POST.get('office_number')
#                 gst_number = request.POST.get('gst_number')
#                 pan_number = request.POST.get('pan_number')
#                 service_type = request.POST.get('service_type')
#                 company_description = request.POST.get('company_description')

#                 try:
#                     profile=Profile.objects.create( 
#                         user_id=user_id,
#                         company_name=company_name,
#                         office_address=office_address,
#                         office_number=office_number,
#                         gst_number=gst_number,
#                         pan_number=pan_number,
#                         service_type=service_type,
#                         company_description=company_description,
#                     )
#                     messages.success(request, "Profile created successfully.")
#                     return redirect('companyprofile')  # Adjust the redirect as per your URL configuration
#                 except Exception as e:
#                     messages.error(request, f"An error occurred: {str(e)}")
#                     return redirect('choose')  # Adjust the redirect as per your URL configuration
#         else:
#             messages.error(request, "Only service providers can create profiles.")
#             return redirect('choose')  # Adjust the redirect as per your URL configuration
#     else:
#         try:
#             user = User.objects.get(name=logged_in_username)
#             user_id = user.id  # Get the user ID
#         except User.DoesNotExist:
#             messages.error(request, "User does not exist.")
#             return redirect('trending')  # Redirect to the login page or handle the error appropriately

#     # Pass the user ID to the template context
#     context = {'user_id': user_id}
#     return render(request, 'demo/Modified_files/createprof.html', context)

#     def createprof(request):
#     if request.method == 'POST':
#         if request.user.user_type == 'service_provider':
#             existing_profile = Profile.objects.filter(user=request.user).exists()
#             if existing_profile:
#                 messages.error(request, "You have already created a profile.")
#                 return redirect('choose')
#             else:
#                 # Extract form data from POST request
#                 name = request.POST.get('name')
#                 company_name = request.POST.get('company_name')
#                 office_address = request.POST.get('office_address')
#                 office_number = request.POST.get('office_number')
#                 gst_number = request.POST.get('gst_number')
#                 pan_number = request.POST.get('pan_number')
#                 service_type = request.POST.get('service_type')
#                 company_description = request.POST.get('company_description')

#                 try:
#                     # Create the profile object and save it to the database
#                     profile=Profile.objects.create(
#                         name=name,
#                         company_name=company_name,
#                         user=request.user,
#                         office_address=office_address,
#                         office_number=office_number,
#                         gst_number=gst_number,
#                         pan_number=pan_number,
#                         service_type=service_type,
#                         company_description=company_description,
#                     )
#                     # Redirect to the companyprofile view after successful creation
#                     return redirect('companyprofile')
#                 except Exception as e:
#                     # Handle any exceptions that occur during the save operation
#                     messages.error(request, f"An error occurred: {str(e)}")
#                     return redirect('choose')
#         else:
#             messages.error(request, "Only service providers can create profiles.")
#             return redirect('choose')
#     else:
#         # If it's a GET request, render the createprof.html template
#         return render(request, 'demo/Modified_files/createprof.html')
#     def createprof(request):
#     if request.method == 'POST':
#         company_name = request.POST.get('company_name')
#         office_address = request.POST.get('office_address')
#         office_number = request.POST.get('office_number')
#         gst_number = request.POST.get('gst_number')
#         pan_number = request.POST.get('pan_number')
#         service_type = request.POST.get('service_type')
#         company_description = request.POST.get('company_description')

#         Profile.objects.create(
#             company_name=company_name,
#             office_address=office_address,
#             office_number=office_number,
#             gst_number=gst_number,
#             pan_number=pan_number,
#             service_type=service_type,
#             company_description=company_description,
#         )
        
#         # Retrieve the newly created profile
#         profile = Profile.objects.last()
#         context = {
#             'profile': profile,
#         }
        
#         # Render the profile template with the newly created profile data
#         return render(request, 'demo/Modified_files/companyprofile.html', context)
#     return render(request, 'demo/Modified_files/createprof.html')
# def createprof(request):
#     return render(request, 'demo/Modified_files/createprof.html')

def explore(request):
    return render(request, 'demo/Modified_files/explore.html')

def new(request):
    return render(request, 'demo/Modified_files/new.html')

def otp(request):
    return render(request, 'demo/Modified_files/otp.html')

def test(request):
    return render(request, 'demo/Modified_files/test (1).html')

def companyprofile(request):
    logged_in_user_id = request.session.get('logged_in_user_id')

    if logged_in_user_id is None:
        logged_in_username = request.session.get('logged_in_username')
        if logged_in_username:
            try:
                user = User.objects.get(name=logged_in_username)
                logged_in_user_id = user.id
                request.session['logged_in_user_id'] = logged_in_user_id
            except User.DoesNotExist:
                messages.error(request, "User ID not found.")
                return redirect('choose')
        else:
            messages.error(request, "User ID not found.")
            return redirect('choose')  # Redirect to a different page or handle the error appropriately

    try:
        # try to retrieve the profile for the logged in user
        profile = UserProfile.objects.get(user_id=int(logged_in_user_id))
    except UserProfile.DoesNotExist:
        # Handle the case where the profile doesn't exist for the given user_id
        messages.error(request, "Profile does not exist for the current user.")
        return redirect('choose')  # Redirect to a different page or handle the error appropriately

    photos = profile.images.all()

    # Ratings summary
    from django.db.models import Avg, Count
    rating_agg = profile.ratings.aggregate(avg=Avg('rating'), count=Count('id'))
    avg_rating = rating_agg['avg'] or 0
    rating_count = rating_agg['count'] or 0

    # determine if current logged-in user can rate (regular user and not the owner)
    logged_in_user = None
    logged_in_user_id = request.session.get('logged_in_user_id')
    can_rate = False
    user_rating = None
    if logged_in_user_id:
        try:
            logged_in_user = User.objects.get(id=int(logged_in_user_id))
        except User.DoesNotExist:
            logged_in_user = None

    if logged_in_user and logged_in_user.user_type == 'user' and profile.user.id != logged_in_user.id:
        can_rate = True
        try:
            user_rating_obj = profile.ratings.get(user=logged_in_user)
            user_rating = user_rating_obj.rating
        except Exception:
            user_rating = None

    return render(request, 'demo/Modified_files/companyprofile.html', {
        'profile': profile,
        'photos': photos,
        'is_owner': True,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'can_rate': can_rate,
        'user_rating': user_rating,
    })


def rate_profile(request, pk):
    """Allow a logged-in regular user to create or update a rating for profile with id=pk."""
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('profile_detail', pk=pk)

    logged_in_user_id = request.session.get('logged_in_user_id')
    if not logged_in_user_id:
        messages.error(request, "Please login to rate profiles.")
        return redirect('trending')

    try:
        user = User.objects.get(id=int(logged_in_user_id))
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
        return redirect('trending')

    # Only regular users can rate
    if user.user_type != 'user':
        messages.error(request, "Only regular users can rate profiles.")
        return redirect('profile_detail', pk=pk)

    try:
        profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('choose')

    # prevent owner from rating own profile
    if profile.user.id == user.id:
        messages.error(request, "You cannot rate your own profile.")
        return redirect('profile_detail', pk=pk)

    try:
        rating_val = int(request.POST.get('rating'))
    except (TypeError, ValueError):
        messages.error(request, "Invalid rating value.")
        return redirect('profile_detail', pk=pk)

    if rating_val < 1 or rating_val > 5:
        messages.error(request, "Rating must be between 1 and 5.")
        return redirect('profile_detail', pk=pk)

    comment = request.POST.get('comment')

    # Create or update (model validation will also prevent owner self-rating)
    from .models import Rating
    try:
        rating_obj, created = Rating.objects.update_or_create(
            profile=profile,
            user=user,
            defaults={'rating': rating_val, 'comment': comment},
        )
    except Exception as e:
        # capture ValidationError or any other exception raised by model.clean/save
        from django.core.exceptions import ValidationError as DjangoValidationError
        if isinstance(e, DjangoValidationError):
            messages.error(request, '; '.join(e.messages))
        else:
            messages.error(request, 'Could not save rating: %s' % str(e))
        return redirect('profile_detail', pk=pk)

    messages.success(request, "Your rating has been submitted.")
    return redirect('profile_detail', pk=pk)


def profile_detail(request, pk):
    """Show profile detail with all uploaded photos."""
    try:
        profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile does not exist.")
        return redirect('choose')

    photos = profile.images.all()

    # Ratings summary
    from django.db.models import Avg, Count
    rating_agg = profile.ratings.aggregate(avg=Avg('rating'), count=Count('id'))
    avg_rating = rating_agg['avg'] or 0
    rating_count = rating_agg['count'] or 0

    # determine if current logged-in user can rate (regular user and not the owner)
    logged_in_user = None
    logged_in_user_id = request.session.get('logged_in_user_id')
    can_rate = False
    user_rating = None
    if logged_in_user_id:
        try:
            logged_in_user = User.objects.get(id=int(logged_in_user_id))
        except User.DoesNotExist:
            logged_in_user = None

    is_owner = False
    if logged_in_user and profile.user.id == logged_in_user.id:
        is_owner = True

    if logged_in_user and logged_in_user.user_type == 'user' and profile.user.id != logged_in_user.id:
        can_rate = True
        try:
            user_rating_obj = profile.ratings.get(user=logged_in_user)
            user_rating = user_rating_obj.rating
        except Exception:
            user_rating = None

    return render(request, 'demo/Modified_files/companyprofile.html', {
        'profile': profile,
        'photos': photos,
        'is_owner': is_owner,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'can_rate': can_rate,
        'user_rating': user_rating,
    })

# def companyprofile(request):
#     logged_in_user_id = request.session.get('logged_in_user_id')
    
#     profile = UserProfile.objects.get(user_id=2)
#     # except UserProfile.DoesNotExist:
#     #     # Handle the case where the profile doesn't exist for the given user_id
#     #     profile = None

#     return render(request, 'demo/Modified_files/companyprofile.html', {'profile': profile})

# def company_profile(request):
#     # Check if the user is authenticated
#     if request.user.is_authenticated:
#         # Retrieve the UserProfile object associated with the current user
#         profile = UserProfile.objects.get(user=request.user)
#         return render(request, 'company_profile.html', {'profile': profile})
#     else:
#         # If the user is not authenticated, redirect them to the login page
#         return redirect('login')

# def trending(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         confirm_password = request.POST.get('confirm_password')
#         user_type = request.POST.get('user_type')

#         # Check if the user exists in the database
#         try:
#             user = User.objects.get(name=name)
#         except User.DoesNotExist:
#             messages.error(request, "User does not exist. Please sign up.")
#             return render(request, 'demo/Modified_files/trending.html')

#         # Validate password and user_type
#         if user.confirm_password != confirm_password:
#             messages.error(request, "Incorrect password.")
#             return render(request, 'demo/Modified_files/trending.html')
#         if user.user_type != user_type:
#             messages.error(request, "Incorrect user type.")
#             return render(request, 'demo/Modified_files/trending.html')
        
#         # Set the username in the session
#         request.session['logged_in_username'] = name

#         # Redirect to another page after successful authentication
#         return redirect('choose')  # Adjust the redirect as per your URL configuration

#     return render(request, 'demo/Modified_files/trending.html')



# original
def trending(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')

        # Check if the user exists in the database by name or email
        user = None
        try:
            # Try to find user by name first
            user = User.objects.get(name=name)
        except User.DoesNotExist:
            # If not found by name, try by email
            try:
                user = User.objects.get(email=name)
            except User.DoesNotExist:
                messages.error(request, "User does not exist. Please sign up.")
                return render(request, 'demo/Modified_files/trending.html')

        # Validate password and user_type
        if user.confirm_password != confirm_password:
            messages.error(request, "Incorrect password.")
            return render(request, 'demo/Modified_files/trending.html')
        if user.user_type != user_type:
            messages.error(request, "Incorrect user type.")
            return render(request, 'demo/Modified_files/trending.html')
        
        # Set a flag to indicate whether the user is a service provider or not
        is_service_provider = user.user_type == 'service_provider'
        is_user = user.user_type == 'user'
        # Set the username in the session
        request.session['logged_in_username'] = user.name
        request.session['is_service_provider'] = is_service_provider
        request.session['is_user'] = is_user
        request.session['logged_in_user_id'] = user.id
        # Authentication successful, redirect to another page
        return redirect('choose')

    return render(request, 'demo/Modified_files/trending.html')
# def signup(request):
#         return render(request, 'demo/Modified_files/signup.html')

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        city = request.POST.get('city')
        create_password = request.POST.get('create_password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')

        # Check if username already exists
        if User.objects.filter(name=name).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return render(request, 'demo/Modified_files/signup.html')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please use a different email.")
            return render(request, 'demo/Modified_files/signup.html')
        
# Contact validation
        if not contact or not contact.isdigit() or len(contact) < 10:
            messages.error(request, "Invalid contact number. Please enter a valid 10-digit number.")
            return render(request, 'demo/Modified_files/signup.html')
        if create_password != confirm_password:
# Passwords do not match, show an error message
            messages.error(request, "Passwords do not match. Please enter matching passwords.")
            return render(request, 'demo/Modified_files/signup.html')
        
        user = User.objects.create(
            name=name,
            contact=contact,
            email=email,
            city=city,
            create_password=create_password,
            confirm_password=confirm_password,
            user_type=user_type
        )

        if user_type == 'service_provider':
            # pre-populate session so the new provider can create their profile immediately
            request.session['logged_in_username'] = user.name
            request.session['is_service_provider'] = True
            request.session['is_user'] = False
            messages.success(request, "Account created! Please complete your service provider profile.")
            return redirect('createprof')

        messages.success(request, "Account created successfully! Please login.")
        return redirect('trending')

    return render(request, 'demo/Modified_files/signup.html')
