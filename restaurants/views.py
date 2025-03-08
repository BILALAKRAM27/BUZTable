from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ReviewForm, MenuItemForm,MenuItemUpdateForm,special_dealsForm,TableForm,special_dealsUpdateForm,RestaurantCategoryForm,RestaurantScheduleForm,PromotionForm,CommentForm,DeliveryPartnerForm
from .models import Profile, Review,Notification,MenuItem, Order,special_deals,RestaurantSchedule,RestaurantCategory,Promotion,Reservation,Payment,DeliveryPartner,Delivery,Comment,Table
from django.http import JsonResponse
import logging,json,stripe
from django.db.models import Q
from django.conf import settings
from decimal import Decimal
from django.http import HttpResponseForbidden
from user.models import Profile as user_profile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Avg




def home(request):
    top_menu_items = MenuItem.objects.all().order_by('-order_count')[:6]
    top_special_deals = special_deals.objects.all().order_by('-order_count')[:3]

    total_users = Profile.objects.filter().count()
    context = {
        'top_menu_items': top_menu_items,
        'top_special_deals': top_special_deals,
        'total_users': total_users,
    }

    return render(request, "base.html", context)

def privacy_policy(request):
    return render(request, 'restaurants/privacy_policy.html')

def about_us(request):
    total_rest = Profile.objects.filter().count()
    total_users = user_profile.objects.filter().count()
    context = {
        'total_users': total_users,
        'total_rest': total_rest,
    }
    return render(request, 'restaurants/about_us.html',context)

def terms_and_conditions(request):
    return render(request, 'restaurants/terms_and_conditions.html')

def read_more(request):
    return render(request, 'restaurants/read_more.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # Create a profile for the new user
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!', extra_tags='logout-success')
            return redirect('restaurants:restaurant_login')
    else:
        form = UserRegisterForm()
    return render(request, 'restaurants/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.user.profile.is_restaurant:
        profile = get_object_or_404(Profile, user=request.user)
        reviews = Review.objects.filter(restaurant=profile).order_by('-created_at')
        menu_items = profile.menu_items.all()
        special_deal = profile.special_deal.all()
        reservations = Reservation.objects.filter(table__profile=profile, status='pending').order_by('-reservation_date')
        notifications = Notification.objects.filter(restaurant=profile)


        context = {
            'profile': profile,
            'reviews': reviews,
            'menu_items': menu_items,
            'special_deal': special_deal,
            'profile_picture': profile.get_image_base64(),
            'reservations': reservations,
            'notifications': notifications,  
        }
        return render(request, 'restaurants/profile.html', context)
    else:
        return redirect('home')
  


@login_required
def update_profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            profile = p_form.save(commit=False)
            if 'profile_picture' in request.FILES:
                profile.image = request.FILES['profile_picture'].read()  # Save image as binary data
            profile.save()
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('restaurants:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'restaurants/update_profile.html', context)

@login_required
def delete_profile_view(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your profile has been deleted.', extra_tags='logout-success')
        return redirect('restaurants:register')
    return render(request, 'restaurants/delete_profile.html')

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif request.user.is_restaurant:
            return redirect('restaurants:profile')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/admin/')
            elif hasattr(user, 'profile') and user.profile.is_restaurant:
                login(request, user)
                return redirect('restaurants:profile')
            else:
                messages.error(request, 'Only restaurants can log in from this page.', extra_tags='login-error')
                return redirect('restaurants:restaurant_login')  
        else:
            messages.error(request, 'Invalid username or password.', extra_tags='login-error')
    
    return render(request, 'restaurants/login.html')




logger = logging.getLogger(__name__)

@login_required
def restaurant_logout(request):
    logout(request)  # Log out the user
    request.session.flush()  # Clear session data
    messages.success(request, 'You have successfully logged out.', extra_tags='login-error')

    # After logout, redirect to restaurant login page
    return redirect('restaurants:restaurant_login')




logger = logging.getLogger(__name__)

def restaurant_list_view(request):
    search_query = request.GET.get('search', '')
    logger.info(f"Search Query: {search_query}")
    
    if search_query:
        profiles = Profile.objects.filter(
            restaurant_name__icontains=search_query
        )
    else:
        profiles = Profile.objects.all()

    profiles = profiles.annotate(average_rating=Avg('review__rating'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        restaurant_data = []
        for profile in profiles:
            restaurant_data.append({
                'id': profile.id,
                'restaurant_name': profile.restaurant_name,
                'contact_number': profile.contact_number,
                'address': profile.address,
                'description': profile.description,
                'image_data': profile.image_data,  # Add more fields if needed
                'site': profile.site,
                'address_link': profile.address_link,
            })
        logger.info(f"AJAX Response: {restaurant_data}")
        return JsonResponse({'restaurants': restaurant_data})
    
    context = {
        'profiles': profiles,
        'search_query': search_query,
    }
    return render(request, 'restaurants/restaurants_list.html', context)


@login_required
def get_reviews(request, restaurant_id):
    if request.method == 'GET':
        # Fetch the restaurant using the correct model name
        restaurant = get_object_or_404(Profile, id=restaurant_id)
        
        # Fetch the reviews related to the restaurant
        reviews = Review.objects.filter(restaurant=restaurant).order_by('-created_at')
        
        # Prepare the reviews data in the required format
        reviews_data = [{
            'username': review.user.username,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for review in reviews]

        # Return the reviews as JSON response
        return JsonResponse({'reviews': reviews_data})

    elif request.method == 'POST':
        try:
            # Parse the POST request data
            data = json.loads(request.body)

            # Validate and save the review
            restaurant = get_object_or_404(Profile, id=restaurant_id)
            comment = data.get('comment', '')
            rating = int(data.get('rating', 0))

            if not comment or not (1 <= rating <= 5):
                return JsonResponse({'error': 'Invalid input'}, status=400)

            review = Review.objects.create(
                restaurant=restaurant,
                user=request.user,  # Ensure the user is authenticated
                comment=comment,
                rating=rating
            )

            # Return the newly created review as JSON
            return JsonResponse({
                'username': review.user.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid data format'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)





@login_required
def comment(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == 'POST':
        # Determine whether the profile is a restaurant or user profile
        form = CommentForm(request.POST, user=request.user, profile=profile)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response_data = {
                    'success': True,
                    'username': comment.user.username,
                    'body': comment.body,
                    'created_at': comment.created_at.strftime("%b %d, %Y %H:%M"),
                    'is_restaurant': comment.user.user_profile.is_restaurant,  # Check if the user has a restaurant profile
                    'image_data': comment.user.user_profile.image_data if comment.user.user_profile.image_data else None,  # Profile image data
                    'restaurant_name': comment.user.user_profile.restaurant_name if comment.user.user_profile.is_restaurant else None,  # Restaurant name if it's a restaurant
                }
                return JsonResponse(response_data)

        else:
            # If form is invalid, log the form errors for debugging
           if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return redirect('restaurants:restaurant_detail', profile_id=profile.id)


from user.models import UserFavorite
def restaurant_detail_view(request, id):
    restaurant = get_object_or_404(Profile, id=id)
    reviews = Review.objects.filter(restaurant=restaurant).select_related('user').order_by('-created_at')
    menu_items = MenuItem.objects.filter(profile=restaurant)
    special_deal_items = special_deals.objects.filter(profile=restaurant)
    comments = Comment.objects.filter(profile=restaurant).select_related('user').order_by('-created_at')

    top_menu_items = menu_items.order_by('-order_count')[:6]
    top_special_deals = special_deal_items.order_by('-order_count')[:3]

    # Check if user is authenticated
    if request.user.is_authenticated:
        user_review_exists = Review.objects.filter(user=request.user, restaurant=restaurant).exists()
    else:
        user_review_exists = False  # If not authenticated, assume they haven't reviewed

    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX request
            if 'submit_review' in request.POST:
                if user_review_exists:
                    return JsonResponse({'error': 'You have already submitted a review for this restaurant.'}, status=400)

                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.user = request.user
                    review.restaurant = restaurant
                    review.save()

                    return JsonResponse({
                        'user': review.user.username,
                        'comment': review.comment,
                        'rating': review.rating,
                        'created_at': review.created_at.strftime('%b %d, %Y %H:%M')
                    })
                return JsonResponse({'error': 'Invalid form data'}, status=400)

        else:  # Non-AJAX handling (fallback for older browsers)
            if 'submit_review' in request.POST:
                if user_review_exists:
                    return redirect('restaurants:restaurant_detail', id=restaurant.id)

                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.user = request.user
                    review.restaurant = restaurant
                    review.save()
                    return redirect('restaurants:restaurant_detail', id=restaurant.id)

            elif 'submit_comment' in request.POST:
                comment_form = CommentForm(request.POST)
                if comment_form.is_valid():
                    comment = comment_form.save(commit=False)
                    comment.user = request.user
                    comment.profile = restaurant
                    comment.save()
                    return redirect('restaurants:restaurant_detail', id=restaurant.id)

    review_form = ReviewForm()
    comment_form = CommentForm()

    context = {
        'profile': restaurant,
        'reviews': reviews,
        'menu_items': menu_items,
        'special_deal_items': special_deal_items,
        'review_form': review_form,
        'comment_form': comment_form,
        'comments': comments,
        'top_menu_items': top_menu_items,
        'top_special_deals': top_special_deals,
    }

    return render(request, 'restaurants/restaurant_detail.html', context)




@login_required
def add_menu_item(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)  # Ensure to pass request.FILES for handling file upload
        if form.is_valid():
            menu_item = form.save(commit=False)  # Create MenuItem instance without saving to DB
            menu_item.profile = profile  # Associate with the user's profile
            
            # If there is an image, it will already be handled by the form's save method
            menu_item.save()  # Save the instance to the database
            messages.success(request, 'Menu item added successfully!')
            return redirect('restaurants:profile')
        else:
            print(form.errors)  # Debug: Check form errors if the form is not valid
    else:
        form = MenuItemForm()
    
    return render(request, 'restaurants/add_menu_item.html', {'form': form})

@login_required
def update_menu_item(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    profile = get_object_or_404(Profile, user=request.user)
    
    # Ensure the menu item belongs to the current user's profile
    if menu_item.profile != profile:
        messages.error(request, "You do not have permission to update this menu item.")
        return redirect('restaurants:profile')
    
    if request.method == 'POST':
        form = MenuItemUpdateForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()  # Save the form with updated data
            messages.success(request, 'Menu item updated successfully!')
            return redirect('restaurants:profile')
    else:
        form = MenuItemUpdateForm(instance=menu_item)
    
    return render(request, 'restaurants/update_menu_item.html', {'form': form, 'menu_item': menu_item})

@login_required
def delete_menu_item(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    profile = menu_item.profile
    menu_item.delete()
    messages.success(request, 'Menu item deleted successfully!')
    return redirect('restaurants:profile')


@login_required
def add_special_deal(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = special_dealsForm(request.POST, request.FILES)
        if form.is_valid():
            special_deal = form.save(commit=False)
            special_deal.profile = profile  
            special_deal.save()
            messages.success(request, 'Special Deal added successfully!')
            return redirect('restaurants:profile')
    else:
        form = special_dealsForm()
    
    return render(request, 'restaurants/add_special_deal.html', {'form': form})

@login_required
def update_special_deal(request, special_deal_id):
    special_deal = get_object_or_404(special_deals, id=special_deal_id)
    profile = special_deal.profile

    if request.method == 'POST':
        form = special_dealsUpdateForm(request.POST, request.FILES, instance=special_deal)
        if form.is_valid():
            form.save()  # Just call form.save() to handle image as well
            messages.success(request, 'Special Deal updated successfully!')
            return redirect('restaurants:profile')
    else:
        form = special_dealsUpdateForm(instance=special_deal)
    
    return render(request, 'restaurants/update_special_deal.html', {'form': form, 'special_deal': special_deal})

@login_required
def delete_special_deal(request, special_deal_id):
    special_deal = get_object_or_404(special_deals, id=special_deal_id)
    profile = special_deal.profile
    special_deal.delete()
    messages.success(request, 'Special Deal deleted successfully!')
    return redirect('restaurants:profile')


@login_required
def add_category(request):
    if request.method == 'POST':
        form = RestaurantCategoryForm(request.POST)
        if form.is_valid():
            # Get the Profile of the currently logged-in user
            profile = Profile.objects.get(user=request.user)
            
            # Save the new category and associate it with the user's profile
            category = form.save(commit=False)
            category.profile = profile  # Associate the category with the current user's profile
            category.save()
            
            return redirect('restaurants:category_list')  # Redirect to the category list view
    else:
        form = RestaurantCategoryForm()
    
    return render(request, 'restaurants/add_category.html', {'form': form})

@login_required
def delete_category(request, category_id):
    # Retrieve the category by its ID or return a 404 if not found
    category = get_object_or_404(RestaurantCategory, id=category_id)
    
    # Check if the logged-in user is the owner of the category's profile
    if category.profile.user != request.user:
        messages.error(request, "You do not have permission to delete this category.")
        return redirect('restaurants:category_list')

    # Delete the category
    category.delete()

    # Show a success message
    messages.success(request, "Category deleted successfully.")

    # Redirect to the category list page
    return redirect('restaurants:category_list')

def category_list(request):
    # Get the search query from the GET parameters
    search_query = request.GET.get('search', '')
    
    # Filter categories based on the search query
    categories = RestaurantCategory.objects.filter(
        Q(category_name__icontains=search_query) |  # Filter by category name
        Q(profile__restaurant_name__icontains=search_query)  # Filter by restaurant name
    ).order_by('category_name')  # Optional: ordering categories
    
    return render(request, 'restaurants/category_list.html', {'categories': categories, 'search_query': search_query})

@login_required
def add_schedule(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = RestaurantScheduleForm(request.POST)
        if form.is_valid():
            # Get the selected day of the week from the form
            day_of_week = form.cleaned_data['day_of_week']

            # Check if a schedule already exists for this day
            if RestaurantSchedule.objects.filter(profile=profile, day_of_week=day_of_week).exists():
                messages.warning(request, f"A schedule already exists for {day_of_week}.")
                return redirect('restaurants:schedule_list')

            # Save the new schedule
            schedule = form.save(commit=False)
            schedule.profile = profile
            schedule.save()
            return redirect('restaurants:schedule_list')
    else:
        # If the day is passed as a query parameter, pre-fill the form with that day
        day = request.GET.get('day', None)
        form = RestaurantScheduleForm(initial={'day_of_week': day}) if day else RestaurantScheduleForm()

    return render(request, 'restaurants/add_schedule.html', {'form': form})

@login_required
def update_schedule(request, schedule_id):
    schedule = get_object_or_404(RestaurantSchedule, id=schedule_id, profile__user=request.user)
    
    if request.method == 'POST':
        form = RestaurantScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('restaurants:schedule_list')
    else:
        form = RestaurantScheduleForm(instance=schedule)
    
    return render(request, 'restaurants/update_schedule.html', {'form': form})
@login_required
def schedule_list(request):
    # Get the profile of the current logged-in user
    profile = get_object_or_404(Profile, user=request.user)
    
    # Get all schedules for the user's profile, ordered by 'day_of_week'
    schedules = RestaurantSchedule.objects.filter(profile=profile).order_by('day_of_week')
    
    # List of days to ensure they are displayed in the correct order
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    return render(request, 'restaurants/schedule_list.html', {'schedules': schedules, 'days_of_week': days_of_week})




def restaurant_dashboard(request):
    # Get the profile of the current logged-in user
    profile = get_object_or_404(Profile, user=request.user)
    restaurant = profile
    
    # Fetch orders, reviews, and reservations for the restaurant
    orders = Order.objects.filter(restaurant=restaurant)
    reviews = Review.objects.filter(restaurant=restaurant)
    reservations = Reservation.objects.filter(restaurant=restaurant)

    # Pagination handling for each section (orders, reviews, reservations)
    orders_page = Paginator(orders, 10)
    reviews_page = Paginator(reviews, 10)
    reservations_page = Paginator(reservations, 10)

    orders_page_number = request.GET.get('orders_page', 1)
    reviews_page_number = request.GET.get('reviews_page', 1)
    reservations_page_number = request.GET.get('reservations_page', 1)

    try:
        orders_page_obj = orders_page.get_page(orders_page_number)
    except PageNotAnInteger:
        orders_page_obj = orders_page.get_page(1)
    except EmptyPage:
        orders_page_obj = orders_page.get_page(orders_page.num_pages)

    try:
        reviews_page_obj = reviews_page.get_page(reviews_page_number)
    except PageNotAnInteger:
        reviews_page_obj = reviews_page.get_page(1)
    except EmptyPage:
        reviews_page_obj = reviews_page.get_page(reviews_page.num_pages)

    try:
        reservations_page_obj = reservations_page.get_page(reservations_page_number)
    except PageNotAnInteger:
        reservations_page_obj = reservations_page.get_page(1)
    except EmptyPage:
        reservations_page_obj = reservations_page.get_page(reservations_page.num_pages)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {
            'orders': orders_page_obj,
            'reviews': reviews_page_obj,
            'reservations': reservations_page_obj,
        }
        html = render_to_string('restaurants/restaurant_dashboard_partial.html', context, request=request)
        return JsonResponse({
            'html': html,
            'orders_page': orders_page_obj.number,
            'reviews_page': reviews_page_obj.number,
            'reservations_page': reservations_page_obj.number
        })

    return render(request, 'restaurants/restaurant_dashboard.html', {
        'orders': orders_page_obj,
        'reviews': reviews_page_obj,
        'reservations': reservations_page_obj,
    })





def some_error_page_view(request):
    return render(request,'restaurants/some_error_page.html')



@login_required
def manage_orders(request):
    profile = get_object_or_404(Profile, user=request.user)
    orders = Order.objects.filter(menu_item__profile=profile).order_by('-order_date')
    return render(request, 'restaurants/manage_orders.html', {'orders': orders})


def manage_reviews(request):
    profile = get_object_or_404(Profile, user=request.user)
    reviews = Review.objects.filter(restaurant=profile).order_by('-created_at')
    return render(request, 'restaurants/manage_reviews.html', {'reviews': reviews})



@login_required
def manage_promotions(request):
    try:
        profile = request.user.profile  # Access the Profile instance for the logged-in user
    except Profile.DoesNotExist:
        # Handle case when the user does not have a profile
        messages.error(request, "Your profile does not exist.")
        return redirect('restaurants:profile')  # Redirect to profile creation or another appropriate page
    
    promotions = Promotion.objects.filter(profile=profile)  # Get promotions for the logged-in user's profile
    return render(request, 'restaurants/manage_promotions.html', {'promotions': promotions})



@login_required
def create_promotion(request):
    try:
        profile = request.user.profile  # Access the Profile instance for the logged-in user
    except Profile.DoesNotExist:
        # Handle case when the user does not have a profile
        messages.error(request, "Your profile does not exist.")
        return redirect('restaurants:profile')  # Redirect to profile creation page
    
    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.profile = profile  # Set the profile to the logged-in user's profile
            promotion.save()  # Save the new promotion
            messages.success(request, 'Promotion created successfully!')
            return redirect('restaurants:manage_promotions')  # Redirect to the manage promotions page
    else:
        form = PromotionForm()
    return render(request, 'restaurants/create_promotion.html', {'form': form})



@login_required
def edit_promotion(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk, profile=request.user.profile)  # Ensure it belongs to the logged-in user's profile
    if request.method == 'POST':
        form = PromotionForm(request.POST, instance=promotion)
        if form.is_valid():
            form.save()  # Update the promotion
            messages.success(request, 'Promotion updated successfully!')
            return redirect('restaurants:manage_promotions')  # Redirect to the manage promotions page
    else:
        form = PromotionForm(instance=promotion)
    return render(request, 'restaurants/edit_promotion.html', {'form': form, 'promotion': promotion})


@login_required
def delete_promotion(request, pk):
    try:
        profile = request.user.profile  # Access the Profile instance for the logged-in user
    except Profile.DoesNotExist:
        messages.error(request, "Your profile does not exist.")
        return redirect('restaurants:profile')

    promotion = get_object_or_404(Promotion, pk=pk, profile=profile)  # Ensure it belongs to the logged-in user's profile
    promotion.delete()
    messages.success(request, 'Promotion deleted successfully!')
    return redirect('restaurants:manage_promotions')  # Redirect to the manage promotions page

####Reservation
@login_required
def add_table(request):
    # Ensure the user is a restaurant
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('user:home')  # Redirect non-restaurants to home
    
    if not profile.is_restaurant:
        return redirect('user:home')  # Redirect if the user is not a restaurant
    
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.profile = profile  # Associate the table with the restaurant profile
            table.save()
            return redirect('restaurants:manage_tables')
    else:
        form = TableForm()

    return render(request, 'restaurants/add_table.html', {'form': form})

@login_required
def manage_tables(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('user:home')  # Redirect non-restaurants to home
    
    if not profile.is_restaurant:
        return redirect('user:home')  # Redirect if the user is not a restaurant

    tables = Table.objects.filter(profile=profile)  # Fetch tables for the logged-in restaurant

    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.profile = profile  # Associate the table with the restaurant profile
            table.save()
            return redirect('restaurants:manage_tables')  # Redirect to manage_tables after saving the table
    else:
        form = TableForm()

    context = {
        'form': form,
        'tables': tables,  # Pass the tables to the template
    }

    return render(request, 'restaurants/manage_tables.html', context)

@login_required
def delete_table(request, table_id):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('user:home')  # Redirect non-restaurants to home
    
    if not profile.is_restaurant:
        return redirect('user:home')  # Redirect if the user is not a restaurant

    # Get the table to delete
    table = get_object_or_404(Table, id=table_id, profile=profile)  # Only allow deletion of tables associated with the logged-in restaurant

    # Delete the table
    table.delete()

    return redirect('restaurants:manage_tables')  # Stay on the manage_tables page after deletion


@login_required
def toggle_table_availability(request, table_id):
    """
    View to toggle the availability of a table (no JSON response).
    """
    try:
        # Ensure the user has a restaurant profile
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('user:home')  # Redirect non-restaurants to home

    if not profile.is_restaurant:
        return redirect('user:home')  # Redirect if the user is not a restaurant

    # Get the table to toggle availability
    table = get_object_or_404(Table, id=table_id, profile=profile)  # Ensure table belongs to the logged-in restaurant

    # Toggle the availability
    table.available = not table.available
    table.save()

    # Provide success feedback to the user
    messages.success(request, f"Table {table.id} availability updated to {'Available' if table.available else 'Unavailable'}.")

    # Redirect to manage_tables or any relevant page
    return redirect('restaurants:manage_tables')



@login_required
def update_reservation_status(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        # Update the reservation status
        status = request.POST.get('status')
        reservation.status = status
        reservation.save()

        # Notify the user about the status change
        Notification.objects.create(
            restaurant=reservation.table.profile,  # Link to the restaurant
            message=f"Your reservation status has been updated to '{status}' for {reservation.reservation_date}.",
            reservation=reservation,
            is_read=False  # Notification is unread initially
        )

        # Add a success message for the restaurant
        messages.success(request, f"Reservation status updated to {status} and notification sent to the user.")
        

        # Redirect to the restaurant's dashboard
        return redirect('restaurants:restaurant_dashboard')

    return render(request, 'restaurants/update_reservation_status.html', {'reservation': reservation})



# Set your secret key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
@login_required
def payment_view(request, total_price):
    if request.method == 'GET':
        total_price = Decimal(total_price)  # Ensure it's a Decimal, not a string
        return render(request, 'restaurants/payments.html', {
            'STRIPE_TEST_PUBLISHABLE_KEY': settings.STRIPE_TEST_PUBLISHABLE_KEY,
            'total_price': total_price
        })
    
    if request.method == 'POST':
        token = request.POST['stripeToken']
        
        # Ensure the total_price is a Decimal (if not already)
        total_price = Decimal(total_price)

        try:
            # Create a Stripe charge
            charge = stripe.Charge.create(
                amount=int(total_price * 100),  # Convert to cents (multiply by 100)
                currency='usd',
                description='Restaurant Order Charge',
                source=token
            )

            # Record the successful payment in the database (optional)
            # You can include a Payment object creation here if you want to track each payment

            return redirect('restaurants:payment_success')  # Redirect to payment success page
        except stripe.error.CardError as e:
            return render(request, 'restaurants/payments.html', {'error': str(e)})
        except stripe.error.StripeError as e:
            return render(request, 'restaurants/payments.html', {'error': 'There was an error processing your payment. Please try again.'})

@login_required
def payment_success(request):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the latest order for the user with 'preparing' status
    order = Order.objects.filter(user=request.user, status='preparing').latest('order_date')

    # Calculate the total price for the order (using the quantities field and ManyToMany relationships)
    total_price = 0

    # Add menu items to the total price
    for menu_item_quantity in order.menuitemquantity_set.all():  # Assuming MenuItemQuantity links Order and MenuItem
        total_price += menu_item_quantity.menu_item.price * menu_item_quantity.quantity

    # Add special deals to the total price
    for special_deal_quantity in order.specialdealquantity_set.all():  # Assuming SpecialDealQuantity links Order and SpecialDeal
        total_price += special_deal_quantity.special_deal.price * special_deal_quantity.quantity

    # Create a payment record in the database
    payment = Payment(
        order=order,  # Link to the order
        amount=total_price,  # Use the calculated total price
        payment_status='completed',  # Customize this based on your needs
        payment_method='stripe',  # Store the method as 'stripe'
        transaction_id=str(order.id),  # Unique identifier for the transaction (you can customize this)
    )
    payment.save()

    # Update the order status to 'completed' after successful payment
    order.status = 'completed'
    order.payment_status = 'paid'  # Ensure the payment status is updated
    order.save()

    # Clear the cart (optional)
    response = redirect('user:order_success')
    response.delete_cookie('cart')  # Clear the cart from cookies (if applicable)

    return response



def most_ordered(request):
    # Get the top 10 most ordered menu items and special deals, ordered by order_count
    top_menu_items = MenuItem.objects.all().order_by('-order_count')[:10]  # Get top 10 by order count
    top_special_deals = special_deals.objects.all().order_by('-order_count')[:10]  # Get top 10 by order count
    
    context = {
        'top_menu_items': top_menu_items,
        'top_special_deals': top_special_deals
    }
    return render(request, 'restaurants/orderedtime.html', context)

@login_required
def add_delivery_partner(request, restaurant_id):
    # Get the restaurant instance
    restaurant = get_object_or_404(Profile, id=restaurant_id)

    # Ensure the logged-in user is the owner of the restaurant
    if request.user != restaurant.user:
        return HttpResponseForbidden("You are not allowed to add a delivery partner to this restaurant.")

    if request.method == 'POST':
        form = DeliveryPartnerForm(request.POST)
        if form.is_valid():
            # Create and save the new delivery partner
            delivery_partner = form.save()

            # Check if this delivery partner is already added to the restaurant
            if delivery_partner not in restaurant.delivery_partners.all():
                restaurant.delivery_partners.add(delivery_partner)  # Add to restaurant's delivery partners
                return redirect('restaurants:manage_delivery_partners', restaurant_id=restaurant.id)
            else:
                form.add_error(None, "This delivery partner is already associated with the restaurant.")
    else:
        form = DeliveryPartnerForm()

    # Pass the restaurant to the context so that it can be used in the template
    return render(request, 'restaurants/add_delivery_partner.html', {'form': form, 'restaurant': restaurant})

@login_required
def update_delivery_partner(request, restaurant_id, partner_id):
    # Get the restaurant and delivery partner instances
    restaurant = get_object_or_404(Profile, id=restaurant_id)
    delivery_partner = get_object_or_404(DeliveryPartner, id=partner_id)

    # Ensure the logged-in user is the owner of the restaurant
    if request.user != restaurant.user:
        return HttpResponseForbidden("You are not allowed to update this delivery partner.")

    if request.method == 'POST':
        form = DeliveryPartnerForm(request.POST, instance=delivery_partner)
        if form.is_valid():
            form.save()
            return redirect('restaurants:manage_delivery_partners', restaurant_id=restaurant.id)
    else:
        form = DeliveryPartnerForm(instance=delivery_partner)

    return render(request, 'restaurants/update_delivery_partner.html', {'form': form, 'restaurant': restaurant})

@login_required
def remove_delivery_partner(request, restaurant_id, partner_id):
    # Get the restaurant and delivery partner instances
    restaurant = get_object_or_404(Profile, id=restaurant_id)
    delivery_partner = get_object_or_404(DeliveryPartner, id=partner_id)

    # Ensure the logged-in user is the owner of the restaurant
    if request.user != restaurant.user:
        return HttpResponseForbidden("You are not allowed to remove this delivery partner.")

    # Remove the delivery partner from the restaurant's many-to-many relationship
    restaurant.delivery_partners.remove(delivery_partner)

    # Optionally, delete the delivery partner if you want to completely remove it from the system
    # delivery_partner.delete()  # Uncomment if you want to delete the partner

    return redirect('restaurants:manage_delivery_partners', restaurant_id=restaurant.id)

@login_required
def manage_delivery_partners(request, restaurant_id):
    # Get the restaurant instance
    restaurant = get_object_or_404(Profile, id=restaurant_id)

    # Ensure the logged-in user is the owner of the restaurant
    if request.user != restaurant.user:
        return redirect('restaurants:home')  # Or show a permission error page
    
    # Get the list of delivery partners associated with the restaurant
    delivery_partners = restaurant.delivery_partners.all()

    return render(request, 'restaurants/manage_delivery_partners.html', {
        'restaurant': restaurant,
        'delivery_partners': delivery_partners,
    })


