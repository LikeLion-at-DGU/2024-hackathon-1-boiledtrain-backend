# admin.py
from django.contrib import admin
from .models import Course, Diary

admin.site.register(Course)
admin.site.register(Diary)
