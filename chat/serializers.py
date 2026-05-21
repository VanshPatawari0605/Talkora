from rest_framework import serializers
from .models import User, Room, Membership, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'is_online']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'profile_picture']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            profile_picture=validated_data.get('profile_picture', None)
        )
        return user


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ['user', 'joined_at', 'is_admin']


class RoomSerializer(serializers.ModelSerializer):
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'room_type', 'members', 'created_at', 'last_message']

    def get_last_message(self, obj):
        last = obj.messages.last()
        if last:
            return {
                'content': last.content,
                'sender': last.sender.username,
                'timestamp': str(last.timestamp)
            }
        return None