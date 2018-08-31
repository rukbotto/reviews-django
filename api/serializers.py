from rest_framework import serializers

from api.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError('Rating must be a numeric value from 1 to 5')
        return value

    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {'ip_address': {'write_only': True}}
