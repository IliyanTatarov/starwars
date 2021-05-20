from typing import Collection
from django.urls import path

from .views import CollectionListView, CollectionDetailView, CollectionAggregateView, CollectionNewView

app_name = 'characters'
urlpatterns = [
    path('', CollectionListView.as_view(), name='homepage'),
    path('retrieve/', CollectionNewView.as_view(), name='retrieve'),
    path('<int:pk>/', CollectionDetailView.as_view(), name='collection'),
    path('<int:pk>/aggregate/', CollectionAggregateView.as_view(), name='aggregate'),
]
