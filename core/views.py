from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Item, OrderItem, Order
from .forms import CheckoutForm
from django.contrib import messages


# Create your views here.


class HomeView(ListView):
    model = Item
    paginate_by = 2
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Nie masz aktywnego zamówienia")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class CheckoutView(View):
    def get(self, *args, **kwargs):
        #form
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        if form.is_valid():
            print("The form is valid")
            return redirect('core:checkout')


def product(request):
    context = {
        'items': Item.objects.all()
    }

    return render(request, "product.html", context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Liczba produktów została zaktualizowana.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Produkt został dodany do twojego koszyka.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Produkt został dodany do twojego koszyka.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
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
            order_item.quantity = 1
            order_item.save()
            order.items.remove(order_item)
            messages.info(request, "Produkt został usunięty z twojego koszyka.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Produkt nie był w twoim koszyku.")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Nie masz aktywnego zamówenia.")
        return redirect("core:product", slug=slug)




@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
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
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "Liczba produktów została zaktualizowana.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Produkt nie był w twoim koszyku.")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Nie masz aktywnego zamówenia.")
        return redirect("core:product", slug=slug)
