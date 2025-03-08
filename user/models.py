# user/models.py

from django.db import models
from django.contrib.auth.models import User
import base64
from restaurants.models import MenuItem ,special_deals
from restaurants.models import Profile as RestaurantProfile

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="user_profile")
    image = models.BinaryField(blank=True, null=True)  # Storing image as binary data (BLOB)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_restaurant = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.user.username} Profile'

    def set_image(self, data):
        """Set the image field as raw binary data"""
        self.image = data

    def get_image(self):
        """Get the raw binary image data"""
        return self.image

    def get_image_base64(self):
        """Returns the base64 string to display in templates"""
        if self.image:
            return base64.b64encode(self.image).decode('utf-8')
        return None

    image_data = property(get_image_base64)
    

class UserFavorite(models.Model):
    user_profile = models.ForeignKey('user.Profile', on_delete=models.CASCADE, related_name='user_favorites')
    restaurant_profile = models.ForeignKey(RestaurantProfile, on_delete=models.CASCADE, related_name='favorites')
    added_on = models.DateTimeField(auto_now_add=True)

    # Adding the related fields for menu items and special deals
    menu_items = models.ManyToManyField(MenuItem, blank=True)
    special_deals = models.ManyToManyField(special_deals, blank=True)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.restaurant_profile.restaurant_name}"

