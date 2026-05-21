from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='pfps/', blank=True, null=True)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Room(models.Model):
    ROOM_TYPES = (
        ('dm', 'Direct Message'),
        ('group', 'Group'),
    )
    name = models.CharField(max_length=100, blank=True, null=True)  # only for groups
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    members = models.ManyToManyField(User, through='Membership', related_name='rooms')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"DM-{self.id}"


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)  # for group admins

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.user.username} in {self.room}"


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"

    class Meta:
        ordering = ['timestamp']