import re
from django.test import TestCase
from rest_framework import serializers

from api.models import Review
from api.serializers import ReviewSerializer


class ReviewModelTests(TestCase):
    def setUp(self):
        self.review = Review(
            title='My review',
            summary='This is my first review.',
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
        )

    def test_save_model(self):
        self.review.save()

        self.assertIsNotNone(self.review.id)
        self.assertEqual(self.review.title, 'My review')
        self.assertEqual(self.review.summary, 'This is my first review.')
        self.assertEqual(self.review.rating, 1)
        self.assertEqual(self.review.ip_address, '127.0.0.1')
        self.assertEqual(self.review.company, 'Some Company')
        self.assertEqual(self.review.reviewer, 'Some Reviewer')

        iso_re = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{1,6}[+-]{1}\d{2}:\d{2}')

        self.assertIsNotNone(iso_re.match(str(self.review.created_at)))
        self.assertEqual(Review.objects.count(), 1)

    def test_save_valid_model(self):
        self.review.title = 'This is a very very very very very very very veeeeery long title'
        self.summary = ''.join(['a' for i in range(10000)])
        self.review.save()
        self.assertEqual(Review.objects.count(), 1)

    def test_validate_long_title(self):
        self.review.title = 'This is a very very very very very very very very very long title'
        with self.assertRaises(Exception):
            self.review.save()

    def test_validate_long_summary(self):
        self.review.summary = ''.join(['a' for i in range(10001)])
        with self.assertRaises(Exception):
            self.review.save()

    def test_validate_below_zero_rating(self):
        self.review.rating = -1
        with self.assertRaises(Exception):
            self.review.save()

    def test_validate_invalid_ip_address(self):
        self.review.ip_address='127,0,0,1'
        with self.assertRaises(Exception):
            self.review.save()


class ReviewSerializerTests(TestCase):
    def setUp(self):
        self.review = Review(
            title='My review',
            summary='This is my first review.',
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
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
        self.assertEqual(data.get('ip_address'), '127.0.0.1')
        self.assertEqual(data.get('company'), 'Some Company')
        self.assertEqual(data.get('reviewer'), 'Some Reviewer')

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
