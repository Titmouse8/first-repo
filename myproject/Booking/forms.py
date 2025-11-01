from django import forms
from .models import Booking, User



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['user_name', 'user_password', 'user_email']