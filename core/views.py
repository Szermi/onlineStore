from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Item, OrderItem, Order

from django.contrib import messages
# Create your views here.


class HomeView(ListView):
    model = Item
    template_name = "home.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

def checkout(request):
    context = {
        'items': Item.objects.all()
    }

    return render(request, "checkout.html", context)


def product(request):
    context = {
        'items': Item.objects.all()
    }

    return render(request, "product.html", context)


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        #check if item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Liczba produktów została zaktualizowana.")
            return redirect("core:product", slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, "Produkt został dodany do twojego koszyka.")
            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Produkt został dodany do twojego koszyka.")
        return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get_or_create(
                item=item,
                user=request.user,
                ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "Produkt został usunięty z twojego koszyka.")
            return redirect("core:product", slug=slug)
        else:
            messages.info(request, "Produkt nie był w twoim koszyku.")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Nie masz aktywnego zamówenia.")
        return redirect("core:product", slug=slug)
