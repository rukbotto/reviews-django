from rest_framework import serializers

from api.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {'ip_address': {'write_only': True}}
