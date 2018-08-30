from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.test.client import FakePayload
from rest_framework import status
from rest_framework.views import APIView

from api.models import Review
from api.views import ReviewDetailView

class TestReviewDetailView(TestCase):
    def setUp(self):
        self.user_john = User.objects.create_user(
            'john',
            'john@example.com',
            'john_pwd'
        )

        self.user_fred = User.objects.create_user(
            'fred',
            'fred@example.com',
            'fred_pwd'
        )

        self.review_by_john = Review(
            title='My review',
            summary='This is my first review.',
            rating=1,
            ip_address='127.0.0.1',
            company='Some Company',
            reviewer='Some Reviewer',
            user=self.user_john,
        )

        self.view = ReviewDetailView()

    def _prepare_get_request(self, user=None):
        payload = FakePayload('')
        request = WSGIRequest({
            'REQUEST_METHOD': 'GET',
            'CONTENT_LENGTH': 0,
            'wsgi.input': payload
        })
        if user:
            request.user = user
        request._dont_enforce_csrf_checks = True
        return request

    def test_get_review(self):
        self.review_by_john.save()

        request = self._prepare_get_request(self.user_john)
        response = self.view.dispatch(request, pk=self.review_by_john.id)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertIsNotNone(data.get('id'))
        self.assertEqual(data.get('title'), 'My review')
        self.assertEqual(data.get('summary'), 'This is my first review.')
        self.assertEqual(data.get('rating'), 1)
        self.assertFalse('ip_address' in data)
        self.assertEqual(data.get('company'), 'Some Company')
        self.assertEqual(data.get('reviewer'), 'Some Reviewer')
        self.assertEqual(data.get('user'), 'john')
        self.assertEqual(Review.objects.count(), 1)

    def test_get_review_not_found(self):
        request = self._prepare_get_request(self.user_john)
        response = self.view.dispatch(request, pk=1)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_review_forbidden(self):
        self.review_by_john.save()

        request = self._prepare_get_request(self.user_fred)
        response = self.view.dispatch(request, pk=self.review_by_john.id)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_review_anon_user(self):
        self.review_by_john.save()

        request = self._prepare_get_request()
        response = self.view.dispatch(request, pk=self.review_by_john.id)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
