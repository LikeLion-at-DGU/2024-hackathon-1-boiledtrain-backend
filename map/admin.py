# admin.py
from django.contrib import admin
from .models import Category, Place

admin.site.register(Category)
admin.site.register(Place)
