# admin.py

from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_number', 'address', 'image_preview')
    search_fields = ('user__username', 'contact_number')
    list_filter = ('user__is_active',)

    def image_preview(self, obj):
        """Display the profile image as a preview in the admin panel."""
        if obj.image:
            # Use a small inline base64 image for preview
            return (
                f'<img src="data:image/jpeg;base64,{obj.get_image_base64()}" '
                f'style="height: 50px; width: 50px; object-fit: cover;" />'
            )
        return "No Image"

    image_preview.allow_tags = True
    image_preview.short_description = 'Image Preview'

admin.site.register(Profile, ProfileAdmin)
