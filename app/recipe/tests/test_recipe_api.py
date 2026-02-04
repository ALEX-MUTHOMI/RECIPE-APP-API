"""
Tests for Recipe Api.
"""
from decimal import Decimal
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """
    Create and return a recipe detail URL.
    Example: /api/recipe/recipes/5/
    """
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    """
    Helper function to create and return a sample recipe.
    This keeps our tests DRY (Don't Repeat Yourself).
    """
    defaults = {
        "title": "sample recipe title",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "sample description",
        "link": "http://example.com/recipe.pdf",
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Helper function to create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required.
        Ensures the API acts as a 'Bouncer' preventingapp/recipe/tests/test_recipe_api.py
        strangers from seeing our data.
        """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="testpass123")
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """
        Tests for retrieving a list of recipes.
        Verifies that the API returns the correct list structure
        using the Standard Serializer (Lightweight).
        """
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """
        Test listing of recipes is limited to the authenticated user.
        Ensures 'Privacy': User A should never see User B's recipes.
        """
        other_user = create_user(email="other@example.com", password="password123")

        # Create a recipe for the other user (Should NOT be visible)
        create_recipe(user=other_user)
        # Create a recipe for ME (Should be visible)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """
        Test get recipe detail.
        Verifies that asking for a specific ID triggers the
        RecipeDetailSerializer (Heavy) with all fields.
        """
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """
        Test Creating a recipe.
        Verifies the POST method correctly parses the payload,
        creates a database entry, and assigns the correct User.
        """
        payload = {
            "title": "Chocolate Cheesecake",
            "time_minutes": 45,
            "price": Decimal("5.99"),
            "description": "Delicious chocolate cheesecake recipe",
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Verify the data was actually saved to the database
        recipe = Recipe.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        # Verify ownership (Security check)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """
        Test partial update (PATCH) of a recipe.
        Verifies we can update just ONE field (Title) without
        erasing or needing to resend the other fields (Link).
        """
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="SAMPLE recipe title",
            link=original_link,
        )

        payload = {"title": "New recipe title"}
        url = detail_url(recipe.id)

        # Use PATCH for partial updates
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        # Check title changed, but link remained the same
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """
        Test full update (PUT) of recipe.
        Verifies that PUT updates ALL fields provided in the payload.
        """
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link="https://example.com/recipe.pdf",
        )

        payload = {
            "title": "new recipe title",
            "link": "https://example.com/new-recipe.pdf",
            "time_minutes": 10,
            "description": "New recipe description",
            "price": Decimal("2.50"),
        }
        url = detail_url(recipe.id)

        # Use PUT for full updates
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """
        Test Changing the recipe user is ignored.
        Ensures that a user cannot 'gift' a recipe to someone else
        or hack the ownership field via the API.
        """
        new_user = create_user(email="user2@example.com", password="password123")
        recipe = create_recipe(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(recipe.id)

        # Attempt to change the owner
        res = self.client.patch(url, payload)

        # The API should ignore the 'user' field (Read Only)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        # Ensure the owner is STILL the original user
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """
        Test deleting a recipe is successful.
        Verifies the DELETE method removes the object from the DB.
        """
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())





