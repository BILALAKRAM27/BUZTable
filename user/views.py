from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from restaurants.models import Table
from restaurants.models import Profile as restaurant_profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm,ReservationForm
from restaurants.models import Order,Notification,Review,MenuItem,special_deals,Reservation ,MenuItemQuantity,SpecialDealQuantity,Delivery,DeliveryPartner,Comment
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from .models import Profile
import json
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView
from django.http import JsonResponse
from django.core.cache import cache
from restaurants.forms import CommentForm
from .forms import CommentForm
from uuid import uuid4 
from .models import UserFavorite
from restaurants.models import Profile as RestaurantProfile, MenuItem, special_deals
from restaurants.models import special_deals  as SpecialDeal

def home(request):
    # Get the top 10 most ordered menu items and special deals
    top_menu_items = MenuItem.objects.all().order_by('-order_count')[:6]
    top_special_deals = special_deals.objects.all().order_by('-order_count')[:3]

    # Get the total number of users and restaurants
    total_users = Profile.objects.filter().count()
    total_rest = restaurant_profile.objects.filter().count()
    
    context = {
        'top_menu_items': top_menu_items,
        'top_special_deals': top_special_deals,
        'total_users': total_users,
        'total_rest':total_rest,
    }

    return render(request, "base.html", context)

def register_viu(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('user:user_login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/user_register.html', {'form': form})

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)

   
    pending_orders = Order.objects.filter(user=request.user, status='preparing')
    
    notifications = Notification.objects.filter(reservation__user=request.user).order_by('-id')

    context = {
        'profile': profile,
        'profile_picture': profile.get_image_base64(),
        'pending_orders': pending_orders,
        'notifications': notifications,
    }
    return render(request, 'user/uprofile.html', context)

@login_required
def update_profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.user_profile)
        if u_form.is_valid() and p_form.is_valid():
            profile = p_form.save(commit=False)
            if 'profile_picture' in request.FILES:
                profile.image = request.FILES['profile_picture'].read()  
            profile.save()
            u_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('user:uprofile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.user_profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'user/update_user_profile.html', context)

@login_required
def delete_profile_view(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your profile has been deleted.')
        return redirect('user:home')
    return render(request, 'user/delete_user_profile.html')

def login_view(request):
    # If the user is already logged in, redirect to the appropriate page
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif not request.user.user_profile.is_restaurant:
            return redirect('user:uprofile')
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
            elif hasattr(user, 'user_profile') and not user.user_profile.is_restaurant:
                login(request, user)
                return redirect('user:uprofile')  # Redirect to user profile page after successful login
            else:
                messages.error(request, 'Only users can log in from this page.', extra_tags='login-error')
                return redirect('user:user_login')  # Handle error case for restaurants logging in
        else:
            messages.error(request, 'Invalid username or password.', extra_tags='login-error')
    
    return render(request, 'user/user_login.html')






@login_required
def user_logout_view(request):
    user = request.user
    logout(request)  
    request.session.flush()  

    messages.success(request, 'You have successfully logged out.', extra_tags='logout-success')

    if hasattr(user, 'profile') and user.profile.is_restaurant:
        return redirect('restaurants:restaurant_login')  # Redirect to the restaurant login page
    else:
        return redirect('user:user_login')  # Redirect to the user login page


from django.core.paginator import Paginator
@login_required
def user_dashboard(request):
    try:
       
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect('restaurants:some_error_page')  
    
    
   
    orders = Order.objects.filter(user=request.user)
    reservations = Reservation.objects.filter(user=request.user)
    reviews = Review.objects.filter(user=request.user)
    
    if profile.is_restaurant:  
        notifications = Notification.objects.filter(restaurant=profile, is_read=False).order_by('-id')
    else:  
        notifications = Notification.objects.filter(reservation__user=request.user, is_read=False).order_by('-id')

    
   
    if request.method == 'POST' and 'clear_notifications' in request.POST:
        notifications.update(is_read=True)  

        return HttpResponseRedirect(request.path) 

   
    orders_page = Paginator(orders, 10).get_page(request.GET.get('page'))
    reservations_page = Paginator(reservations, 10).get_page(request.GET.get('page'))
    reviews_page = Paginator(reviews, 10).get_page(request.GET.get('page'))
    
    return render(request, 'user/user_dashboard.html', {
        'orders_page': orders_page,
        'reservations_page': reservations_page,
        'reviews_page': reviews_page,
        'notifications': notifications,

    })


@login_required
def comment(request, profile_id):
  
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == 'POST':
       
        form = CommentForm(request.POST, user=request.user, profile=profile)

        if form.is_valid():
         
            comment = form.save(commit=False)
            comment.user = request.user
            comment.profile = profile  
            comment.save()

       
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response_data = {
                    'success': True,
                    'username': comment.user.username,
                    'body': comment.body,
                    'created_at': comment.created_at.strftime("%b %d, %Y %H:%M"),
                    'is_restaurant': comment.user.user_profile.is_restaurant if hasattr(comment.user, 'user_profile') else False,
                    'image_data': comment.user.user_profile.image_data if hasattr(comment.user, 'user_profile') and comment.user.user_profile.image_data else None,
                }

                if comment.user.user_profile.is_restaurant:
                    response_data['restaurant_name'] = comment.user.user_profile.restaurant_name

                return JsonResponse(response_data)
        else:
            if request.is_ajax():
                form_errors = form.errors.as_json()
                print("Form Errors:", form_errors)
                return JsonResponse({'success': False, 'error': form_errors}, status=400)

    return redirect('user:profile_detail', profile_id=profile.id)


# Utility function to get cart from cache
def get_cart(request):
    user_id = request.user.id
    cache_key = f'cart_{user_id}'
    cart = cache.get(cache_key, '[]')  # Default to an empty list if no cart in cache
    try:
        return json.loads(cart)
    except json.JSONDecodeError:
        return []  # Return an empty cart if the cache is invalid

# Utility function to set cart in cache
def set_cart(request, cart):
    user_id = request.user.id
    cache_key = f'cart_{user_id}'
    cache.set(cache_key, json.dumps(cart))


@login_required
def add_to_cart(request, item_type, item_id):
    # Retrieve the item based on its type (MenuItem or special_deals)
    try:
        if item_type == 'menu_item':
            item = MenuItem.objects.get(id=item_id)
        elif item_type == 'special_deal':
            item = special_deals.objects.get(id=item_id)
        else:
            return HttpResponse('Invalid item type', status=400)
    except MenuItem.DoesNotExist:
        return HttpResponse('MenuItem not found', status=404)
    except special_deals.DoesNotExist:
        return HttpResponse('SpecialDeal not found', status=404)

    quantity = int(request.POST.get('quantity', 1))
    
    # Initialize or get the cart from cache
    cart = get_cart(request)
    
    price = float(item.price)  # Convert the Decimal to float
    
    # Check if item already exists in the cart
    for cart_item in cart:
        if cart_item['id'] == item.id and cart_item['item_type'] == item_type:
            cart_item['quantity'] += quantity  # Increment quantity if item is already in cart
            break
    else:
        # If the item is not in the cart, add it
        cart.append({
            'id': item.id,
            'name': item.name,
            'price': price, 
            'quantity': quantity,
            'item_type': item_type
        })


    set_cart(request, cart)

    return redirect('user:view_cart')

@login_required
def view_cart(request):
    cart = get_cart(request)  
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render(request, 'user/view_cart.html', {'cart': cart, 'total_price': total_price})

@login_required
def remove_from_cart(request, item_id, item_type):
    """
    Removes an item from the cart based on its ID and type.
    """
    
    cart = get_cart(request)

    # Filter out the item to remove, matching both ID and type
    cart = [item for item in cart if not (item['id'] == item_id and item['item_type'] == item_type)]

    # Update the cart in cache
    set_cart(request, cart)

    return redirect('user:view_cart')


def clear_cart(request):
    user_id = request.user.id
    cache_key = f'cart_{user_id}'
    cache.delete(cache_key)




def create_order(request, cart):
    """Create an order from the cart."""
    total_price = 0
    for item in cart:
        menu_item = MenuItem.objects.get(id=item['id'])
        order = Order(
            user=request.user,
            menu_item=menu_item,
            quantity=item['quantity'],
            status='preparing',  
        )
        order.save()
        total_price += menu_item.price * item['quantity']
    return total_price





@login_required
def checkout(request):
    # Get the user's profile
    try:
        profile = request.user.user_profile
    except Profile.DoesNotExist:
        return redirect('user:uprofile')

    # Get cart items
    cart_items = get_cart(request)
    if not cart_items:
        return redirect('user:view_cart')

    menu_items_in_cart = {}
    special_deals_in_cart = {}

    # Process cart items
    for item in cart_items:
        if item['item_type'] == 'menu_item':
            menu_item_id = item['id']
            quantity = item['quantity']
            menu_items_in_cart[menu_item_id] = menu_items_in_cart.get(menu_item_id, 0) + quantity
        elif item['item_type'] == 'special_deal':
            special_deal_id = item['id']
            quantity = item['quantity']
            special_deals_in_cart[special_deal_id] = special_deals_in_cart.get(special_deal_id, 0) + quantity

    # Fetch available menu items and special deals
    available_menu_items = MenuItem.objects.filter(id__in=menu_items_in_cart.keys())
    available_special_deals = special_deals.objects.filter(id__in=special_deals_in_cart.keys())

    total_price = sum(item.price * menu_items_in_cart[item.id] for item in available_menu_items)
    total_price += sum(deal.price * special_deals_in_cart[deal.id] for deal in available_special_deals)

    # Determine the restaurant
    restaurant = None
    if available_menu_items:
        restaurant = available_menu_items[0].profile
    elif available_special_deals:
        restaurant = available_special_deals[0].profile

    if not restaurant:
        return redirect('user:view_cart')

    # Get delivery partners for the restaurant
    delivery_partners = restaurant.delivery_partners.all()

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        delivery_method = request.POST.get('delivery_method')  # Takeout/Delivery
        delivery_partner_id = request.POST.get('delivery_partner') if delivery_method == 'delivery' else None

        # Check if a delivery partner is selected for delivery method
        if delivery_method == 'delivery' and not delivery_partner_id:
            return render(request, 'user/checkout.html', {
                'cart_items': cart_items,
                'total_price': total_price,
                'delivery_partners': delivery_partners,
                'error_message': 'Please select a delivery partner.'
            })

        # Fetch the delivery partner if selected
        delivery_partner = None
        if delivery_method == 'delivery':
            try:
                delivery_partner = DeliveryPartner.objects.get(id=delivery_partner_id)
            except DeliveryPartner.DoesNotExist:
                return render(request, 'user/checkout.html', {
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'delivery_partners': delivery_partners,
                    'error_message': 'Invalid delivery partner selected.'
                })

        # Create the order
        order = Order(
            user=request.user,
            restaurant=restaurant,
            status='preparing',
            full_name=full_name,
            address=address,
            phone_number=phone_number,
            payment_id=str(uuid4()),
            delivery_method=delivery_method,
            delivery_partner=delivery_partner if delivery_method == 'delivery' else None
        )
        order.save()

        # Create Delivery instance if delivery method is selected
        if delivery_method == 'delivery' and delivery_partner:
            delivery = Delivery(
                order=order,
                delivery_partner=delivery_partner,
                status='pending',  
            )
            delivery.save()

        # Add items to the order
        for menu_item in available_menu_items:
            quantity = menu_items_in_cart[menu_item.id]
            MenuItemQuantity.objects.create(order=order, menu_item=menu_item, quantity=quantity)
            menu_item.order_count += quantity
            menu_item.save()

        for special_deal in available_special_deals:
            quantity = special_deals_in_cart[special_deal.id]
            SpecialDealQuantity.objects.create(order=order, special_deal=special_deal, quantity=quantity)
            special_deal.order_count += quantity
            special_deal.save()

        # Clear the cart after placing the order
        clear_cart(request)

        return redirect('restaurants:payments', total_price=str(total_price))
    
    cart_items_context = []
    for item in available_menu_items:
        cart_items_context.append({
            'type': 'menu_item',
            'item': item,
            'quantity': menu_items_in_cart[item.id]
        })
    for deal in available_special_deals:
        cart_items_context.append({
            'type': 'special_deal',
            'item': deal,
            'quantity': special_deals_in_cart[deal.id]
        })

    context = {
        'cart_items': cart_items_context,
        'total_price': total_price,
        'delivery_partners': delivery_partners,
        'error_message': None,
    }

    return render(request, 'user/checkout.html', context)


@login_required
def order_success(request):
    
    last_order = Order.objects.filter(user=request.user).order_by('-order_date').first()

    if last_order:
        order_items = []

        # Fetch menu items and special deals through the through models
        menu_item_quantities = last_order.menuitemquantity_set.all()
        special_deal_quantities = last_order.specialdealquantity_set.all()

        # Add menu items to the order items list
        for menu_item_quantity in menu_item_quantities:
            order_items.append({
                'item': menu_item_quantity.menu_item,
                'quantity': menu_item_quantity.quantity,
                'is_special_deal': False
            })

        # Add special deals to the order items list
        for special_deal_quantity in special_deal_quantities:
            order_items.append({
                'item': special_deal_quantity.special_deal,
                'quantity': special_deal_quantity.quantity,
                'is_special_deal': True
            })

        # Calculate the total price
        total_price = sum(item['item'].price * item['quantity'] for item in order_items if not item['is_special_deal'])
        total_price += sum(item['item'].price * item['quantity'] for item in order_items if item['is_special_deal'])
    else:
        order_items = []
        total_price = 0

    # Return the order success template with order details
    return render(request, 'user/order_success.html', {
        'order_items': order_items,
        'total_price': total_price,
        'shipping_details': last_order,
    })






### reservation

@login_required
def make_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.status = 'pending'
            reservation.save()

            # Set table availability to False after reservation is made
            reservation.table.available = False
            reservation.table.save()

            # Send notification
            restaurant_profile = reservation.table.profile
            Notification.objects.create(
                restaurant=restaurant_profile,
                message=f"New reservation request from {request.user.username} on {reservation.reservation_date}.",
                is_read=False
            )

            # Add success message
            messages.success(request, f'Your reservation has been successfully made on {reservation.reservation_date} at {reservation.table.profile.restaurant_name}.')

            return redirect('user:user_dashboard')
    else:
        form = ReservationForm()

    return render(request, 'user/make_reservation.html', {'form': form})

@login_required
def cancel_reservation(request, reservation_id):
    try:
        # Fetch the reservation instance
        reservation = Reservation.objects.get(id=reservation_id, user=request.user)

        if reservation.status == 'canceled':
            messages.warning(request, 'This reservation has already been canceled.')
            return redirect('user:user_dashboard')

        # Update the reservation status
        reservation.status = 'canceled'
        reservation.save()

        # Set the table availability back to True
        table = reservation.table
        table.available = True
        table.save()

        restaurant_profile = table.profile  # Accessing the restaurant's profile from the table
        Notification.objects.create(
            restaurant=restaurant_profile,
            message=f"Reservation from {request.user.username} on {reservation.reservation_date} has been canceled.",
            is_read=False
        )

        # Add success message
        messages.success(request, f'Your reservation on {reservation.reservation_date} at {restaurant_profile.restaurant_name} has been successfully canceled.')

    except Reservation.DoesNotExist:
        messages.error(request, 'Reservation not found.')

    return redirect('user:user_dashboard')



@login_required
def delete_all_notifications(request):
    # Delete all notifications for the current user
    notifications = Notification.objects.filter(reservation__user=request.user)
    notifications.delete()

    # Show a success message
    messages.success(request, 'All notifications have been deleted.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Custom Password Reset Confirm View
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('user:password_reset_complete')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context




class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'user/password_reset_form.html'
    email_template_name = 'user/password_reset_email.html'
    subject_template_name = 'user/password_reset_subject.txt'
    success_url = reverse_lazy('user:password_reset_done')

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            # The form handling will occur here
            return super().post(request, *args, **kwargs)
        else:
            # Handle errors if needed
            return self.form_invalid(form)
        
@login_required
def order_confirmation(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    if orders:
        latest_order = orders[0]
        delivery = Delivery.objects.get(order=latest_order)
        return render(request, 'user/order_confirmation.html', {
            'order': latest_order,
            'delivery': delivery,
        })
    return redirect('user:view_cart')

@login_required
def track_delivery(request, tracking_number):
    delivery = get_object_or_404(Delivery, tracking_number=tracking_number)
    return render(request, 'user/track_delivery.html', {'delivery': delivery})


def get_tables(request):
    restaurant_id = request.GET.get('restaurant_id')
    
    # Fetch tables associated with the selected restaurant profile
    tables = Table.objects.filter(profile_id=restaurant_id, available=True)

    # Prepare data for the table options dropdown
    table_options = [{'id': table.id, 'name': f"Table for {table.max_guests} guests"} for table in tables]
    
    return JsonResponse(table_options, safe=False)





@login_required
def add_to_favorites(request, favorite_id, favorite_type):
    user_profile = request.user.user_profile

    #
    if favorite_type == 'restaurant':
        
        restaurant = get_object_or_404(RestaurantProfile, id=favorite_id)
        
        
        if not UserFavorite.objects.filter(user_profile=user_profile, restaurant_profile=restaurant).exists():
            
            favorite = UserFavorite.objects.create(user_profile=user_profile, restaurant_profile=restaurant)
            favorite.save()
            messages.success(request, "Restaurant added to your favorites.")
        else:
            messages.info(request, "Restaurant is already in your favorites.")
    
    elif favorite_type == 'menu_item':
       
        menu_item = get_object_or_404(MenuItem, id=favorite_id)
        restaurant = menu_item.profile  
        
       
        favorite = UserFavorite.objects.filter(user_profile=user_profile, restaurant_profile=restaurant).first()
        if favorite:
            if not menu_item in favorite.menu_items.all():
                favorite.menu_items.add(menu_item)
                messages.success(request, "Menu item added to your favorites.")
            else:
                messages.info(request, "Menu item is already in your favorites.")
        else:
            
            favorite = UserFavorite.objects.create(user_profile=user_profile, restaurant_profile=restaurant)
            favorite.menu_items.add(menu_item)
            favorite.save()
            messages.success(request, "Menu item added to your favorites.")
    
    elif favorite_type == 'special_deal':
        
        special_deal = get_object_or_404(special_deals, id=favorite_id)
        restaurant = special_deal.profile  
        
        
        favorite = UserFavorite.objects.filter(user_profile=user_profile, restaurant_profile=restaurant).first()
        if favorite:
            if not special_deal in favorite.special_deals.all():
                favorite.special_deals.add(special_deal)
                messages.success(request, "Special deal added to your favorites.")
            else:
                messages.info(request, "Special deal is already in your favorites.")
        else:
            
            favorite = UserFavorite.objects.create(user_profile=user_profile, restaurant_profile=restaurant)
            favorite.special_deals.add(special_deal)
            favorite.save()
            messages.success(request, "Special deal added to your favorites.")
    
    else:
        messages.error(request, "Invalid type of favorite.")

    
    return redirect('user:favorites')




@login_required
def remove_from_favorites(request, favorite_id, favorite_type):
    user_profile = request.user.user_profile

    if favorite_type == 'restaurant':
        # Remove the restaurant from the favorites list
        favorite = UserFavorite.objects.filter(user_profile=user_profile, restaurant_profile__id=favorite_id).first()
        if favorite:
            favorite.delete()
            message = "Restaurant removed from your favorites."
        else:
            message = "Restaurant was not in your favorites."
    
    elif favorite_type == 'menu_item':
        # Remove the menu item from the favorites list
        favorite = UserFavorite.objects.filter(user_profile=user_profile, menu_items__id=favorite_id).first()
        if favorite:
            favorite.menu_items.remove(MenuItem.objects.get(id=favorite_id))
            message = "Menu item removed from your favorites."
        else:
            message = "Menu item was not in your favorites."
    
    elif favorite_type == 'special_deal':
        # Remove the special deal from the favorites list
        favorite = UserFavorite.objects.filter(user_profile=user_profile, special_deals__id=favorite_id).first()
        if favorite:
            favorite.special_deals.remove(SpecialDeal.objects.get(id=favorite_id))
            message = "Special deal removed from your favorites."
        else:
            message = "Special deal was not in your favorites."

    return redirect('user:favorites')



@login_required
def user_favorites(request):
    user_profile = request.user.user_profile
    

    favorite_restaurants = UserFavorite.objects.filter(user_profile=user_profile, restaurant_profile__isnull=False)
    favorite_menu_items = UserFavorite.objects.filter(user_profile=user_profile, menu_items__isnull=False)
    favorite_special_deals = UserFavorite.objects.filter(user_profile=user_profile, special_deals__isnull=False)


    favorite_restaurants_data = []
    for favorite in favorite_restaurants:
        favorite_restaurants_data.append(favorite.restaurant_profile)

    favorite_menu_items_data = []
    for favorite in favorite_menu_items:
        favorite_menu_items_data.extend(favorite.menu_items.all())  

    favorite_special_deals_data = []
    for favorite in favorite_special_deals:
        favorite_special_deals_data.extend(favorite.special_deals.all())  

    return render(request, 'user/favorites.html', {
        'favorite_restaurants': favorite_restaurants_data,
        'favorite_menu_items': favorite_menu_items_data,
        'favorite_special_deals': favorite_special_deals_data
    })

