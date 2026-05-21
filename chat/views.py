from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Room, Membership, Message
from .serializers import UserSerializer, RegisterSerializer, RoomSerializer, MessageSerializer


# ─── AUTH ───────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.exclude(id=request.user.id)
    return Response(UserSerializer(users, many=True).data)


# ─── ROOMS ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rooms(request):
    rooms = request.user.rooms.all()
    return Response(RoomSerializer(rooms, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_dm(request):
    target_id = request.data.get('user_id')
    try:
        target = User.objects.get(id=target_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    # Check if DM already exists between these two users
    existing = Room.objects.filter(room_type='dm', members=request.user).filter(members=target)
    if existing.exists():
        return Response(RoomSerializer(existing.first()).data)

    room = Room.objects.create(room_type='dm', created_by=request.user)
    Membership.objects.create(user=request.user, room=room)
    Membership.objects.create(user=target, room=room)
    return Response(RoomSerializer(room).data, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = request.data.get('name')
    member_ids = request.data.get('members', [])
    if not name:
        return Response({'error': 'Group name required'}, status=400)

    room = Room.objects.create(room_type='group', name=name, created_by=request.user)
    Membership.objects.create(user=request.user, room=room, is_admin=True)

    for uid in member_ids:
        try:
            user = User.objects.get(id=uid)
            Membership.objects.create(user=user, room=room)
        except User.DoesNotExist:
            pass

    return Response(RoomSerializer(room).data, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member(request, room_id):
    try:
        room = Room.objects.get(id=room_id, room_type='group')
    except Room.DoesNotExist:
        return Response({'error': 'Group not found'}, status=404)

    user_id = request.data.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    Membership.objects.get_or_create(user=user, room=room)
    return Response({'message': f'{user.username} added to group'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member(request, room_id, user_id):
    try:
        room = Room.objects.get(id=room_id, room_type='group')
        membership = Membership.objects.get(user_id=user_id, room=room)
        membership.delete()
        return Response({'message': 'Member removed'})
    except (Room.DoesNotExist, Membership.DoesNotExist):
        return Response({'error': 'Not found'}, status=404)


# ─── MESSAGES ───────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=404)

    if not room.members.filter(id=request.user.id).exists():
        return Response({'error': 'Not a member'}, status=403)

    messages = Message.objects.filter(room=room).order_by('timestamp')
    return Response(MessageSerializer(messages, many=True).data)