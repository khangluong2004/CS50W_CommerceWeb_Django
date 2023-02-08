from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.utils.safestring import mark_safe

from .models import User, Listing, Bids, Comment, Watchlist

#Active Listing
def index(request):
    try:
        items = Listing.objects.filter(active = True)
    except Listing.DoesNotExist:
        items = []
    return render(request, "auctions/index.html", {
        "items": items
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

#Create Listing views
class ListForm(forms.Form):
    title = forms.CharField(max_length = 100, label = mark_safe("<p> Title: <p>"), label_suffix="", widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label = mark_safe("<p> Description: <p>"), label_suffix="", widget=forms.Textarea(attrs={'class': 'form-control'}))
    start_bidding = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    url_img = forms.CharField(empty_value="", widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.CharField(empty_value="", widget=forms.TextInput(attrs={'class': 'form-control'}))

def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        #Obtain value from form
        form = ListForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            start_bidding = int(form.cleaned_data["start_bidding"])
            url_img = form.cleaned_data["url_img"]
            category = form.cleaned_data["category"]
            owner = User.objects.get(pk = request.user.id)
            #Add data to database
            listing = Listing(owner_id = owner, winner_id = owner, title = title.capitalize(), description = description, start_bid = start_bidding, current_bid = start_bidding, url_img = url_img, category = category, active = True)
            listing.save()
    #Return template
    return render(request, "auctions/create_listing.html", {
        "form": ListForm()
    })
    
#Listing page view
#Listing page form class
class BidForm(forms.Form):
    bid = forms.IntegerField(label = mark_safe("<p> Bid: <p>"), label_suffix="", min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    comment = forms.CharField(empty_value="", label = mark_safe("<p> Comment: <p>"), label_suffix="", widget=forms.Textarea(attrs={'class': 'form-control'}), required = False)

def listing_page(request, id):
    message = ""
    actual_owner = False
    won = False
    item = Listing.objects.get(pk = id)
    exist = False
    if request.user.is_authenticated:
        user = User.objects.get(pk = request.user.id)
        if request.user == item.owner_id:
            actual_owner = True
        if item.active == False and item.winner_id == request.user:
            won = True
        watch_check = Watchlist.objects.filter(watcher_id = request.user, watched_listing_id = item)
        if len(watch_check) == 0:
            exist = False
        else:
            exist = True
        if request.method == "POST":
            form = BidForm(request.POST)
            if form.is_valid():
                bid = int(form.cleaned_data["bid"])
                comment = form.cleaned_data["comment"]
                start_bid = item.start_bid
                current_bid = item.current_bid
                if bid < start_bid or bid <= current_bid:
                    message = "Invalid bid. The current bid is higher."
                else:
                    #Update the Listing table
                    item.current_bid = bid  
                    item.save()
                    #Update the Bid table
                    check = Bids.objects.filter(bidder_id = user, bid_listing_id = item)
                    if len(check) == 0:
                        new_bid = Bids(bidder_id = user, bid_listing_id = item, bid_money = bid)
                        new_bid.save()
                    else:
                        old_bid = Bids.objects.get(bidder_id = user, bid_listing_id = item)
                        old_bid.bid_money = bid
                        old_bid.save()
                    #Update the Comments table
                    if comment != "":
                        new_comment = Comment(commentor_id = user, comment_listing_id = item, comments = comment)
                        new_comment.save()
    
    count = len(Bids.objects.filter(bid_listing_id = item))
    comments = Comment.objects.filter(comment_listing_id = item)
    
    return render(request, "auctions/listing_page.html", {
        "message": message,
        "item": item,
        "count": count,
        "comment_list": comments,
        "actual_owner": actual_owner,
        "won": won,
        "watch_exist": exist,
        "form": BidForm()
    })

#Closing a listing
def close(request, id):
    item = Listing.objects.get(pk = id)
    bid = item.current_bid
    highest_bidder = Bids.objects.get(bid_money = bid, bid_listing_id = item).bidder_id
    item.winner_id = highest_bidder
    item.active = False
    item.save()
    return HttpResponseRedirect(reverse("listing_page", args=(id,)))

#Adding to Watchlist
def add_watch(request, method, id):
    item = Listing.objects.get(pk = id)
    if method == "remove":
        watch = Watchlist.objects.filter(watcher_id = request.user, watched_listing_id = item)
        watch.delete()
    else:
        watch = Watchlist(watcher_id = request.user, watched_listing_id = item)
        watch.save()
    return HttpResponseRedirect(reverse("listing_page", args=(id,)))

#Watchlist view
def watchlist(request):
    pre_items = Watchlist.objects.filter(watcher_id=request.user)
    items = []
    for pre_item in pre_items:
        items.append(pre_item.watched_listing_id)
    return render(request, "auctions/watchlist.html", {
        "items": items
    })

#Category view
def category(request):
    categories = set(Listing.objects.all().values_list("category", flat=True))
    return render(request, "auctions/category.html", {
        "categories": categories
    })

#Category listing view
def category_list(request, cat):
    items = Listing.objects.filter(active=True, category=cat)
    return render(request, "auctions/category_listing.html", {
        "items": items
    })    
    