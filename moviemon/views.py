import random
from typing import Callable

from django.http import HttpResponse
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
        game_data.dump('session')
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
    context = {'enemy_block': False, 'event': None, 'enemy': None, 'radar': False}

    @get_game
    def get(self, request, game: Game, *args, **kwargs):
        move = request.GET.get('move', None)
        game_data: GameData = game.game_data
        move_on = None
        context = {}
        context.update({'progress': f'{len(game.game_data.captured)}/{len(game.game_data.moviemons)}'})
        if len(game.game_data.captured) == len(game.game_data.moviemons):
            game_data.flush_session()
            # TODO Win logic
        if request.GET.get('flush_state', False):
            self.context.update({'enemy_block': False, 'event': None, 'enemy': None})
        if request.GET.get('escape', False) or request.GET.get('win', False):
            self.context.update({'enemy_block': False, 'enemy': None})
        if move and not self.context['enemy_block']:
            move_on = getattr(game, f'move_{move}', lambda: ...)()
            self.context.update({
                'enemy_block': True if move_on == Tile.Types.enemy else False,
            })

        event_message = None
        if move_on == Tile.Types.ball:
            event_message = 'You get +1 movieball'
        if move_on == Tile.Types.enemy or self.context['enemy_block']:
            event_message = '<div>You find moviemon<br>' \
                            'Press <span>A</span> to start fighting</div>'
        if move_on == Tile.Types.radar:
            event_message = 'You obtain radar, now you see better, for a limited time'
            game_data.activate_radar()
            game_data.show_map()
        if request.GET.get('escape', False):
            event_message = 'You escape from battle'
        if request.GET.get('win', False):
            event_message = 'You obtain new moviemon'
        self.context.update({
            'event': event_message
        })
        if self.context['enemy_block']:
            self.context.update({'enemy': game_data.get_random_movie()})
        self.context['radar'] = True if game_data.radar_moves_count else False
        context.update(game_data.to_data())
        context.update(**self.context)
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


class Save(TemplateView):
    template_name = "save.html"
    context = {"selected": 1}

    @get_game
    def get(self, request, game: Game, *args, **kwargs):
        move = request.GET.get('move', None)
        to_slot = request.GET.get('to_slot', None)
        move_handler = {
            'up': -1,
            'down': +1,
        }

        self.context['selected'] += move_handler.get(move, 0)

        if self.context['selected'] > 3:
            self.context['selected'] = 1
        if self.context['selected'] < 1:
            self.context['selected'] = 3

        if to_slot:
            game.game_data.dump(to_slot)

        self.context.update({'slots': game.game_data.get_slots()})
        return render(request, self.template_name, self.context)


class BattleView(TemplateView):
    template_name = "battle.html"

    @get_game
    def get(self, request, game: Game, imdb_id, *args, **kwargs):
        moviemon = game.game_data.get_movie(imdb_id)
        success_rate = 50 - (moviemon['imdbRating'] * 10) + (game.game_data.get_strength * 5)
        if success_rate <= 0:
            success_rate = 1
        if success_rate >= 100:
            success_rate = 90
        success_rate = int(success_rate)
        context = {
            'enemy': moviemon,
            'movie_balls': game.game_data.movie_balls,
            'message': request.GET.get('message'),
            'strength': game.game_data.get_strength,
            'success_rate': success_rate
        }
        return render(request, self.template_name, context)


class MoviemonsView(TemplateView):
    template_name = "moviemons.html"
    context = {
        'selected': 1,
        'selected_moviemon': Moviemon(),
        'moviemons': [],
        'moviemons_count': 0,
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
        try:
            self.context['selected_moviemon'] = moviemons[self.context['selected'] - 1]
        except IndexError:
            self.context['selected_moviemon'] = moviemons[self.context['selected'] - 2]
        self.context.update({'moviemons': moviemons[self.context['selected'] - 1:len(moviemons)]})
        return render(request, self.template_name, self.context)


class MoviemonDetailView(TemplateView):
    template_name = "moviemon_detail.html"
    context = {}

    @get_game
    def get(self, request, game: Game, imdb_id, *args, **kwargs):
        self.context.update({'selected_moviemon': game.game_data.get_movie(imdb_id)})
        return render(request, self.template_name, self.context)


class CatchView(View):
    @get_game
    def get(self, request, game: Game, imdb_id, *args, **kwargs):
        if game.game_data.movie_balls:
            game.game_data.movie_balls -= 1
            game.game_data.dump('session')
        else:
            return redirect(f'/worldmap/?escape=1')
        enemy = game.game_data.get_movie(imdb_id)
        success_rate = 50 - (enemy['imdbRating'] * 10) + (game.game_data.get_strength * 5)
        if success_rate <= 0:
            success_rate = 1
        if success_rate >= 100:
            success_rate = 90
        success_rate = int(success_rate)
        roll = [True] * success_rate + [False] * (100 - success_rate)
        if random.choice(roll):
            game.game_data.captured.append(enemy)
            game.game_data.dump('session')
            return redirect(f'/worldmap/?win=1')
        return redirect(f'/battle/{imdb_id}/?message=You missed')
