from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Review
from api.serializers import ReviewSerializer


class ReviewListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = ReviewSerializer(request.user.reviews.all(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            review = Review.objects.get(pk=kwargs['pk'])
            if request.user != review.user:
                return Response({}, status.HTTP_403_FORBIDDEN)
        except Review.DoesNotExist:
            raise Http404
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
