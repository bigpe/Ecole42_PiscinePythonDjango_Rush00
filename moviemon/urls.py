from django.urls import path
from .views import Main, WorldMap, Load

urlpatterns = [
    path('', Main.as_view(), name='main'),
    path("worldmap/", WorldMap.as_view(), name="world_map"),
    path("load/", Load.as_view(), name="load"),
]
