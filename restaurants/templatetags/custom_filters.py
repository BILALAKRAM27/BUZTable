# custom_filters.py
from django import template
from restaurants.models import RestaurantSchedule
import base64

register = template.Library()

@register.filter
def get_day_schedule(schedules, day_of_week):
    return schedules.filter(day_of_week=day_of_week).first()
@register.filter
def multiply(value, arg):
    return value * arg
@register.filter(name='range')
def filter_range(value):
    """
    Returns a range object based on the given value.
    Useful for generating a sequence of numbers in templates.
    """
    try:
        value = int(value)
    except ValueError:
        return []
    return range(value)
# In your Profile model, `get_image_base64` method
def get_image_base64(self):
    """Returns the base64 string to display in templates"""
    if self.image:
        return base64.b64encode(self.image).decode('utf-8')
    return None

@register.filter
def last_message(messages):
    return messages[-1] if messages else None