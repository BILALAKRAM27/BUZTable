from django.urls import path
from .views import (
    home, register_viu, profile_view, update_profile_view, delete_profile_view, 
    login_view, user_logout_view, user_dashboard
)
from . import views
from django.contrib.auth import views as auth_views


app_name = 'user'

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_viu, name='user_register'),
    path('profile/', profile_view, name='uprofile'),
    path('profile/update/', update_profile_view, name='update_user_profile'),
    path('profile/delete/', delete_profile_view, name='delete_user_profile'),
    path('user_login/', login_view, name='user_login'),
    path('logout/', user_logout_view, name='user_logout'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('user/password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('user/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('user/reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('user/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<str:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # add to cart
    path('cart/add/<str:item_type>/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:item_type>/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # for checkout
    path('checkout/', views.checkout, name='checkout'),
    path('order_success/', views.order_success, name='order_success'),
    # reservation
    path('make_reservation/', views.make_reservation, name='make_reservation'),
    path('cancel-reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    # notification
    path('delete-notifications/', views.delete_all_notifications, name='delete_all_notifications'),
    #track_deliveries
    path('track-delivery/<str:tracking_number>/', views.track_delivery, name='track_delivery'),
    #table
    path('get-tables/', views.get_tables, name='get_tables'),
    # favourites
    path('comment/<int:profile_id>/', views.comment, name='comment'),
    path('add_to_favorites/<int:favorite_id>/<str:favorite_type>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:favorite_id>/<str:favorite_type>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.user_favorites, name='favorites'),
    
]
