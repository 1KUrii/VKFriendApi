from django.db import models
from user.models import User


class Friends(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_friend_list")
    friends = models.ManyToManyField(
        User,
        blank=True,
        related_name='friends',
    )

    def __str__(self):
        return self.user.username

    def add_friend(self, user):
        if not user in self.friends.all():
            self.friends.add(user)
            self.save()

    def remove_friend(self, user):
        if user in self.friends.all():
            self.friends.remove(user)

    def unfriend(self, remove_friend):
        remove_friends_list = self
        remove_friends_list.remove_friend(remove_friend)
        friend_list = Friends.objects.get(user=remove_friend)
        friend_list.remove_friend(self.user)


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=True, null=False, default=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        receiver_friend_list = Friends.objects.get(user=self.receiver)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list = Friends.objects.get(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()

                # Check if there is a reciprocal friend request from the receiver to the sender
                reciprocal_request = FriendRequest.objects.filter(sender=self.receiver, receiver=self.sender,
                                                                  is_active=True).first()
                if reciprocal_request:
                    reciprocal_request.accept()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()
