"""
Serializers for the User API Views.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        """Meta class for the serializer."""
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'email': {'read_only': True}
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)
