from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import serializers

from api.models import Review
from api.serializers import ReviewSerializer


class ReviewSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'user1',
            'user1@example.com',
            'user1_pwd'
        )

        self.review = Review(
            title='My review',
            summary='This is my first review.',
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
            user=self.user,
        )

        self.data = {
            'id': 1,
            'title': 'My review',
            'summary': 'This is my first review.',
            'rating': 1,
            'ip_address': '127.0.0.1',
            'company': 'Some Company',
            'reviewer': 'Some Reviewer',
        }

    def test_serialize_model(self):
        self.review.save()
        serializer = ReviewSerializer(self.review)

        self.assertIsInstance(serializer, serializers.ModelSerializer)

        data = serializer.data

        self.assertIsNotNone(data.get('id'))
        self.assertEqual(data.get('title'), 'My review')
        self.assertEqual(data.get('summary'), 'This is my first review.')
        self.assertEqual(data.get('rating'), 1)
        self.assertFalse('ip_address' in data)
        self.assertEqual(data.get('company'), 'Some Company')
        self.assertEqual(data.get('reviewer'), 'Some Reviewer')
        self.assertEqual(data.get('user'), 'user1')

    def test_deserialize_data(self):
        serializer = ReviewSerializer(data=self.data)

        self.assertIsInstance(serializer, serializers.ModelSerializer)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validated_data

        self.assertEqual(validated_data.get('title'), 'My review')
        self.assertEqual(validated_data.get('summary'), 'This is my first review.')
        self.assertEqual(validated_data.get('rating'), 1)
        self.assertEqual(validated_data.get('ip_address'), '127.0.0.1')
        self.assertEqual(validated_data.get('company'), 'Some Company')
        self.assertEqual(validated_data.get('reviewer'), 'Some Reviewer')

    def test_validate_long_title(self):
        self.data['title'] = 'This is a very very very very very very very very very long title'
        serializer = ReviewSerializer(data=self.data)

        self.assertIsInstance(serializer, serializers.ModelSerializer)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors.get('title')), 1)

    def test_validate_long_summary(self):
        self.data['summary'] = ''.join(['a' for i in range(10001)])
        serializer = ReviewSerializer(data=self.data)

        self.assertIsInstance(serializer, serializers.ModelSerializer)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors.get('summary')), 1)

    def test_validate_below_zero_rating(self):
        self.data['rating'] = -1
        serializer = ReviewSerializer(data=self.data)

        self.assertIsInstance(serializer, serializers.ModelSerializer)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors.get('rating')), 1)

    def test_validate_invalid_ip_address(self):
        self.data['ip_address'] = '127,0,0,1'
        serializer = ReviewSerializer(data=self.data)

        self.assertIsInstance(serializer, serializers.ModelSerializer)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors.get('ip_address')), 1)
