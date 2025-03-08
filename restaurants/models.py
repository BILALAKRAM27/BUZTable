# restaurants/models.py

from django.db import models
from django.contrib.auth.models import User
import base64



class DeliveryPartner(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=255)
    image = models.BinaryField(blank=True, null=True)  # Storing image as binary data (BLOB)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    site = models.URLField(max_length=500, blank=True, null=True)  # URL field for the menu link
    address_link = models.URLField(max_length=500, blank=True, null=True) # URL field for the address link
    pet_friendly = models.BooleanField(default=False)
    WiFi = models.BooleanField(default=False)
    delivery_partners = models.ManyToManyField('DeliveryPartner')
    is_restaurant = models.BooleanField(default=True)



    def __str__(self):
        return self.restaurant_name 

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

class RestaurantDeliveryPartner(models.Model):
    restaurant = models.ForeignKey(Profile, on_delete=models.CASCADE)
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('restaurant', 'delivery_partner'),)
    
    def __str__(self):
        return f"{self.restaurant.restaurant_name} - {self.delivery_partner.name}"




class MenuItem(models.Model):
    profile = models.ForeignKey(Profile, related_name="menu_items", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False)
    ingredients = models.TextField(blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_count = models.PositiveIntegerField(default=0)  # To track how many times the dish has been ordered
    item_image = models.BinaryField(blank=True, null=True, default=None)  # Storing image as binary data (BLOB)

    def __str__(self):
        return self.name

    def set_image(self, data):
        """Set the image field as raw binary data"""
        self.item_image = data

    def get_image(self):
        """Get the raw binary image data"""
        return self.item_image

    def get_image_base64(self):
        """Returns the base64 string to display in templates"""
        if self.item_image:
            return base64.b64encode(self.item_image).decode('utf-8')
        return None

    image_data = property(get_image_base64)

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        
class special_deals(models.Model):
    profile = models.ForeignKey(Profile, related_name="special_deal", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False)
    items = models.TextField(blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_count = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField(blank=True, null=True, default=None)
    end_date = models.DateTimeField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    deal_image = models.BinaryField(blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    def set_image(self, data):
        """Set the image field as raw binary data"""
        self.deal_image = data

    def get_image(self):
        """Get the raw binary image data"""
        return self.deal_image

    def get_image_base64(self):
        """Returns the base64 string to display in templates"""
        if self.deal_image:
            return base64.b64encode(self.deal_image).decode('utf-8')
        return None

    image_data = property(get_image_base64)

    class Meta:
        verbose_name = "Special Deal"
        verbose_name_plural = "Special Deals"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who is reviewing
    restaurant = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Restaurant being reviewed
    rating = models.PositiveIntegerField()  # Rating out of 5
    comment = models.TextField()  # Comment/Review text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the review was made

    def __str__(self):
        return f"Review by {self.user.username} for {self.restaurant.restaurant_name}"

    class Meta:
        unique_together = ['user', 'restaurant']  # Ensures a user can only review a restaurant once

from uuid import uuid4  

class Order(models.Model):
    STATUS_CHOICES = [
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='preparing')
    full_name = models.CharField(max_length=255)
    address = models.TextField(default=None)
    phone_number = models.CharField(max_length=20)
    delivery_method = models.CharField(max_length=50, default='None',choices=[('takeout', 'Takeout'), ('delivery', 'Delivery')])
    delivery_partner = models.ForeignKey(DeliveryPartner, null=True, blank=True, on_delete=models.SET_NULL)

    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=255, default=uuid4, blank=True)  # Provide a default unique payment ID

    def total_price(self):
        total = 0
        for item_quantity in self.menuitemquantity_set.all():
            total += item_quantity.menu_item.price * item_quantity.quantity
        for deal_quantity in self.specialdealquantity_set.all():
            total += deal_quantity.special_deal.price * deal_quantity.quantity
        return total

    def mark_as_paid(self, payment_id):
        self.payment_status = 'paid'
        self.payment_id = payment_id
        self.save()

    def __str__(self):
        items = ', '.join([str(iq.menu_item.name) for iq in self.menuitemquantity_set.all()])
        deals = ', '.join([str(dq.special_deal.name) for dq in self.specialdealquantity_set.all()])
        return f"Order by {self.user.username} for items: {items}, deals: {deals}"

class MenuItemQuantity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} (x{self.quantity})"

class SpecialDealQuantity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    special_deal = models.ForeignKey(special_deals, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.special_deal.name} (x{self.quantity})"
    

class RestaurantCategory(models.Model):
    profile = models.ForeignKey(Profile, related_name="categories", on_delete=models.CASCADE,default=None)
    category_name = models.CharField(max_length=255,choices=[
        ('Italian', 'italian'),
        ('Chinese', 'chinese'),
        ('Mexican', 'mexican'),
        ('Indian', 'indian'),
        ('Japanese', 'japanese'),
        ('Mediterranean', 'mediterranean'),
        ('French', 'french'),
        ('American', 'american'),
        ('Thai', 'thai'),
        ('Spanish', 'spanish'),
    ])

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Restaurant Category"
        verbose_name_plural = "Restaurant Categories"

class RestaurantSchedule(models.Model):
    profile = models.ForeignKey(Profile, related_name="schedules", on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=9, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ])
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return f"{self.profile.restaurant_name} - {self.day_of_week}"

    class Meta:
        verbose_name = "Restaurant Schedule"
        verbose_name_plural = "Restaurant Schedules"

class Promotion(models.Model):
    profile = models.ForeignKey(Profile, related_name="promotions", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Comment(models.Model):
    profile = models.ForeignKey(Profile, related_name='comments', on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.profile.user.username}"

## reservation
class Table(models.Model):
    # Associate the table with the restaurant profile (Profile model)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='tables')
    
    max_guests = models.IntegerField()  # Maximum number of guests per table
    available = models.BooleanField(default=True)  # Whether the table is available
    # Optionally, you can add fields for table number, location, etc.

    def __str__(self):
        return f"Table for {self.max_guests} at {self.profile.restaurant_name}"
    
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user making the reservation
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')  # The table being reserved
    restaurant = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reservations_as_restaurant',default=1)
    reservation_date = models.DateTimeField()  # The date and time for the reservation
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
        default='pending'
    )  # The status of the reservation

    def __str__(self):
        return f"Reservation by {self.user.username} for {self.num_guests} guests on {self.reservation_date}"
    
class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Store amount as decimal
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, default='stripe')
    transaction_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_status}"


class Notification(models.Model):
    restaurant = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    reservation = models.ForeignKey(Reservation, null=True, blank=True, on_delete=models.SET_NULL)  # Add reservation field
    
    def __str__(self):
        return self.message    
    
import random
import string

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    delivery_partner = models.ForeignKey('DeliveryPartner', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'Delivery {self.tracking_number} - {self.get_status_display()}'

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)

    def generate_tracking_number(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


