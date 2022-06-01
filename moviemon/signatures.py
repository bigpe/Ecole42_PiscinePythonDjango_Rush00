import glob
import os
import pickle
import random
from dataclasses import dataclass, field
from typing import Tuple, List

import requests
from django.conf import settings


@dataclass
class Tile:
    class Types:
        empty = 'empty'
        enemy = 'enemy'
        ball = 'ball'
        player = 'player'

    type: str
    seen: bool = False


class API:
    base = 'https://www.omdbapi.com'
    _search = f'{base}/?i={{}}'

    def search(self, imdb_id):
        return self.send_request(self.inject_variable(self._search, imdb_id))

    @staticmethod
    def inject_variable(text, *args):
        return text.format(*args)

    @staticmethod
    def send_request(url):
        # key = 'c29c9750'
        key = settings.OMDB_API_KEY
        config = {
            'params': {'apikey': key}
        }
        return requests.get(url, **config).json()


class Moviemon:
    imdbID: str
    Title: str
    Year: str
    Director: str
    Poster: str
    Ratings: List[dict]
    imdbRating: float
    Actors: str

    def __init__(self, **kwargs):
        try:
            self.__dict__.update(**kwargs)
            self.imdbRating = float(self.imdbRating)
        except Exception:
            ...

    def __str__(self):
        return self.Title

    def to_data(self):
        return self.__dict__


def save_path(slot):
    saved_data_folder = settings.BASE_DIR.parent / 'saved_data'
    saved_data_folder.mkdir(exist_ok=True)
    return saved_data_folder / f'slot-{slot}.bin'


@dataclass
class GameData:
    moviemons: List[Moviemon] = field(default_factory=list)
    position: Tuple[int, int] = settings.PLAYER_START_POSITION
    captured: List[str] = field(default_factory=list)
    movie_balls: int = settings.PLAYER_START_MOVIE_BALLS
    map: List[List[Tile]] = field(default_factory=list)
    moves_count = 0

    def load(self, slot):
        try:
            load_data = pickle.load(open(save_path(slot), 'rb'))
        except FileNotFoundError:
            load_data = self.load_default_settings()
        return load_data

    def dump(self, slot):
        pickle.dump(self, open(save_path(slot), 'wb'))

    def get_random_movie(self):
        moviemons_ids = [moviemoon.imdbID for moviemoon in self.moviemons]
        [moviemons_ids.pop(i) if moviemoon in self.captured else ... for i, moviemoon in enumerate(moviemons_ids)]
        random_moviemoon_id = random.choice(moviemons_ids)
        return next(filter(lambda moviemoon: moviemoon.imdbID == random_moviemoon_id, self.moviemons))

    def load_default_settings(self):
        self.generate_map()
        self.load_movies()
        self.create_session()
        return self

    @property
    def get_strength(self):
        return len(self.moviemons)

    def get_movie(self, imdb_id):
        return next(filter(lambda moviemoon: moviemoon.imdbID == imdb_id, self.moviemons)).to_data()

    def generate_map(self):
        map_size = settings.MAP_SIZE
        for i in range(map_size):
            tiles = []
            for j in range(map_size):
                tiles.append(Tile(type=random.choice(
                    [Tile.Types.empty, Tile.Types.ball, Tile.Types.enemy]
                ) if (i, j) != settings.PLAYER_START_POSITION else Tile.Types.player))
            self.map.append(tiles)

    def load_movies(self):
        imdb_list = settings.IMDB_LIST

        self.moviemons = [Moviemon(**API().search(imdb_id)) for imdb_id in imdb_list]

    def create_session(self):
        self.dump('session')

    @staticmethod
    def flush_session():
        if os.path.exists(save_path('session')):
            os.remove(save_path('session'))

    def restore_tile(self, x=None, y=None):
        random_y = random.randint(0, settings.MAP_SIZE - 1) if y is None else y
        random_x = random.randint(0, settings.MAP_SIZE - 1) if x is None else x

        if self.map[random_y][random_x].type != Tile.Types.empty:
            return self.restore_tile()
        self.map[random_y][random_x] = random.choice([Tile(Tile.Types.ball), Tile(Tile.Types.enemy)])
        self.dump('session')

    def get_slots(self):
        slots = [slot.split('/')[-1] for slot in glob.glob(str(save_path('session').parent / 'slot-*.bin'))]
        slots = list(filter(lambda slot: 'session' not in slot, slots))
        slots_ids = [slot.replace('slot-', '').replace('.bin', '') for slot in slots]
        slots = {
            '1': {'number': 1, 'progress': None},
            '2': {'number': 2, 'progress': None},
            '3': {'number': 3, 'progress': None},
        }
        for slot in slots_ids:
            slot_data: GameData = self.load(slot)
            slots[slot]['progress'] = f'{len(slot_data.moviemons) / len(slot_data.captured)}'
        slots = [slots[slot] for slot in slots]
        return slots

    def to_data(self):
        return {
            'map': [[x_tile.type for x_tile in y_tile] for y_tile in self.map],
            'movie_balls': self.movie_balls,
        }


class Game:
    def __init__(self, game_data):
        self.game_data: GameData = game_data

    def move(self, to_y=0, to_x=0):
        move_on = None
        y, x = self.game_data.position
        if y + to_y < 0 or x + to_x < 0:
            return
        try:
            move_on = self.game_data.map[y + to_y][x + to_x].type
            if move_on == Tile.Types.ball:
                self.game_data.movie_balls += 1
            self.game_data.map[y + to_y][x + to_x] = Tile(type=Tile.Types.player)
            self.game_data.map[y][x] = Tile(type=Tile.Types.empty)
            self.game_data.position = (y + to_y, x + to_x)
            self.game_data.moves_count += 1
            self.game_data.dump('session')
            if not self.game_data.moves_count % 5:
                self.game_data.restore_tile()
        except IndexError:
            ...
        return move_on

    def move_left(self):
        return self.move(to_x=-1)

    def move_right(self):
        return self.move(to_x=1)

    def move_up(self):
        return self.move(to_y=-1)

    def move_down(self):
        return self.move(to_y=1)
