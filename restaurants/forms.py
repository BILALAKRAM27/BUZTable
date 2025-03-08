# restaurants/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Review, MenuItem,special_deals,RestaurantCategory,RestaurantSchedule,Promotion,Comment,Table,DeliveryPartner



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
    profile_picture = forms.FileField(required=False)  

    class Meta:
        model = Profile
        fields = ['restaurant_name', 'description', 'contact_number', 'address', 'site', 'address_link', 
                  'pet_friendly','WiFi','is_restaurant']
        widgets = {
            'pet_friendly': forms.CheckboxInput(),
            'WiFi': forms.CheckboxInput(),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disabling the restaurant field since it's selected automatically in the view
        self.fields['rating'].widget = forms.NumberInput(attrs={'min': 1, 'max': 5})  # Rating out of 5

class MenuItemForm(forms.ModelForm):
    image_upload = forms.FileField(required=False)  # Add an ImageField to handle image upload

    class Meta:
        model = MenuItem
        fields = ['name', 'ingredients', 'price', 'image_upload']

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Handling the image conversion to binary if it's uploaded
        if self.cleaned_data['image_upload']:
            image = self.cleaned_data['image_upload']
            # Reading the uploaded image file and converting it to binary
            instance.item_image = image.read()  # Saving the image as binary data (BLOB)
        if commit:
            instance.save()
        return instance

class MenuItemUpdateForm(forms.ModelForm):
    image_upload = forms.FileField(required=False)  # Add an ImageField to handle image upload
    
    class Meta:
        model = MenuItem
        fields = ['name', 'ingredients', 'price', 'image_upload']

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Handling the image conversion to binary if it's uploaded
        if self.cleaned_data['image_upload']:
            image = self.cleaned_data['image_upload']
            # Reading the uploaded image file and converting it to binary
            instance.item_image = image.read()  # Saving the image as binary data (BLOB)
        if commit:
            instance.save()
        return instance

class special_dealsForm(forms.ModelForm):
    deal_image_upload = forms.FileField(required=False)

    class Meta:
        model = special_deals
        fields = ['name', 'items', 'price', 'deal_image_upload','start_date','end_date','is_active']
        widgets = {
            'is_active': forms.CheckboxInput(),
            'start_date':forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            'end_date':forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Handling the image conversion to binary if it's uploaded
        if self.cleaned_data.get('deal_image_upload'):
            image = self.cleaned_data['deal_image_upload']
            instance.deal_image = image.read()  # Saving the image as binary data (BLOB)
        if commit:
            instance.save()
        return instance

class special_dealsUpdateForm(forms.ModelForm):
    deal_image_upload = forms.FileField(required=False)

    class Meta:
        model = special_deals
        fields = ['name', 'items', 'price', 'deal_image_upload','start_date','end_date','is_active']
        widgets = {
            'is_active': forms.CheckboxInput(),
            'start_date':forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            'end_date':forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Handling the image conversion to binary if it's uploaded
        if self.cleaned_data.get('deal_image_upload'):
            image = self.cleaned_data['deal_image_upload']
            instance.deal_image = image.read()  # Saving the image as binary data (BLOB)
        if commit:
            instance.save()
        return instance


class RestaurantCategoryForm(forms.ModelForm):
    class Meta:
        model = RestaurantCategory
        fields = ['category_name']

class RestaurantScheduleForm(forms.ModelForm):
    class Meta:
        model = RestaurantSchedule
        fields = ['day_of_week', 'opening_time', 'closing_time']

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['name', 'description', 'price', 'active']  # Removed 'profile' from here

    def __init__(self, *args, **kwargs):
        # Pass the user to the form via kwargs
        user = kwargs.get('user', None)
        super().__init__(*args, **kwargs)
        
        # Automatically assign the profile to the logged-in user if available
        if user:
            self.instance.profile = user.profile  # Set the user's profile

        # Optionally, customize widgets here
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['active'].widget.attrs.update({'class': 'form-control'})


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.profile = kwargs.pop('profile', None)
        super(CommentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        comment = super().save(commit=False)

        if self.user:
            comment.user = self.user
        if self.profile:
            comment.profile = self.profile

        if commit:
            comment.save()
        return comment

## Reservation
class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['max_guests', 'available']





class DeliveryPartnerForm(forms.ModelForm):
    """
    Form for creating and updating Delivery Partner information.
    """
    class Meta:
        model = DeliveryPartner
        fields = ['name']

    def clean_contact_number(self):
        """
        Custom validation for the contact number field to ensure it's a valid format.
        """
        contact_number = self.cleaned_data.get('contact_number')
        if not contact_number.isdigit():
            raise forms.ValidationError("Contact number must contain only digits.")
        return contact_number
