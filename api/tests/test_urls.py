from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from rest_framework import status

from api.models import Review


class TestUrls(TestCase):
    def setUp(self):
        self.user_john = User.objects.create_user(
            'john',
            'john@example.com',
            'john_pwd'
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
        self.review_by_john.save()

        self.client = Client()

    def test_post_review_url(self):
        data = {
            'title': 'My review',
            'summary': 'This is my first review.',
            'rating': 1,
            'ip_address': '127.0.0.1',
            'company': 'Some Company',
            'reviewer': 'Some Reviewer'
        }

        self.client.login(username='john', password='john_pwd')
        response = self.client.post(
            '/api/reviews/',
            data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertIsNotNone(data.get('id'))
        self.assertEqual(data.get('user'), 'john')

    def test_get_reviews_url(self):
        self.client.login(username='john', password='john_pwd')
        response = self.client.get('/api/reviews/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)

    def test_get_review_url(self):
        self.client.login(username='john', password='john_pwd')
        response = self.client.get('/api/review/{}/'.format(self.review_by_john.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIsNotNone(data.get('id'))
        self.assertEqual(data.get('user'), 'john')
