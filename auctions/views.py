from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import F
from django.urls import reverse

from .models import User, Listing, Watchlist, Comment, Bid

categories = ["Electronics",
"Furniture",
"Home & Garden",
"Clothing & Accessories",
"Jewelry & Watches",
"Collectibles & Antiques",
"Art",
"Books & Media",
"Toys & Games",
"Sporting Goods",
"Musical Instruments",
"Automotive & Parts",
"Tools & Equipment",
"Appliances",
"Health & Beauty",
"Baby & Kids",
"Pet Supplies",
"Real Estate",
"Business & Industrial",
"Others and Miscellaneous"]

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        'listings': listings
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

def new_listing(request):
    if request.method == 'GET':
        return render(request, "auctions/new_listing.html",{
            "categories": categories
        })
    else:
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        image = request.POST.get("image")
        starting = request.POST.get("starting")
        poster = User.objects.get(id = request.POST.get("posted_by"))


        new = Listing(name=title, description = description, category = category, image = image, starting_price = starting, posted_by = poster)
        new.save()
        return HttpResponseRedirect(reverse ("index"))

def listing(request, id):
 
    item = Listing.objects.get(id = id)
    comments = Comment.objects.filter(listing = item)


    all = Bid.objects.filter(listing = item)
    pricenow = item.current_price
    winner = all.filter(amount = pricenow).first()

    if not winner:
        winnerID = None
    else:
        winnerID = winner.user.id


    return render(request, "auctions/listing.html", {
        "item":item,
        "comments": comments.order_by('-id'),
        "winner": winnerID
    })
def comment(request):
    if request.method == 'POST':

        action  = request.POST.get('comment')

        if action == 'add':
            comment =request.POST.get('remark')

            poster = User.objects.get(id = request.POST.get('poster'))
            item = Listing.objects.get(id = request.POST.get('listing'))

            new = Comment(remark = comment, user = poster, listing = item)
            new.save()

            messages.success(request, "Your comment has been added successfully!")
            return HttpResponseRedirect(reverse('listing', kwargs = {
                'id' : request.POST.get('listing')
            }))
        elif action == 'delete':
            comment = Comment.objects.get(id = request.POST.get('remark'))
            comment.delete()

            messages.success(request, "Your comment has been deleted successfully!")
            return HttpResponseRedirect(reverse('listing', kwargs = {
                'id' : request.POST.get('listing')
            }))


def watchlist(request):
    user = request.user
    if request.method == "GET":

        if user.is_authenticated:
            list = Watchlist.objects.filter(user = User.objects.get(id = user.id))

            if not list:
                return render(request, "auctions/watchlist.html", {
                "message": "Watchlist is empty."
            })

            return render(request, "auctions/watchlist.html", {
                "items": list.order_by('-id')
            })
        else:
            return render(request, "auctions/watchlist.html", {
                "message": "Please sign in to see your watchlist"
            })
    
    else:
        todo = request.POST.get("action")
        if todo == "delete":
            row = request.POST.get("toRemove")

            toremove = Watchlist.objects.get(id = row)
            toremove.delete()
            return HttpResponseRedirect(reverse('watchlist'))
        
        elif todo == 'add':
            item = request.POST.get("toAdd")
            realItem = Listing.objects.get(id = item)

            account = request.POST.get('user')

            if Watchlist.objects.filter(user = User.objects.get(id = account), item = realItem).exists():
                messages.error(request, "Item already in watchlist")
                return HttpResponseRedirect(reverse ("listing", kwargs = {
                    "id":item
                }))


            new = Watchlist(item = realItem, user = User.objects.get(id = account))
            new.save()
            return HttpResponseRedirect(reverse('watchlist'))
        
def bid(request):
    user = request.user

    #POST
    if request.method == "POST":
        todo = request.POST.get('action')

        if todo == 'put':
            amt = int(request.POST.get('bid_amt'))
            product = Listing.objects.get(id = request.POST.get('item'))
            bidder = User.objects.get(id = request.POST.get('bidder'))

            if product.current_price == None:
                product.current_price = product.starting_price

            if product.current_price > amt:
                messages.error(request, "Please enter amount greater than current price")
                return HttpResponseRedirect(reverse('listing', kwargs={
                    "id":request.POST.get('item')
                }))
            elif amt - product.current_price < 100:
                messages.error(request, "Minimum bid increment amount is $100.")
                return HttpResponseRedirect(reverse('listing', kwargs={
                    "id":request.POST.get('item')
                }))
            
            new = Bid(listing = product, user = bidder, amount = amt)
            new.save()

            Listing.objects.filter(id = request.POST.get('item')).update(current_price = amt)


            messages.success(request, "Bid placed successfully!")
            return HttpResponseRedirect(reverse("bid"))
        
        elif todo == 'delete':
            bidID = request.POST.get('BidId')

            remove = Bid.objects.get(id = bidID)
            remove.delete()

            messages.success(request, "Bid removed successfully!")
            return HttpResponseRedirect(reverse("bid"))
        elif todo == 'close':
            item = Listing.objects.get(id = request.POST.get('theID'))
            item.bidding = False
            item.save()


            messages.success(request, "Bidding closed successfully")
            return HttpResponseRedirect(reverse('listing', kwargs={
                "id": request.POST.get('theID')
            }))
    
    # GET
    if user.is_authenticated:
        bids = Bid.objects.filter(user = User.objects.get(id = user.id))
        other_bids = Bid.objects.exclude(user = User.objects.get(id = user.id))

        

        return render(request, "auctions/bids.html", {
            "bids": bids.order_by("-id"),
            "others": other_bids.order_by('-amount')
        })
    return render(request, "auctions/bids.html")


def category(request, name = None):
    if request.method == "GET":
        if name == None:
            items = Listing.objects.all()

            return render(request, "auctions/category.html",{
                "categories": categories,
                "items": items
            })
        
        objects = Listing.objects.filter(category = name)
        return render(request, "auctions/category_detail.html",{
            "items": objects,
            "category": name
        })