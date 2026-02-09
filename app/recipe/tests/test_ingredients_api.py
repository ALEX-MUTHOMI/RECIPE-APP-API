"""
Test for the Ingredients API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredient-list")

def create_user(email="user@example.com", password="testpass123"):
    """Helper function to create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicIngredientsApiTests(TestCase):
    """Test the publicly available (unauthenticated) Ingredients API"""
    def setup(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that Login is required for retreiving Ingredients"""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """Test the authorized user for Ingredients API"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_ingredients(self):
        """Test retreiving a list of Ingredients"""
        Ingredient.objects.create(user=self.user, name="potpieingredients")
        Ingredient.objects.create(user=self.user, name ="meat ingredients")

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients are  for the authenticate user only"""
        user2 = create_user(email="user2@example.com")

        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name="Tumeric")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)





