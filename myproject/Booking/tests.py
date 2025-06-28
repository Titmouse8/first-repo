from django.test import TestCase
from Booking.models import Order, User
from django.urls import reverse
from rest_framework import status
# Create your tests here.

class UserOrderTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='test1')
        user2 = User.objects.create_user(username='user2', password='test2')
        Order.objects.create(user=user1)
        Order.objects.create(user=user1)
        Order.objects.create(user=user2)
        Order.objects.create(user=user2)
    
    def test_user_order_endpoint_retrieves_only_authenticated_user_orders(self):
        # user gets only his orders
        user = User.objects.get(username='user2')

        #TestCase has self.client property - can perform requests, we use force_login request - it will authenticate the user we pass as 
        # argument and then we can test sending get requests to the endpoint(user-order - the name for url, reverse function get absolute
        # path reference)
        self.client.force_login(user)
        response = self.client.get(reverse('user-order'))

        #assert response.status_code == status.HTTP_200_OK   #tvrdenie kt. sa ma overiť, success-program beží, fail-program sa zastaví
        self.assertEqual(response.status_code, 200)
        orders = response.json()
        self.assertTrue(all(order['user'] == user.id for order in orders))
        print(orders)

    def test_user_order_list_unauthenticated(self):
        # test if unauthenticated user get 403
        response = self.client.get(reverse('user-order'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)