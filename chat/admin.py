from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Room, Membership, Message

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'is_online', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('profile_picture', 'is_online')}),
    )

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'room_type', 'created_by', 'created_at']

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'is_admin', 'joined_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'content', 'timestamp']