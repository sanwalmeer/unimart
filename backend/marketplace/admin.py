from django.contrib import admin

from .models import Category, Product, University, SellerVerificationRequest, ProductReview, Favorite

admin.site.register(University)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Favorite)
admin.site.register(SellerVerificationRequest)
admin.site.register(ProductReview)
