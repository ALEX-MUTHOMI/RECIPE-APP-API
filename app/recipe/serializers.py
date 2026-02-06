"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
)

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # Nesting: Expect a list of Tag objects here
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a recipe."""
        # 1. Separate tags from recipe data (prevents crash on create)
        tags = validated_data.pop('tags', [])

        # 2. Create the recipe first to generate an ID
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user

        # 3. Handle the tags (Transactional Logic)
        for tag in tags:
            # Get existing tag or create a new one (prevents duplicates)
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            # Link the tag to the recipe
            recipe.tags.add(tag_obj)

        return recipe

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']