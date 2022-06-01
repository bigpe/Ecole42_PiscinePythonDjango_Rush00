from typing import Callable

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View

from .signatures import GameData, Game, Tile, Moviemon


def get_game(f: Callable):
    def wrapper(self, request, *args, **kwargs):
        slot = request.GET.get('slot', 'session')
        new_game = request.GET.get('new_game', False)
        if new_game:
            GameData.flush_session()
        game_data = GameData().load(slot)
        game = Game(game_data)
        return f(self, request, game, *args, **kwargs)

    return wrapper


class Main(TemplateView):
    template_name = "main.html"
    context = {'selected': 1}

    def get(self, request, *args, **kwargs):
        move = request.GET.get('move', None)
        move_handler = {
            'up': -1,
            'down': +1,
        }

        self.context['selected'] += move_handler.get(move, 0)

        if self.context['selected'] > 2:
            self.context['selected'] = 1
        if self.context['selected'] < 1:
            self.context['selected'] = 2

        return render(request, self.template_name, self.context)


class WorldMap(TemplateView):
    template_name = "worldmap.html"
    context = {'enemy_block': False, 'event': None, 'enemy': None}

    @get_game
    def get(self, request, game: Game, *args, **kwargs):
        move = request.GET.get('move', None)
        game_data: GameData = game.game_data
        move_on = None
        context = {}
        new_game = request.GET.get('new_game', False)
        if new_game:
            self.context = {'enemy_block': False, 'event': None, 'enemy': None}
        if self.context.get('enemy_block', False) and game_data.moves_count:
            context.update(game_data.to_data())
            context.update(self.context)
            return render(request, self.template_name, context)
        if move:
            move_on = getattr(game, f'move_{move}', lambda: ...)()
        context.update(game_data.to_data())
        self.context.update({
            'enemy_block': True if move_on == Tile.Types.enemy else False,
        })

        event_message = None
        if move_on == Tile.Types.ball:
            event_message = 'Your get +1 movieball'
        if move_on == Tile.Types.enemy:
            event_message = '<div>Your find moviemon<br>' \
                            'Press <span>A</span> to start fighting</div>'
        self.context.update({
            'event': event_message
        })
        if self.context['enemy_block']:
            self.context.update({'enemy': game_data.get_random_movie()})
        context.update(self.context)
        return render(request, self.template_name, context)


class Load(TemplateView):
    template_name = "load.html"
    context = {"selected": 1}

    @get_game
    def get(self, request, game: Game, *args, **kwargs):
        move = request.GET.get('move', None)
        move_handler = {
            'up': -1,
            'down': +1,
        }

        self.context['selected'] += move_handler.get(move, 0)

        if self.context['selected'] > 3:
            self.context['selected'] = 1
        if self.context['selected'] < 1:
            self.context['selected'] = 3

        self.context.update({'slots': game.game_data.get_slots()})
        return render(request, self.template_name, self.context)


class BattleView(TemplateView):
    template_name = "battle.html"

    @get_game
    def get(self, request, game: Game, imdb_id, *args, **kwargs):
        moviemon = game.game_data.get_movie(imdb_id)
        context = {'enemy': moviemon, 'movie_balls': game.game_data.movie_balls}
        return render(request, self.template_name, context)


class MoviemonsView(TemplateView):
    template_name = "moviemons.html"
    context = {
        'selected': 1,
        'selected_moviemon': Moviemon(),
        'moviemons': [],
        'moviemons_count': 0
    }

    @get_game
    def get(self, request, game: Game, *args, **kwargs):
        move = request.GET.get('move', None)
        move_handler = {
            'left': -1,
            'right': +1,
        }

        moviemons = game.game_data.captured

        self.context['moviemons_count'] = len(moviemons)
        if not moviemons:
            return render(request, self.template_name, self.context)

        if self.context['selected'] >= len(moviemons):
            self.context['selected'] = 0
        elif self.context['selected'] < 1:
            self.context['selected'] = len(moviemons)

        self.context['selected'] += move_handler.get(move, 0)
        self.context['selected_moviemon'] = moviemons[self.context['selected'] - 1]
        self.context.update({'moviemons': moviemons[self.context['selected'] - 1:len(moviemons)]})
        return render(request, self.template_name, self.context)


class MoviemonDetailView(TemplateView):
    template_name = "moviemon_detail.html"
    context = {}

    @get_game
    def get(self, request, game: Game, imdb_id, *args, **kwargs):
        self.context.update({'selected_moviemon': game.game_data.get_movie(imdb_id)})
        return render(request, self.template_name, self.context)
