from django.shortcuts import render
from django.views.generic import TemplateView

from .signatures import GameData, Game


class Main(TemplateView):
    template_name = "main.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class WorldMap(TemplateView):
    template_name = "worldmap.html"
    context = {}

    def get(self, request, *args, **kwargs):
        slot = request.GET.get('slot', 'session')
        game_data = GameData().load(slot)
        game = Game(game_data)
        move = request.GET.get('move', None)
        if move:
            getattr(game, f'move_{move}', lambda: ...)()
        self.context.update(game_data.to_data())
        self.context.update({'player_position': game_data.position})
        return render(request, self.template_name, self.context)
