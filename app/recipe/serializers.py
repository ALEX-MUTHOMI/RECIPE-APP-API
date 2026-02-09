"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredients"""

    class Meta:
        model  = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # Nesting: Expect a list of Tag,Ingredient objects (e.g., [{"name": "Vegan"}])

    ingredients = IngredientSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle ingredient retreival or creation to avoid duplication."""
        # Get the authenticated user from the context
        auth_user =self.context["request"].user

        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipe.ingredients.add(ingredient_obj)


    def _get_or_create_tags(self, tags, recipe):
        """Handle tag retrieval or creation to avoid duplication."""
        # Get the authenticated user from the context
        auth_user = self.context['request'].user

        for tag in tags:
            # Get existing tag or create new one based on name + user
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,  # Unpacks {'name': 'Vegan'} to name='Vegan'
            )
            # Add the tag object to the recipe's ManyToMany relationship
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a recipe."""
        
        # 1. Pop 'tags' so we don't try to save them directly to the Recipe model yet
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop("ingredients", [])

        # 2. Create the recipe instance (without tags)
        recipe = Recipe.objects.create(**validated_data)

        # 3. Use our helper method to process and link the tags
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe."""
        # 1. Pop 'tags' from the data (returns None if not present)
        tags = validated_data.pop('tags', None)

        # 2. If tags were provided in the update, clear old ones and add new ones
        if tags is not None:
            instance.tags.clear()  # Removes all existing associations
            self._get_or_create_tags(tags, instance)

        # 3. Update the other fields (title, price, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']