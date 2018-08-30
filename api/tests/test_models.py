import re

from django.contrib.auth.models import User
from django.test import TestCase

from api.models import Review


class ReviewModelTests(TestCase):
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

    def test_save_model(self):
        self.review.save()

        self.assertIsNotNone(self.review.id)
        self.assertEqual(self.review.title, 'My review')
        self.assertEqual(self.review.summary, 'This is my first review.')
        self.assertEqual(self.review.rating, 1)
        self.assertEqual(self.review.ip_address, '127.0.0.1')
        self.assertEqual(self.review.company, 'Some Company')
        self.assertEqual(self.review.reviewer, 'Some Reviewer')
        self.assertEqual(self.review.user.username, 'user1')

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
