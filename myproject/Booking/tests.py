from django.test import TestCase
from Booking.models import Order, User, MenuItem, Category
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group
# Create your tests here.

class MenuitemAPITestCase(APITestCase):
    # setUp will run before other methods in this class
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username="superusertest", password="test")
        my_group = Group.objects.create(name="Manager")
        my_group.user_set.add(self.admin_user)
        self.t_user = User.objects.create_user(username="usertest", password="test")
        self.category = Category.objects.create(category_name="testcategory")
        self.menuitem = MenuItem.objects.create(
            item_name = "TestItem",
            category = self.category,
            price = 4.60,
            description = "test test test test"

        )
        # we gone refer to url where we want to send request, reverse func. we are useing to get named url(we need to named it in path)
        # kwargs={'product_id'}) is lookup_url_kwarg we define in views, we need to pass pk of menuitem we created
        self.url = reverse('menuitem-single', kwargs={'product_id': self.menuitem.pk})
        
    def test_get_menuitem(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_name'], self.menuitem.item_name)
    
    def test_unauthorized_update_menuitem(self):
        data = {'item_name': 'updated item'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthorized_delete_menuitem(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_only_manager_can_delete_menuitem(self):
        # test normal user cannot delete - note that this could be its own method
        self.client.login(username="usertest", password="test")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(MenuItem.objects.filter(pk=self.menuitem.pk).exists())

        # test manager can delete
        self.client.login(username="superusertest", password="test")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MenuItem.objects.filter(pk=self.menuitem.pk).exists())
    
    def test_only_manager_can_update_menuitem(self):
        # normal user cannot update
        self.client.login(username="usertest", password="test")
        data = {'item_name': 'updated name'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual('updated name', self.menuitem.item_name)
        

        # manager can update
        self.client.login(username="superusertest", password="test")
        data = {'item_name': 'updated name'}
        response = self.client.patch(self.url, data)
        self.menuitem.refresh_from_db() #lebo aj ked PATCH prebehlo a API odpoveda spravne, self.menuitem objekt kt. sa vytvoril v setUp nie je automaticky aktualizovany
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_name'], self.menuitem.item_name)
        



# class UserOrderTestCase(TestCase):
#     def setUp(self):
#         user1 = User.objects.create_user(username='user1', password='test1')
#         user2 = User.objects.create_user(username='user2', password='test2')
#         Order.objects.create(user=user1)
#         Order.objects.create(user=user1)
#         Order.objects.create(user=user2)
#         Order.objects.create(user=user2)
    
#     def test_user_order_endpoint_retrieves_only_authenticated_user_orders(self):
#         # user gets only his orders
#         user = User.objects.get(username='user2')

#         #TestCase has self.client property - can perform requests, we use force_login request - it will authenticate the user we pass as 
#         # argument and then we can test sending get requests to the endpoint(user-order - the name for url, reverse function get absolute
#         # path reference)
#         self.client.force_login(user)
#         response = self.client.get(reverse('user-order'))

#         #assert response.status_code == status.HTTP_200_OK   #tvrdenie kt. sa ma overiť, success-program beží, fail-program sa zastaví
#         self.assertEqual(response.status_code, 200)
#         orders = response.json()
#         self.assertTrue(all(order['user'] == user.id for order in orders))
#         print(orders)

#     def test_user_order_list_unauthenticated(self):
#         # test if unauthenticated user get 403
#         response = self.client.get(reverse('user-order'))
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

