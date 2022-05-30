from django.urls import path
from .views import Main, WorldMap, Select

urlpatterns = [
    path('', Main.as_view(), name='main'),
    path("worldmap/", WorldMap.as_view(), name="world_map"),
    path('select/', Select.as_view(), name='select')
]
