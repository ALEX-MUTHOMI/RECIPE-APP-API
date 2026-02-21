"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredients."""

    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipes."""

    # Nesting: Expect a list of Tag/Ingredient objects (e.g., [{"name": "Vegan"}])
    ingredients = IngredientSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id", "title", "time_minutes", "price", "link", "tags", "ingredients"
        ]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle tag retrieval or creation to avoid duplication."""
        auth_user = self.context["request"].user

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle ingredient retrieval or creation to avoid duplication."""
        auth_user = self.context["request"].user

        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a recipe."""

        # 1. Separate M2M data (tags/ingredients) from recipe data
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])

        # 2. Create the recipe instance
        recipe = Recipe.objects.create(**validated_data)

        # 3. Handle the relationships using helper methods
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe."""

        # 1. Separate M2M data (returns None if key is missing)
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)

        # 2. Handle Tags (if provided in payload)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        # 3. Handle Ingredients (if provided in payload)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        # 4. Update remaining fields (title, price, link, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]

class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to a recipe"""

    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": "image"}}