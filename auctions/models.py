from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Listing(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(default="")
    category = models.CharField(max_length=20, null=True)
    image = models.CharField(max_length=100, null=True)
    starting_price = models.IntegerField()
    current_price = models.IntegerField(null=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    bidding = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.current_price:
            self.current_price = self.starting_price

        super().save(*args, **kwargs)


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.listing.name}: {self.amount}"

class Comment(models.Model):
    remark = models.CharField(null=True, max_length= 200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.listing.name} | {self.user.username}: {self.remark}"

class Watchlist(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True )