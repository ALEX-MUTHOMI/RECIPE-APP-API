"""
Tests for Recipe Api
"""
from decimal import Decimal
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse("recipe:recipe-list")

def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        "title": "sample recipe title",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "sample description",
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        # FIX 3: Correct casing for APIClient
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testuser@example.com",
            "testpass123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Tests for retrieving a list of recipes"""

        # This creates 2 recipes in the temporary DB
        create_recipe(user=self.user)
        create_recipe(user=self.user)


        res = self.client.get(RECIPES_URL)

        # FIX 5: Minus sign for descending order
        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test listing of recipes to authenticated user"""

        # 1. Create a stranger
        other_user = get_user_model().objects.create_user(
            "other@example.com",
            "password123"
        )
        # 2. Create the stranger's recipe (Should NOT see this)
        create_recipe(user=other_user)
        # 3. Create MY recipe (Should see this)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # 4. Check if the database only returned MY recipe
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)