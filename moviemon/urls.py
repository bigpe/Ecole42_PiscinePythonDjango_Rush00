from django.urls import path
from .views import Main, WorldMap, MoviemonsView, Load, Save, BattleView, MoviemonDetailView, CatchView, WinView

urlpatterns = [
    path('', Main.as_view(), name='main'),
    path("worldmap/", WorldMap.as_view(), name="world_map"),
    path("load/", Load.as_view(), name="load"),
    path("save/", Save.as_view(), name="save"),
    path("battle/<str:imdb_id>/", BattleView.as_view(), name="battle"),
    path('moviemons/', MoviemonsView.as_view(), name='moviemons'),
    path('moviemon/<str:imdb_id>/', MoviemonDetailView.as_view(), name='moviemon_info'),
    path('catch/<str:imdb_id>/', CatchView.as_view(), name='catch'),
    path('win/', WinView.as_view(), name='win')
]
