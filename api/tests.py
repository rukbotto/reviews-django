import re
from django.test import TestCase
from rest_framework import serializers

from api.models import Review
from api.serializers import ReviewSerializer


class ReviewModelTests(TestCase):
    def test_can_create_review(self):
        review = Review(
            title='My review',
            summary='This is my first review.',
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
        )
        review.save()

        self.assertIsNotNone(review.id)
        self.assertEqual(review.title, 'My review')
        self.assertEqual(review.summary, 'This is my first review.')
        self.assertEqual(review.rating, 1)
        self.assertEqual(review.ip_address, '127.0.0.1')
        self.assertEqual(review.company, 'Some Company')
        self.assertEqual(review.reviewer, 'Some Reviewer')

        iso_re = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{1,6}[+-]{1}\d{2}:\d{2}')
        self.assertIsNotNone(iso_re.match(str(review.created_at)))

        reviews = Review.objects.count()

        self.assertEqual(reviews, 1)

    def test_can_create_valid_review(self):
        review = Review(
            title='This is a very very very very very very very veeeeery long title',
            summary=''.join(['a' for i in range(10000)]),
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
        )
        review.save()

        reviews = Review.objects.count()

        self.assertEqual(reviews, 1)

    def test_cannot_create_review_long_title(self):
        review = Review(
            title='This is a very very very very very very very very very long title',
            summary='This is my first review.',
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
        )

        with self.assertRaises(Exception) as cm:
            review.save()

    def test_cannot_create_review_long_summary(self):
        review = Review(
            title='My review',
            summary=''.join(['a' for i in range(10001)]),
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
        )

        with self.assertRaises(Exception) as cm:
            review.save()

    def test_cannot_create_review_below_zero_rating(self):
        review = Review(
            title='My review',
            summary='This is my first review.',
            rating=-1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
        )

        with self.assertRaises(Exception):
            review.save()

    def test_cannot_create_review_invalid_ip_address(self):
        review = Review(
            title='My review',
            summary='This is my first review.',
            rating=1,
            ip_address='127,0,0,1',
            company='Some Company',
            reviewer='Some Reviewer',
        )

        with self.assertRaises(Exception):
            review.save()


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
