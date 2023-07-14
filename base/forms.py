from django.forms import ModelForm
from .models import Room
from .models import User

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'topic', 'description']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']