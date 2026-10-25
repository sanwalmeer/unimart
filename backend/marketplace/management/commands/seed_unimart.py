from django.core.management.base import BaseCommand

from marketplace.models import Category, University


class Command(BaseCommand):
    help = 'Seed initial universities and product categories for UniMart.'

    def handle(self, *args, **options):
        universities = [
            'NUST',
            'COMSATS University Islamabad',
            'FAST-NUCES Islamabad',
            'Quaid-i-Azam University (QAU)',
            'Air University',
            'Bahria University Islamabad',
            'International Islamic University Islamabad (IIUI)',
            'NUML Islamabad',
            'Institute of Space Technology (IST)',
            'Riphah International University Islamabad',
            'NUTECH (National University of Technology)',
        ]

        for name in universities:
            University.objects.get_or_create(name=name)

        categories = [
            'Electronics & Laptops',
            'Headphones & Accessories',
            'Books & Study Materials',
            'Backpacks & Bags',
            'Clothes & Fashion',
            'Sneakers & Footwear',
            'Kitchen Essentials',
            'Food & Homemade Meals',
            'Hostel & Room Essentials',
            'Handmade Products',
        ]

        for index, name in enumerate(categories, start=1):
            Category.objects.get_or_create(name=name, defaults={'sort_order': index})

        self.stdout.write(self.style.SUCCESS('UniMart seed data created successfully.'))
