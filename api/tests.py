import re
from django.test import TestCase

from api.models import Review


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
