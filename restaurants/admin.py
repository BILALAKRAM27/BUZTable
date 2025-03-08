from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, MenuItem, Review, Order, special_deals,MenuItemQuantity,SpecialDealQuantity,RestaurantCategory,RestaurantSchedule,Reservation,Payment,Promotion,Comment,Table

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant_name', 'contact_number', 'address', 'pet_friendly', 'WiFi', 'image_data')
    search_fields = ('user__username', 'restaurant_name', 'contact_number', 'address')
    list_filter = ('pet_friendly', 'WiFi')
    readonly_fields = ('image_data',)

    def image_data(self, obj):
        if obj.image:
            return format_html('<img src="data:image/png;base64,{}" width="100" height="100" />', obj.get_image_base64())
        return "No image"

    image_data.short_description = 'Image'

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile', 'price', 'order_count', 'image_data')
    search_fields = ('name', 'profile__restaurant_name')
    list_filter = ('profile__restaurant_name',)
    ordering = ('profile', 'name')
    readonly_fields = ('image_data',)

    def image_data(self, obj):
        if obj.item_image:
            return format_html('<img src="data:image/png;base64,{}" width="100" height="100" />', obj.get_image_base64())
        return "No image"

    image_data.short_description = 'Image'

class SpecialDealAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile', 'price', 'order_count')
    search_fields = ('name', 'profile__restaurant_name')
    list_filter = ('profile__restaurant_name',)
    ordering = ('profile', 'name')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'rating', 'created_at')
    search_fields = ('user__username', 'restaurant__restaurant_name', 'comment')
    list_filter = ('rating', 'created_at')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_date')
    list_filter = ('order_date',)
    ordering = ('order_date',)

class MenuItemQuantityAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity')
    search_fields = ('order__user__username', 'menu_item__name')

class SpecialDealQuantityAdmin(admin.ModelAdmin):
    list_display = ('order', 'special_deal', 'quantity')
    search_fields = ('order__user__username', 'special_deal__name')

class RestaurantCategoryAdmin(admin.ModelAdmin):
    list_display = ('profile', 'category_name')
    search_fields = ('profile__restaurant_name', 'category_name')

class RestaurantScheduleAdmin(admin.ModelAdmin):
    list_display = ('profile', 'day_of_week', 'opening_time', 'closing_time')
    search_fields = ('profile__restaurant_name', 'day_of_week')

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'price', 'active', 'created_at', 'updated_at')
    search_fields = ('profile__restaurant_name', 'name')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile', 'body', 'created_at', 'updated_at')
    search_fields = ('user__username', 'profile__restaurant_name', 'body')

class TableAdmin(admin.ModelAdmin):
    list_display = ('profile', 'max_guests', 'available')
    search_fields = ('profile__restaurant_name',)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'reservation_date', 'status')
    search_fields = ('user__username', 'table__profile__restaurant_name')
    list_filter = ('status',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(special_deals, SpecialDealAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(MenuItemQuantity, MenuItemQuantityAdmin)
admin.site.register(SpecialDealQuantity, SpecialDealQuantityAdmin)
admin.site.register(RestaurantCategory, RestaurantCategoryAdmin)
admin.site.register(RestaurantSchedule, RestaurantScheduleAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Reservation, ReservationAdmin)
