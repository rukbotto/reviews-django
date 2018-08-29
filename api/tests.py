import re

from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.test.client import FakePayload
from rest_framework import serializers
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from api.models import Review
from api.serializers import ReviewSerializer
from api.views import ReviewListView, ReviewDetailView


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


class TestReviewListView(TestCase):
    def setUp(self):
        self.context = {
            'title': 'My review',
            'summary': 'This is my first review.',
            'rating': 1,
            'ip_address': '127.0.0.1',
            'company': 'Some Company',
            'reviewer': 'Some Reviewer'
        }

        self.data = '''
        {{
            "title": "{c[title]}",
            "summary": "{c[summary]}",
            "rating": {c[rating]},
            "ip_address": "{c[ip_address]}",
            "company": "{c[company]}",
            "reviewer": "{c[reviewer]}"
        }}
        '''

        self.view = ReviewListView()

    def _prepare_request(self, data):
        payload = FakePayload(data)
        request = WSGIRequest({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': '{}'.format(len(payload)),
            'wsgi.input': payload
        })
        return request

    def test_post_review(self):
        request = self._prepare_request(self.data.format(c=self.context))
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data

        self.assertIsNotNone(data.get('id'))
        self.assertEqual(data.get('title'), 'My review')
        self.assertEqual(data.get('summary'), 'This is my first review.')
        self.assertEqual(data.get('rating'), 1)
        self.assertEqual(data.get('ip_address'), '127.0.0.1')
        self.assertEqual(data.get('company'), 'Some Company')
        self.assertEqual(data.get('reviewer'), 'Some Reviewer')
        self.assertEqual(Review.objects.count(), 1)

    def test_post_review_long_title(self):
        self.context['title'] = 'This is a very very very very very very very very very long title'
        request = self._prepare_request(self.data.format(c=self.context))
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data

        self.assertEqual(len(errors.get('title')), 1)

    def test_post_review_long_summary(self):
        self.context['summary'] = ''.join(['a' for i in range(10001)])
        request = self._prepare_request(self.data.format(c=self.context))
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data

        self.assertEqual(len(errors.get('summary')), 1)

    def test_post_review_below_zero_rating(self):
        self.context['rating'] = -1
        request = self._prepare_request(self.data.format(c=self.context))
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data

        self.assertEqual(len(errors.get('rating')), 1)

    def test_post_review_invalid_ip_address(self):
        self.context['ip_address'] = '127,0,0,1'
        request = self._prepare_request(self.data.format(c=self.context))
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data

        self.assertEqual(len(errors.get('ip_address')), 1)


class TestReviewDetailView(TestCase):
    def setUp(self):
        self.review = Review(
            title='My review',
            summary='This is my first review.',
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
        )

        self.view = ReviewDetailView()

    def _prepare_get_request(self):
        payload = FakePayload('')
        request = WSGIRequest({
            'REQUEST_METHOD': 'GET',
            'CONTENT_LENGTH': 0,
            'wsgi.input': payload
        })
        return request

    def test_get_review(self):
        self.review.save()

        request = self._prepare_get_request()
        response = self.view.dispatch(request, pk=self.review.id)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertIsNotNone(data.get('id'))
        self.assertEqual(data.get('title'), 'My review')
        self.assertEqual(data.get('summary'), 'This is my first review.')
        self.assertEqual(data.get('rating'), 1)
        self.assertEqual(data.get('ip_address'), '127.0.0.1')
        self.assertEqual(data.get('company'), 'Some Company')
        self.assertEqual(data.get('reviewer'), 'Some Reviewer')
        self.assertEqual(Review.objects.count(), 1)

    def test_review_not_found(self):
        request = self._prepare_get_request()
        response = self.view.dispatch(request, pk=1)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
