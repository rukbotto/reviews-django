from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.test.client import FakePayload
from rest_framework import status
from rest_framework.views import APIView

from api.models import Review
from api.views import ReviewListView


class TestReviewListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'user1',
            'user1@example.com',
            'user1_pwd'
        )

        self.data = {
            'title': 'My review',
            'summary': 'This is my first review.',
            'rating': 1,
            'ip_address': '127.0.0.1',
            'company': 'Some Company',
            'reviewer': 'Some Reviewer'
        }

        self.view = ReviewListView()

    def _prepare_request(self, data):
        payload_content = '''
        {{
            "title": "{c[title]}",
            "summary": "{c[summary]}",
            "rating": {c[rating]},
            "ip_address": "{c[ip_address]}",
            "company": "{c[company]}",
            "reviewer": "{c[reviewer]}"
        }}
        '''.format(c=data)

        payload = FakePayload(payload_content)
        request = WSGIRequest({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': '{}'.format(len(payload)),
            'wsgi.input': payload
        })
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        return request

    def test_post_review(self):
        request = self._prepare_request(self.data)
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
        self.assertEqual(data.get('user'), 'user1')
        self.assertEqual(Review.objects.count(), 1)

    def test_post_review_long_title(self):
        self.data['title'] = 'This is a very very very very very very very very very long title'
        request = self._prepare_request(self.data)
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data

        self.assertEqual(len(errors.get('title')), 1)

    def test_post_review_long_summary(self):
        self.data['summary'] = ''.join(['a' for i in range(10001)])
        request = self._prepare_request(self.data)
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data

        self.assertEqual(len(errors.get('summary')), 1)

    def test_post_review_below_zero_rating(self):
        self.data['rating'] = -1
        request = self._prepare_request(self.data)
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data

        self.assertEqual(len(errors.get('rating')), 1)

    def test_post_review_invalid_ip_address(self):
        self.data['ip_address'] = '127,0,0,1'
        request = self._prepare_request(self.data)
        response = self.view.dispatch(request)

        self.assertIsInstance(self.view, APIView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data

        self.assertEqual(len(errors.get('ip_address')), 1)
