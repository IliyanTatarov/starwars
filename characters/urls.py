from typing import Collection
from django.urls import path

from .views import CollectionListView, NewCollectionView

app_name = 'characters'
urlpatterns = [
    path('', CollectionListView.as_view(), name='homepage'),
    path('retrieve/', NewCollectionView.as_view(), name='retrieve'),
]
