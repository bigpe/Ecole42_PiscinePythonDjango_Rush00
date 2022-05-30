from typing import Callable

from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .signatures import GameData, Game, Tile


def get_game(f: Callable):
    def wrapper(self, request, *args, **kwargs):
        slot = request.GET.get('slot', 'session')
        game_data = GameData().load(slot)
        game = Game(game_data)
        return f(self, request, game, *args, **kwargs)

    return wrapper


class Main(TemplateView):
    template_name = "main.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class Select(TemplateView):
    template_name = "select.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class WorldMap(TemplateView):
    template_name = "worldmap.html"
    context = {}

    @get_game
    def get(self, request, game: Game, *args, **kwargs):
        move = request.GET.get('move', None)
        game_data: GameData = game.game_data
        if move:
            move_on = getattr(game, f'move_{move}', lambda: ...)()
            if move_on == Tile.Types.enemy:
                ...
                # TODO Redirect battle
        self.context.update(game_data.to_data())
        return render(request, self.template_name, self.context)
