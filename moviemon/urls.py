from django.urls import path
from .views import Main, WorldMap, MoviemonsView, Load, Battle, MoviemonDetailView, NewGameView

urlpatterns = [
    path('', Main.as_view(), name='main'),
    path("worldmap/", WorldMap.as_view(), name="world_map"),
    path("load/", Load.as_view(), name="load"),
    path("battle/<str:imdb_id>/", Battle.as_view(), name="battle"),
    path('moviemons/', MoviemonsView.as_view(), name='moviemons'),
    path('moviemon/<str:imdb_id>/', MoviemonDetailView.as_view(), name='moviemon_info'),
    path('new_game/', NewGameView.as_view(), name='new_game'),
]
