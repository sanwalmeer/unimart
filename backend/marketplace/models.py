from django.conf import settings
from django.db import models


class University(models.Model):
    name = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('suspended', 'Suspended'),
    ]

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('pre_loved', 'Pre-loved'),
    ]

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_pkr = models.DecimalField(max_digits=12, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    image_url = models.URLField(blank=True, null=True)
    allow_email_contact = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user} -> {self.product}'


class ProductReview(models.Model):
    DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews_done')
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product} - {self.decision}'


class SellerVerificationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_requests')
    submitted_evidence = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_verifications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.status}'
