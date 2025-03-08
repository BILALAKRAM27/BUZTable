from django.urls import path
from . import views


app_name = 'restaurants'

urlpatterns = [
    path('', views.home, name='home'),
    path('restaurant_register/', views.register_view, name='register'),
    path('restaurant_login/', views.login_view, name='restaurant_login'),
    path('logout/', views.restaurant_logout, name='restaurant_logout'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('about_us/', views.about_us, name='about_us'),
    path('read_more/', views.read_more, name='read_more'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    #Profile
    path('restaurant_profile/', views.profile_view, name='profile'),
    path('restaurant_profile/update/', views.update_profile_view, name='update_profile'),
    path('restaurant_profile/delete/', views.delete_profile_view, name='delete_profile'),
    path('restaurant_profile/menu/add/', views.add_menu_item, name='add_menu_item'),
    path('restaurant_profile/menu/update/<int:menu_item_id>/', views.update_menu_item, name='update_menu_item'),
    path('restaurant_profile/menu/delete/<int:menu_item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('restaurants/', views.restaurant_list_view, name='restaurant_list'), 
    path('restaurant/<int:id>/reviews/', views.get_reviews, name='get_reviews'),
    path('restaurant/<int:id>/', views.restaurant_detail_view, name='restaurant_detail'),
    path('restaurant_dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    #Menu Item
    path('menu_item/add/', views.add_menu_item, name='add_menu_item'),
    path('menu_item/update/<int:menu_item_id>/', views.update_menu_item, name='update_menu_item'),
    path('menu_item/delete/<int:menu_item_id>/', views.delete_menu_item, name='delete_menu_item'),
    #Special Deals
    path('special_deal/add/', views.add_special_deal, name='add_special_deal'),
    path('special_deal/update/<int:special_deal_id>/', views.update_special_deal, name='update_special_deal'),
    path('special_deal/delete/<int:special_deal_id>/', views.delete_special_deal, name='delete_special_deal'),
    #schedules    
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/add/', views.add_schedule, name='add_schedule'),
    path('schedules/<int:schedule_id>/edit/', views.update_schedule, name='update_schedule'),
    #categories
    path('add_category/', views.add_category, name='add_category'),
    path('categories/', views.category_list, name='category_list'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    #dashboard
    path('restaurant_dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('manage_orders/', views.manage_orders, name='manage_orders'),
    path('manage_promotions/', views.manage_promotions, name='manage_promotions'),
    path('manage_reviews/', views.manage_reviews, name='manage_reviews'),
    #promotions
    path('manage_promotions/', views.manage_promotions, name='manage_promotions'),
    path('promotions/create/', views.create_promotion, name='create_promotion'),
    path('promotions/edit/<int:pk>/', views.edit_promotion, name='edit_promotion'),
    path('promotions/delete/<int:pk>/', views.delete_promotion, name='delete_promotion'),
    #review
    path('profile/<int:profile_id>/comment/', views.comment, name='comment'),
    # Reservation
    path('add_table/', views.add_table, name='add_table'),
    path('manage_tables/', views.manage_tables, name='manage_tables'),  # New URL for managing tables
    path('delete_table/<int:table_id>/', views.delete_table, name='delete_table'),  # URL for deleting a table
    path('table/<int:table_id>/toggle-availability/', views.toggle_table_availability, name='update_table'),
    path('error/',views.some_error_page_view,name='some_error_page'),
    path('reservation/<int:reservation_id>/update-status/', views.update_reservation_status, name='update_reservation_status'),
    
    # Payment
    path('payments/<str:total_price>/', views.payment_view, name='payments'),
    path('payment/success/', views.payment_success, name='payment_success'),  # Success view
    path('most-ordered/', views.most_ordered, name='orderedtime'),

    # Delivery Partner Management
    path('restaurant/<int:restaurant_id>/delivery-partners/', views.manage_delivery_partners, name='manage_delivery_partners'),
    path('restaurant/<int:restaurant_id>/delivery-partner/add/', views.add_delivery_partner, name='add_delivery_partner'),
    path('restaurant/<int:restaurant_id>/delivery-partner/update/<int:partner_id>/', views.update_delivery_partner, name='update_delivery_partner'),
    path('restaurant/<int:restaurant_id>/delivery-partner/remove/<int:partner_id>/', views.remove_delivery_partner, name='remove_delivery_partner'),

]
