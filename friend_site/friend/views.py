from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from user.models import User
from friend.models import FriendRequest, Friends
from friend.serializers import FriendRequestSerializer, FriendsSerializer


class FriendRequestView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def create(self, request, *args, **kwargs):
        sender = request.user
        receiver = User.objects.get(pk=request.data.get('receiver'))
        if receiver != sender and not Friends.objects.filter(user=sender, friends=receiver).exists():
            friend_request, created = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver)
            if created:
                return Response({'status': 'Friend request sent'}, status=status.HTTP_201_CREATED)
            elif not friend_request.is_active:
                friend_request.is_active = True
                friend_request.save()
                return Response({'status': 'Friend request sent again'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'Friend request already sent'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


class FriendRequestListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, is_active=True)


class FriendRequestAcceptRejectView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receiver == request.user:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if instance.is_active:
                Friends.objects.get_or_create(user=instance.sender).friends.add(instance.receiver)
                Friends.objects.get_or_create(user=instance.receiver).friends.add(instance.sender)
            return Response(serializer.data)
        else:
            return Response({'status': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


class FriendsListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendsSerializer

    def get_queryset(self):
        user = self.request.user
        return Friends.objects.filter(user=user)


class FriendStatusView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def get_object(self):
        user1 = self.request.user
        user2 = User.objects.get(pk=self.kwargs.get('pk'))
        if user1 == user2:
            return None
        if Friends.objects.filter(user=user1, friends=user2).exists():
            return {'status': 'Already Friends'}
        if FriendRequest.objects.filter(sender=user1, receiver=user2, is_active=True).exists():
            return {'status': 'Outgoing Friend Request'}
        if FriendRequest.objects.filter(sender=user2, receiver=user1, is_active=True).exists():
            return {'status': 'Incoming Friend Request'}
        return {'status': 'No Friend Request or Friendship'}


class FriendsRemoveView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendsSerializer

    def get_object(self):
        user = self.request.user
        friend = User.objects.get(pk=self.kwargs.get('pk'))
        return Friends.objects.get(user=user, friends=friend)

    def delete(self, request, *args, **kwargs):
        friend_relationship = self.get_object()
        friend_relationship.unfriend(remove_friend=friend_relationship.friends.first())
        return Response(status=status.HTTP_204_NO_CONTENT)

