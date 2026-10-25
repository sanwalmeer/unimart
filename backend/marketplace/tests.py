import json
import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Product


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_VERIFICATION_REQUIRED=True)
class MarketplaceAccountTests(TestCase):
	def setUp(self):
		self.category = Category.objects.create(name='Books & Study Materials')

	def create_user(self, email):
		return get_user_model().objects.create_user(
			username=email,
			email=email,
			password='SeaGlass!Rocket9284',
		)

	def create_product(self, seller, status='approved'):
		return Product.objects.create(
			seller=seller,
			category=self.category,
			title='Test marketplace listing',
			description='A listing used to test permissions.',
			price_pkr='1500',
			status=status,
		)

	def test_personal_email_can_signup_verify_and_submit_pending_product(self):
		response = self.client.post(
			reverse('api_signup'),
			data=json.dumps({
				'name': 'Student Seller',
				'email': 'student@example.com',
				'password': 'SeaGlass!Rocket9284',
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(len(mail.outbox), 1)
		verification_token = re.search(r'/verify-email/([^/]+)/', mail.outbox[0].body).group(1)
		verification_response = self.client.get(reverse('verify_email', args=[verification_token]))
		self.assertEqual(verification_response.status_code, 302)

		product_response = self.client.post(
			reverse('api_create_product'),
			data=json.dumps({
				'title': 'Used Calculus Book',
				'description': 'Clean copy with no missing pages.',
				'price': '1200',
				'categoryId': self.category.id,
				'condition': 'pre_loved',
				'universityId': None,
				'imageUrl': 'https://example.com/book.jpg',
			}),
			content_type='application/json',
		)

		self.assertEqual(product_response.status_code, 201)
		product = Product.objects.get()
		self.assertEqual(product.status, 'pending')
		self.assertEqual(product.seller.email, 'student@example.com')
		public_products = self.client.get(reverse('api_products')).json()['products']
		self.assertTrue(all(product.get('demo') for product in public_products))
		self.assertNotIn(product.id, [item['id'] for item in public_products])
		self.assertEqual(len(self.client.get(reverse('api_my_products')).json()['products']), 1)
		self.assertEqual(self.client.get(reverse('product_detail', args=[product.id])).status_code, 404)

		product.status = 'approved'
		product.allow_email_contact = True
		product.save(update_fields=['status', 'allow_email_contact'])
		self.client.logout()
		detail_response = self.client.get(reverse('product_detail', args=[product.id]))
		self.assertEqual(detail_response.status_code, 200)
		self.assertContains(detail_response, 'Contact seller')
		self.assertNotContains(detail_response, product.seller.email)
		buyer = get_user_model().objects.create_user(
			username='verified-buyer@example.com',
			email='verified-buyer@example.com',
			password='SeaGlass!Rocket9284',
		)
		self.client.force_login(buyer)
		authenticated_detail = self.client.get(reverse('product_detail', args=[product.id]))
		self.assertContains(authenticated_detail, product.seller.email)

	def test_contact_email_requires_seller_opt_in(self):
		seller = self.create_user('private-seller@example.com')
		buyer = self.create_user('private-buyer@example.com')
		product = self.create_product(seller)
		self.client.force_login(buyer)
		response = self.client.get(reverse('product_detail', args=[product.id]))
		self.assertContains(response, 'Seller contact unavailable')
		self.assertNotContains(response, seller.email)

	@override_settings(DEBUG=False)
	def test_demo_products_are_disabled_outside_debug_mode(self):
		response = self.client.get(reverse('api_products'))
		self.assertEqual(response.json()['products'], [])

	def test_unverified_account_cannot_sign_in_or_submit_product(self):
		self.client.post(
			reverse('api_signup'),
			data=json.dumps({
				'name': 'Student Seller',
				'email': 'student@example.com',
				'password': 'SeaGlass!Rocket9284',
			}),
			content_type='application/json',
		)

		response = self.client.post(
			reverse('api_login'),
			data=json.dumps({'email': 'student@example.com', 'password': 'SeaGlass!Rocket9284'}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code, 403)
		self.assertEqual(self.client.post(reverse('api_create_product')).status_code, 401)

	@override_settings(EMAIL_VERIFICATION_REQUIRED=False)
	def test_local_demo_signup_is_immediately_authenticated(self):
		response = self.client.post(
			reverse('api_signup'),
			data=json.dumps({
				'name': 'Demo Student',
				'email': 'demo@example.com',
				'password': 'SeaGlass!Rocket9284',
			}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code, 201)
		self.assertTrue(response.json()['authenticated'])
		self.assertEqual(len(mail.outbox), 0)
		self.assertEqual(self.client.get(reverse('api_session')).json()['user']['email'], 'demo@example.com')

	@override_settings(EMAIL_VERIFICATION_REQUIRED=False, DEBUG=True)
	def test_previous_inactive_demo_account_can_login_without_verification(self):
		user = get_user_model().objects.create_user(
			username='old-demo@example.com',
			email='old-demo@example.com',
			password='simplepass',
			is_active=False,
		)
		response = self.client.post(
			reverse('api_login'),
			data=json.dumps({'email': user.email, 'password': 'simplepass'}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code, 200)
		user.refresh_from_db()
		self.assertTrue(user.is_active)
		self.assertNotEqual(user.password, 'simplepass')

	@override_settings(EMAIL_VERIFICATION_REQUIRED=False, DEBUG=True)
	def test_local_demo_allows_simple_six_character_password(self):
		response = self.client.post(
			reverse('api_signup'),
			data=json.dumps({
				'name': 'Simple Password Student',
				'email': 'simple@example.com',
				'password': 'simplepass',
			}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code, 201)

	@override_settings(DEBUG=True)
	def test_demo_products_cover_all_seeded_filters(self):
		call_command('seed_unimart', verbosity=0)
		catalog = self.client.get(reverse('api_catalog')).json()
		products = self.client.get(reverse('api_products')).json()['products']
		self.assertTrue(products)
		self.assertEqual({product['categoryId'] for product in products}, {category['id'] for category in catalog['categories']})
		self.assertEqual({product['universityId'] for product in products}, {university['id'] for university in catalog['universities']})
		self.assertEqual({product['condition'] for product in products}, {'New', 'Pre-loved'})
		for category in catalog['categories']:
			filtered = self.client.get(reverse('api_products'), {'category': category['id']}).json()['products']
			self.assertTrue(filtered, category['name'])
		for university in catalog['universities']:
			filtered = self.client.get(reverse('api_products'), {'university': university['id']}).json()['products']
			self.assertTrue(filtered, university['name'])

		user = get_user_model().objects.create_user(
			username='approved@example.com',
			email='approved@example.com',
			password='SeaGlass!Rocket9284',
		)
		Product.objects.create(
			seller=user,
			category=Category.objects.get(pk=catalog['categories'][0]['id']),
			title='Real approved test listing',
			description='Approved database product',
			price_pkr='100',
			status='approved',
		)
		other_category = catalog['categories'][-1]
		filtered = self.client.get(reverse('api_products'), {'category': other_category['id']}).json()['products']
		self.assertTrue(any(item.get('demo') for item in filtered))

	@override_settings(DEBUG=False)
	def test_demo_products_are_not_returned_in_production_mode(self):
		call_command('seed_unimart', verbosity=0)
		response = self.client.get(reverse('api_products'))
		self.assertEqual(response.json()['products'], [])

	def test_favorites_require_login_and_are_private_to_owner(self):
		seller = self.create_user('seller@example.com')
		buyer = self.create_user('buyer@example.com')
		other_buyer = self.create_user('other@example.com')
		product = self.create_product(seller)

		self.assertEqual(self.client.get(reverse('api_favorites')).status_code, 401)
		self.client.force_login(buyer)
		favorite_response = self.client.post(
			reverse('api_toggle_favorite'),
			data=json.dumps({'productId': product.id}),
			content_type='application/json',
		)
		self.assertEqual(favorite_response.status_code, 200)
		self.assertTrue(favorite_response.json()['favorited'])
		self.assertEqual(len(self.client.get(reverse('api_favorites')).json()['products']), 1)

		self.client.force_login(other_buyer)
		self.assertEqual(self.client.get(reverse('api_favorites')).json()['products'], [])

	def test_only_listing_owner_can_withdraw_product(self):
		seller = self.create_user('seller@example.com')
		other_user = self.create_user('other@example.com')
		product = self.create_product(seller, status='pending')

		self.client.force_login(other_user)
		self.assertEqual(self.client.post(reverse('api_withdraw_product', args=[product.id])).status_code, 404)
		product.refresh_from_db()
		self.assertEqual(product.status, 'pending')

		self.client.force_login(seller)
		response = self.client.post(reverse('api_withdraw_product', args=[product.id]))
		self.assertEqual(response.status_code, 200)
		product.refresh_from_db()
		self.assertEqual(product.status, 'withdrawn')
