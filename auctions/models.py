from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    winner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "winner")
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length =700, blank=False)
    start_bid = models.PositiveIntegerField(blank=False)
    current_bid = models.PositiveIntegerField(default = 0, blank = False)
    url_img = models.CharField(max_length = 5000, blank = True)
    category = models.CharField(max_length=50, blank = True)
    active = models.BooleanField(default = True)
    
    def __str__(self):
        return f"{self.title} (start bid: {self.start_bid}; current bid: {self.current_bid}; active: {self.active})"

class Bids(models.Model):
    bidder_id = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "buyer")
    bid_listing_id = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name = "blisting")
    bid_money = models.PositiveIntegerField(blank = False)
    
    def __str__(self):
        return f"{self.bidder_id.username}: {self.bid_listing_id} for {self.bid_money}"
    
class Comment(models.Model):
    commentor_id = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "commentor")
    comment_listing_id = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name = "clisting")
    comments = models.CharField(max_length = 300, blank = False)
    
    def __str__(self):
        return f"{self.commentor_id} commented {self.comments} for {self.comment_listing_id}"

class Watchlist(models.Model):
    watcher_id = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "watcher")
    watched_listing_id = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name = "wlisting")
    