# restaurants/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from restaurants.models import MenuItem,Reservation,Table # Import MenuItem model
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    profile_picture = forms.FileField(required=False)  # Profile picture field

    class Meta:
        model = Profile
        fields = ['profile_picture', 'contact_number', 'address']






class ShippingForm(forms.Form):
    menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.none(), label="Menu Item")
    quantity = forms.IntegerField(min_value=1, label="Quantity")
    full_name = forms.CharField(max_length=255, label="Full Name")
    address = forms.CharField(widget=forms.Textarea, label="Shipping Address")
    phone_number = forms.CharField(max_length=15, label="Phone Number")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        available_menu_items = kwargs.pop('available_menu_items', None)  # Get the available menu items
        super().__init__(*args, **kwargs)
        
        if user:
            # Pre-populate the fields with user's profile data using related_name 'user_profile'
            profile = user.user_profile if hasattr(user, 'user_profile') else None
            if profile:
                self.fields['full_name'].initial = user.username  # Username can be used as full name
                self.fields['address'].initial = profile.address
                self.fields['phone_number'].initial = profile.contact_number
        
        if available_menu_items:
            # Set the queryset for menu_item to only the items in the cart
            self.fields['menu_item'].queryset = available_menu_items

from restaurants.models import Profile as RestaurantProfile  # Import the restaurant profile model using alias

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['restaurant', 'table', 'reservation_date']
        widgets = {
            'reservation_date': forms.DateTimeInput(attrs={
                'type': 'text',
                'class': 'datetimepicker',
                'placeholder': 'Select date and time',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Query the restaurant profile model and display restaurant names
        self.fields['restaurant'].queryset = RestaurantProfile.objects.filter(is_restaurant=True)  # Query restaurants only
        
        # Ensure that table options are updated based on the selected restaurant
        if 'restaurant' in self.data:
            try:
                restaurant_id = int(self.data.get('restaurant'))
                self.fields['table'].queryset = Table.objects.filter(profile_id=restaurant_id, available=True)
            except (ValueError, TypeError):
                pass
        else:
            self.fields['table'].queryset = Table.objects.none()



# Password reset form for requesting a password reset email
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address'
        })
    )

# Password reset confirmation form for setting a new password
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        help_text=_("Your password must be at least 8 characters long."),
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput,
    )

from django import forms
from restaurants.models import Comment

class CommentForm(forms.ModelForm):
    # Define the fields for the comment form
    class Meta:
        model = Comment
        fields = ['body']  # Only allow the body of the comment to be entered by the user

    def __init__(self, *args, **kwargs):
        # Allow passing the user and profile as extra arguments
        self.user = kwargs.pop('user', None)
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

    def clean_body(self):
        # Ensure the comment body isn't empty
        body = self.cleaned_data.get('body')
        if not body.strip():
            raise forms.ValidationError("Comment body cannot be empty.")
        return body

    def save(self, commit=True):
        # Create the comment and associate it with the current user and profile
        comment = super().save(commit=False)
        if self.user:
            comment.user = self.user
        if self.profile:
            comment.profile = self.profile
        if commit:
            comment.save()
        return comment
    
# user/forms.py
from django import forms
from .models import UserFavorite
from restaurants.models import MenuItem, special_deals

class UserFavoriteForm(forms.ModelForm):
    class Meta:
        model = UserFavorite
        fields = ['user_profile', 'restaurant_profile', 'menu_items', 'special_deals']
        widgets = {
            'menu_items': forms.CheckboxSelectMultiple,
            'special_deals': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can add customizations like setting the queryset of choices here if needed
        self.fields['menu_items'].queryset = MenuItem.objects.all()
        self.fields['special_deals'].queryset = special_deals.objects.all()

