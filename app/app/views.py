"""
Views for the core app.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


class FakeSerializer(serializers.Serializer):
    pass


@extend_schema(exclude=True)
class FakeProtectedView(generics.GenericAPIView):
    """This view is used for testing purposes only."""
    permission_classes = [IsAuthenticated]
    serializer_class = FakeSerializer

    def get(self, request):
        return Response({"message": "You have access!"})
