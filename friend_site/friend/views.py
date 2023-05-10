from rest_framework import generics, status
from rest_framework.response import Response
from .models import Friends, FriendRequest
from .serializers import FriendsSerializer, FriendRequestSerializer


class FriendsListCreateAPIView(generics.ListCreateAPIView):
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer


class FriendsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer


class FriendRequestListCreateAPIView(generics.ListCreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sender = serializer.validated_data['sender']
        receiver = serializer.validated_data['receiver']

        if sender == receiver:
            return Response({'error': 'You cannot send a friend request to yourself.'},
                            status=status.HTTP_400_BAD_REQUEST)

        friend_request, created = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver)

        if not created:
            if friend_request.is_active:
                return Response({'error': 'You already sent a friend request to this user.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                friend_request.is_active = True
                friend_request.save()
                return Response({'success': 'Friend request has been sent again.'}, status=status.HTTP_200_OK)

        return Response({'success': 'Friend request has been sent.'}, status=status.HTTP_201_CREATED)


class FriendRequestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if not instance.is_active:
            return Response({'error': 'This friend request has already been handled.'},
                            status=status.HTTP_400_BAD_REQUEST)

        instance.is_active = False
        instance.save()

        if 'accepted' in request.data and request.data['accepted'] == True:
            instance.accept()
            return Response({'success': 'Friend request has been accepted.'}, status=status.HTTP_200_OK)
        else:
            instance.decline()
            return Response({'success': 'Friend request has been declined.'}, status=status.HTTP_200_OK)
