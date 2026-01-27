"""
Views for the recipe API.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication # <--- IMPORTED
from rest_framework.permissions import IsAuthenticated        # <--- IMPORTED

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""

    # FIX 1: Correct spelling (serializer_class)
    serializer_class = serializers.RecipeSerializer

    # FIX 2: Correct spelling (queryset)
    queryset = Recipe.objects.all()

    # FIX 3: Lists with brackets [], not parentheses ()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # FIX 4: self.queryset (not self.query_set)
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """Create a new recipe."""
        # FIX 5: Clean save logic. Assign the current user to the recipe.
        serializer.save(user=self.request.user)