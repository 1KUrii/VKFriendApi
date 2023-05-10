from rest_framework import serializers
from .models import Friends, FriendRequest


class FriendsSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    friends = serializers.SerializerMethodField()

    class Meta:
        model = Friends
        fields = ['id', 'user', 'friends']

    def get_friends(self, obj):
        friends = []
        for friend in obj.friends.all():
            friends.append(friend.username)
        return friends


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    receiver = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = FriendRequest
        fields = "__all__"
