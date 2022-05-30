from django.urls import path
from .views import Main, WorldMap, Select, Load, Battle

urlpatterns = [
    path('', Main.as_view(), name='main'),
    path("worldmap/", WorldMap.as_view(), name="world_map"),
    path("load/", Load.as_view(), name="load"),
    path("battle/<str:imdb_id>/", Battle.as_view(), name="battle"),
    path('select/', Select.as_view(), name='select'),
]
