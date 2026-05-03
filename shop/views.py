from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Product

ABOUT_FEATURES = [
    {
        "title": "Качество",
        "text": "Тщательно отбираем каждый товар для нашего каталога"
    },
    {
        "title": "Доставка",
        "text": "Быстрая доставка по всему Кыргызстану от 1 до 3 дней"
    },
    {
        "title": "Гарантия",
        "text": "Возврат и обмен товара в течение 14 дней"
    },
    {
        "title": "Забота",
        "text": "Индивидуальный подход к каждому клиенту"
    },
]


def get_cart_list(request):
    cart = request.session.get("cart", [])

    if isinstance(cart, list):
        return cart

    if isinstance(cart, dict):
        fixed_cart = []
        for key, item in cart.items():
            if not isinstance(item, dict):
                continue

            fixed_cart.append({
                "id": item.get("id"),
                "size": item.get("size", "M"),
                "qty": item.get("qty", item.get("quantity", 1))
            })

        request.session["cart"] = fixed_cart
        request.session.modified = True
        return fixed_cart

    request.session["cart"] = []
    request.session.modified = True
    return []


def home(request):
    featured = Product.objects.all()[:4]
    categories = ["Футболки", "Худи", "Джинсы", "Куртки", "Обувь"]
    return render(request, "home.html", {
        "featured": featured,
        "categories": categories,
    })


def catalog(request):
    query = request.GET.get("q", "").strip().lower()
    category = request.GET.get("category", "").strip()

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category and category != "Все":
        products = products.filter(category=category)

    categories = ["Все", "Футболки", "Худи", "Джинсы", "Куртки", "Обувь", "Рубашки", "Штаны", "Свитшоты"]

    return render(request, "catalog.html", {
        "products": products,
        "categories": categories,
        "selected_category": category,
        "query": request.GET.get("q", ""),
    })


def product(request, id):
    product_data = Product.objects.filter(id=id).first()
    if not product_data:
        return redirect("catalog")

    added_product_id = request.session.get("added_product_id")
    return render(request, "product.html", {
        "product": product_data,
        "added_product_id": added_product_id,
    })


def add_to_cart(request, id):
    product_data = Product.objects.filter(id=id).first()
    if not product_data:
        return redirect("catalog")

    selected_size = request.GET.get("size")
    if not selected_size:
        return redirect("product", id=id)

    cart = get_cart_list(request)

    found = False
    for item in cart:
        if item["id"] == id and item["size"] == selected_size:
            item["qty"] += 1
            found = True
            break

    if not found:
        cart.append({
            "id": id,
            "size": selected_size,
            "qty": 1
        })

    request.session["cart"] = cart
    request.session["added_product_id"] = id
    request.session.modified = True
    return redirect("product", id=id)


def cart(request):
    cart_data = get_cart_list(request)
    items = []
    total = 0
    total_qty = 0

    for index, item in enumerate(cart_data):
        product_id = item["id"]
        qty = item["qty"]
        size = item["size"]

        product_data = Product.objects.filter(id=product_id).first()
        if product_data:
            item_total = product_data.price * qty
            total += item_total
            total_qty += qty

            items.append({
                "index": index,
                "id": product_id,
                "name": product_data.name,
                "price": product_data.price,
                "image": product_data.image,
                "qty": qty,
                "size": size,
                "total": item_total
            })

    return render(request, "cart.html", {
        "items": items,
        "total": total,
        "total_qty": total_qty
    })


def sync_added_product_id(request):
    cart = get_cart_list(request)
    added_product_id = request.session.get("added_product_id")

    if added_product_id is None:
        return

    exists_in_cart = any(item.get("id") == added_product_id for item in cart)

    if not exists_in_cart:
        request.session.pop("added_product_id", None)
        request.session.modified = True


def increase_qty(request, index):
    cart = get_cart_list(request)
    if 0 <= index < len(cart):
        cart[index]["qty"] += 1
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


def decrease_qty(request, index):
    cart = get_cart_list(request)
    if 0 <= index < len(cart):
        cart[index]["qty"] -= 1
        if cart[index]["qty"] <= 0:
            cart.pop(index)

    request.session["cart"] = cart
    request.session.modified = True
    sync_added_product_id(request)
    return redirect("cart")


def remove_from_cart(request, index):
    cart = get_cart_list(request)
    if 0 <= index < len(cart):
        cart.pop(index)

    request.session["cart"] = cart
    request.session.modified = True
    sync_added_product_id(request)
    return redirect("cart")


def checkout(request):
    if not request.user.is_authenticated:
        return redirect("login")

    cart_data = get_cart_list(request)
    if not cart_data:
        return redirect("catalog")

    total = 0
    for item in cart_data:
        product_data = Product.objects.filter(id=item["id"]).first()
        if product_data:
            total += product_data.price * item["qty"]

    if request.method == "POST":
        request.session["cart"] = []
        request.session.pop("added_product_id", None)
        request.session.modified = True
        return redirect("success")

    return render(request, "checkout.html", {
        "total": total
    })

def success(request):
    return render(request, "success.html")


def about(request):
    return render(request, "about.html", {
        "features": ABOUT_FEATURES
    })


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")

    return render(request, "register.html", {
        "form": form
    })


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = AuthenticationForm()

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")

    return render(request, "login.html", {
        "form": form
    })


def user_logout(request):
    logout(request)
    return redirect("home")