from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.register),
    path('auth/login/', views.login),

    # Users
    path('api/users/', views.get_users),

    # Rooms
    path('api/rooms/', views.get_rooms),
    path('api/dm/', views.create_dm),
    path('api/group/', views.create_group),
    path('api/group/<int:room_id>/add/', views.add_member),
    path('api/group/<int:room_id>/remove/<int:user_id>/', views.remove_member),

    # Messages
    path('api/messages/<int:room_id>/', views.get_messages),
]