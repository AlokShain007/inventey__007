from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from inventory.models import Item

class ItemViewTest(APITestCase):

    def setUp(self):
        self.item = Item.objects.create(
            name="Tablet",
            description="A tablet with a stylus"
        )
        self.item_url = reverse('item-detail', args=[self.item.id])
        self.item_list_url = reverse('item-list')

    def test_get_item(self):
        response = self.client.get(self.item_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Tablet")

    def test_post_item(self):
        data = {
            'name': 'Smartwatch',
            'description': 'A watch with health tracking features'
        }
        response = self.client.post(self.item_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Smartwatch')

    def test_delete_item(self):
        response = self.client.delete(self.item_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())
