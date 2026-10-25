import json
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.validators import URLValidator
from django.views.decorators.http import require_GET, require_POST

from .models import Category, Favorite, Product, University


def home(request):
    return render(request, 'index.html')


def product_list_page(request):
    return render(request, 'products.html')


def product_detail_page(request, product_id):
    product = get_object_or_404(
        Product.objects.filter(status='approved').select_related('category', 'university', 'seller'),
        pk=product_id,
    )
    return render(request, 'product_detail.html', {
        'product': product,
        'seller_contact_email': product.seller.email if request.user.is_authenticated and product.allow_email_contact else None,
    })


def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'project': 'UniMart Backend',
        'framework': 'Django',
    })


def _json_body(request):
    try:
        return json.loads(request.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _product_data(product):
    return {
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'price': str(product.price_pkr),
        'category': product.category.name,
        'categoryId': product.category_id,
        'condition': product.get_condition_display(),
        'university': product.university.name if product.university else 'Not affiliated',
        'universityId': product.university_id,
        'sellerName': product.seller.first_name or 'UniMart Seller',
        'image': product.image_url,
        'status': product.get_status_display(),
        'createdAt': product.created_at.isoformat(),
        'allowEmailContact': product.allow_email_contact,
    }


def _demo_products(categories, universities):
    category_ids = {category.name: category.id for category in categories}
    university_ids = {university.name: university.id for university in universities}
    demo_items = [
        {
            'id': 'demo-laptop',
            'title': 'Dell Latitude 7410',
            'description': 'A reliable study laptop with 16GB RAM and 512GB SSD.',
            'price': '82000',
            'category': 'Electronics & Laptops',
            'condition': 'Pre-loved',
            'university': 'NUST',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-20',
        },
        {
            'id': 'demo-books',
            'title': 'Chemistry Lab Book Set',
            'description': 'A clean set of chemistry lab books and study notes.',
            'price': '3500',
            'category': 'Books & Study Materials',
            'condition': 'Pre-loved',
            'university': 'FAST-NUCES Islamabad',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-19',
        },
        {
            'id': 'demo-backpack',
            'title': 'Everyday Campus Backpack',
            'description': 'Roomy backpack with a laptop sleeve and water-resistant finish.',
            'price': '4200',
            'category': 'Backpacks & Bags',
            'condition': 'New',
            'university': 'Air University',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-18',
        },
        {
            'id': 'demo-headphones',
            'title': 'Wireless Study Headphones',
            'description': 'Comfortable over-ear headphones for lectures and study sessions.',
            'price': '18000',
            'category': 'Headphones & Accessories',
            'condition': 'New',
            'university': 'Bahria University Islamabad',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-17',
        },
        {
            'id': 'demo-lamp',
            'title': 'Adjustable Desk Lamp',
            'description': 'Compact LED lamp with adjustable brightness for a hostel desk.',
            'price': '2600',
            'category': 'Hostel & Room Essentials',
            'condition': 'New',
            'university': 'NUML Islamabad',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-16',
        },
        {
            'id': 'demo-sneakers',
            'title': 'Classic Everyday Sneakers',
            'description': 'Pre-loved sneakers in good condition, size 40.',
            'price': '8000',
            'category': 'Sneakers & Footwear',
            'condition': 'Pre-loved',
            'university': 'Riphah International University Islamabad',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-15',
        },
        {
            'id': 'demo-fashion',
            'title': 'Everyday Campus Hoodie',
            'description': 'A comfortable layering piece for early classes and cool evenings.',
            'price': '3200',
            'category': 'Clothes & Fashion',
            'condition': 'New',
            'university': 'COMSATS University Islamabad',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-14',
        },
        {
            'id': 'demo-kitchen',
            'title': 'Hostel Kitchen Starter Set',
            'description': 'Useful everyday kitchen basics for a student room or hostel.',
            'price': '2800',
            'category': 'Kitchen Essentials',
            'condition': 'Pre-loved',
            'university': 'Quaid-i-Azam University (QAU)',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-13',
        },
        {
            'id': 'demo-meals',
            'title': 'Homemade Snack Box',
            'description': 'A preview of homemade food listings available around campus.',
            'price': '650',
            'category': 'Food & Homemade Meals',
            'condition': 'New',
            'university': 'International Islamic University Islamabad (IIUI)',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-12',
        },
        {
            'id': 'demo-handmade',
            'title': 'Handmade Ceramic Mug',
            'description': 'A handmade mug, a thoughtful addition to a study desk.',
            'price': '1400',
            'category': 'Handmade Products',
            'condition': 'New',
            'university': 'Institute of Space Technology (IST)',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-11',
        },
        {
            'id': 'demo-bahria-books',
            'title': 'Semester Study Notes',
            'description': 'Organized lecture notes ready for another student to use.',
            'price': '900',
            'category': 'Books & Study Materials',
            'condition': 'Pre-loved',
            'university': 'Bahria University Islamabad',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1455390582262-044c33d4a6ad?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-10',
        },
        {
            'id': 'demo-numl-bag',
            'title': 'Everyday Tote Bag',
            'description': 'A lightweight tote for notebooks and daily essentials.',
            'price': '1100',
            'category': 'Backpacks & Bags',
            'condition': 'Pre-loved',
            'university': 'NUML Islamabad',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-09',
        },
        {
            'id': 'demo-nust-accessories',
            'title': 'Wireless Earbuds',
            'description': 'Compact wireless earbuds for commuting and study breaks.',
            'price': '4500',
            'category': 'Headphones & Accessories',
            'condition': 'New',
            'university': 'NUST',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-08',
        },
        {
            'id': 'demo-nutech-laptop',
            'title': 'Laptop Stand',
            'description': 'Foldable stand to make long study sessions more comfortable.',
            'price': '1700',
            'category': 'Electronics & Laptops',
            'condition': 'Pre-loved',
            'university': 'NUTECH (National University of Technology)',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-07',
        },
        {
            'id': 'demo-riphah-fashion',
            'title': 'Classic Denim Jacket',
            'description': 'A gently worn denim jacket in excellent everyday condition.',
            'price': '3900',
            'category': 'Clothes & Fashion',
            'condition': 'Pre-loved',
            'university': 'Riphah International University Islamabad',
            'sellerName': 'Sample seller',
            'image': 'https://images.unsplash.com/photo-1543076447-215ad9ba6923?auto=format&fit=crop&w=900&q=80',
            'createdAt': '2026-10-06',
        },
    ]
    products = []
    for item in demo_items:
        category_id = category_ids.get(item['category'])
        university_id = university_ids.get(item['university'])
        if not category_id or not university_id:
            continue
        products.append({
            **item,
            'categoryId': category_id,
            'universityId': university_id,
            'status': 'Preview sample',
            'demo': True,
        })
    return products


@require_GET
def api_session(request):
    user = request.user
    return JsonResponse({
        'authenticated': user.is_authenticated,
        'user': {
            'name': user.first_name or user.username,
            'email': user.email,
        } if user.is_authenticated else None,
    })


@require_GET
def api_catalog(request):
    return JsonResponse({
        'categories': list(Category.objects.filter(is_active=True).order_by('sort_order', 'name').values('id', 'name')),
        'universities': list(University.objects.filter(is_active=True).order_by('name').values('id', 'name')),
    })


@require_GET
def api_products(request):
    products = Product.objects.filter(status='approved').select_related('category', 'university', 'seller')
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category')
    university_id = request.GET.get('university')
    condition = request.GET.get('condition')
    if search:
        from django.db.models import Q
        products = products.filter(Q(title__icontains=search) | Q(description__icontains=search))
    if category_id:
        products = products.filter(category_id=category_id)
    if university_id:
        products = products.filter(university_id=university_id)
    if condition in {'new', 'pre_loved'}:
        products = products.filter(condition=condition)
    database_products = [_product_data(product) for product in products.order_by('-created_at')]
    if not settings.DEBUG:
        return JsonResponse({'products': database_products})

    demo_products = _demo_products(
        Category.objects.filter(is_active=True),
        University.objects.filter(is_active=True),
    )
    if search:
        demo_products = [product for product in demo_products if search.casefold() in f"{product['title']} {product['description']}".casefold()]
    if category_id:
        demo_products = [product for product in demo_products if str(product['categoryId']) == category_id]
    if university_id:
        demo_products = [product for product in demo_products if str(product['universityId']) == university_id]
    if condition in {'new', 'pre_loved'}:
        display_condition = 'New' if condition == 'new' else 'Pre-loved'
        demo_products = [product for product in demo_products if product['condition'] == display_condition]
    return JsonResponse({'products': database_products + demo_products})


@require_GET
def api_product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.filter(status='approved').select_related('category', 'university', 'seller'),
        pk=product_id,
    )
    return JsonResponse({'product': _product_data(product)})


@require_GET
def api_my_products(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Sign in to view your listings.'}, status=401)
    products = Product.objects.filter(seller=request.user).select_related('category', 'university', 'seller')
    product_data = []
    for product in products.order_by('-created_at'):
        item = _product_data(product)
        item['rejectionReason'] = product.reviews.filter(decision='rejected').order_by('-created_at').values_list('rejection_reason', flat=True).first()
        item['canWithdraw'] = product.status in {'pending', 'approved', 'rejected'}
        product_data.append(item)
    return JsonResponse({'products': product_data})


@require_GET
def api_favorites(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Sign in to view your favourites.'}, status=401)
    products = Product.objects.filter(
        favorited_by__user=request.user,
        status='approved',
    ).select_related('category', 'university', 'seller').order_by('-favorited_by__created_at')
    return JsonResponse({'products': [_product_data(product) for product in products]})


@require_POST
def api_toggle_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Sign in to save favourites.'}, status=401)
    data = _json_body(request)
    if data is None:
        return JsonResponse({'error': 'Please submit valid form data.'}, status=400)
    try:
        product = Product.objects.get(pk=data.get('productId'), status='approved')
    except (Product.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'This product is not available to favourite.'}, status=404)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
    return JsonResponse({'favorited': created})


@require_POST
def api_withdraw_product(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Sign in to manage your listings.'}, status=401)
    product = get_object_or_404(Product, pk=product_id, seller=request.user)
    if product.status not in {'pending', 'approved', 'rejected'}:
        return JsonResponse({'error': 'This listing cannot be withdrawn in its current status.'}, status=409)
    product.status = 'withdrawn'
    product.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'message': 'Your listing has been withdrawn.'})


@require_POST
def api_signup(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({'error': 'Please submit valid form data.'}, status=400)
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    if not name or len(name) > 150 or not email or len(email) > 254 or not password:
        return JsonResponse({'error': 'Name, email, and password are required.'}, status=400)
    User = get_user_model()
    if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username=email).exists():
        return JsonResponse({'error': 'An account with this email already exists.'}, status=400)
    verification_required = settings.EMAIL_VERIFICATION_REQUIRED
    if settings.DEBUG and not verification_required:
        if len(password) < 6:
            return JsonResponse({'error': 'Use a password with at least 6 characters.'}, status=400)
    else:
        try:
            validate_password(password)
        except ValidationError as error:
            return JsonResponse({'error': ' '.join(error.messages)}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        first_name=name,
        password=password,
        is_active=not verification_required,
    )
    if not verification_required:
        login(request, user)
        return JsonResponse({
            'message': 'Account created. You are signed in and can submit a product now.',
            'authenticated': True,
            'user': {'name': user.first_name or user.username, 'email': user.email},
        }, status=201)

    verification_token = signing.dumps(user.pk, salt='marketplace.email-verification')
    verification_url = request.build_absolute_uri(reverse('verify_email', args=[verification_token]))
    send_mail(
        'Verify your UniMart account',
        f'Hello {name}, verify your email to start using UniMart: {verification_url}',
        None,
        [email],
    )
    return JsonResponse({'message': 'Account created. Check your email for the verification link.'}, status=201)


@require_GET
def verify_email(request, token):
    try:
        user_id = signing.loads(token, salt='marketplace.email-verification', max_age=60 * 60 * 24)
        user = get_user_model().objects.get(pk=user_id)
    except (signing.BadSignature, get_user_model().DoesNotExist):
        return JsonResponse({'error': 'This verification link is invalid or expired.'}, status=400)
    user.is_active = True
    user.save(update_fields=['is_active'])
    login(request, user)
    return redirect('/?verified=1')


@require_POST
def api_login(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({'error': 'Please submit valid form data.'}, status=400)
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    User = get_user_model()
    user_record = User.objects.filter(email__iexact=email).first()
    user = authenticate(request, username=user_record.username, password=password) if user_record else None
    if user is None:
        if user_record and not user_record.is_active and settings.EMAIL_VERIFICATION_REQUIRED:
            return JsonResponse({'error': 'Verify your email before signing in. Check the verification email.'}, status=403)
        if user_record and not user_record.is_active and settings.DEBUG:
            if not user_record.check_password(password):
                return JsonResponse({'error': 'Email or password is incorrect.'}, status=400)
            user_record.is_active = True
            user_record.save(update_fields=['is_active'])
            user = authenticate(request, username=user_record.username, password=password)
        if user is None:
            return JsonResponse({'error': 'Email or password is incorrect.'}, status=400)
    login(request, user)
    return JsonResponse({'message': 'Signed in successfully.', 'user': {'name': user.first_name or user.username, 'email': user.email}})


@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({'message': 'Signed out.'})


@require_POST
def api_create_product(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Sign in to submit a product.'}, status=401)
    if not request.user.is_active:
        return JsonResponse({'error': 'Verify your email before submitting a product.'}, status=403)
    data = _json_body(request)
    if data is None:
        return JsonResponse({'error': 'Please submit valid form data.'}, status=400)
    title = str(data.get('title', '')).strip()
    description = str(data.get('description', '')).strip()
    image_url = str(data.get('imageUrl', '')).strip()
    if not title or len(title) > 200 or not description or not image_url:
        return JsonResponse({'error': 'Title, description, and product image URL are required.'}, status=400)
    try:
        URLValidator(schemes=['http', 'https'])(image_url)
        price = Decimal(str(data.get('price', '')))
        if not price.is_finite() or price <= 0 or price.as_tuple().exponent < -2:
            raise InvalidOperation
        category = Category.objects.get(pk=data.get('categoryId'), is_active=True)
        condition = data.get('condition')
        if condition not in {'new', 'pre_loved'}:
            raise ValueError
        university_id = data.get('universityId') or None
        university = University.objects.get(pk=university_id, is_active=True) if university_id else None
        product = Product.objects.create(
            seller=request.user,
            category=category,
            university=university,
            title=title,
            description=description,
            price_pkr=price,
            condition=condition,
            image_url=image_url,
            allow_email_contact=data.get('allowEmailContact') is True,
            status='pending',
        )
    except (InvalidOperation, ValueError, Category.DoesNotExist, University.DoesNotExist, ValidationError):
        return JsonResponse({'error': 'Check the price, category, condition, and university fields.'}, status=400)
    return JsonResponse({'message': 'Product submitted for admin review.', 'product': _product_data(product)}, status=201)


@require_GET
def api_csrf(request):
    from django.middleware.csrf import get_token
    return JsonResponse({'csrfToken': get_token(request)})
