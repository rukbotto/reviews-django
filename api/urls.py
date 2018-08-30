from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^reviews/$', views.ReviewListView.as_view()),
    url(r'^review/(?P<pk>[0-9]+)/$', views.ReviewDetailView.as_view()),
]
