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
        self.__dict__.update(**kwargs)
        self.imdbRating = float(self.imdbRating)

    def __str__(self):
        return self.Title

    def to_data(self):
        return self.__dict__


@dataclass
class GameData:
    moviemons: List[Moviemon] = field(default_factory=list)
    position: Tuple[int, int] = settings.PLAYER_START_POSITION
    captured: List[str] = field(default_factory=list)
    movie_balls: int = settings.PLAYER_START_MOVIE_BALLS
    map: List[List[Tile]] = field(default_factory=list)

    def load(self, slot):
        try:
            load_data = pickle.load(open(self.save_path(slot), 'rb'))
        except FileNotFoundError:
            load_data = self.load_default_settings()
        return load_data

    def dump(self, slot):
        pickle.dump(self, open(self.save_path(slot), 'wb'))

    @staticmethod
    def save_path(slot):
        saved_data_folder = settings.BASE_DIR.parent / 'saved_data'
        saved_data_folder.mkdir(exist_ok=True)
        return saved_data_folder / f'slot-{slot}.bin'

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
        # map_size = 10
        for i in range(map_size):
            tiles = []
            for j in range(map_size):
                tiles.append(Tile(type=random.choice(
                    [Tile.Types.empty, Tile.Types.ball, Tile.Types.enemy]
                ) if (i, j) != settings.PLAYER_START_POSITION else Tile.Types.player))
            self.map.append(tiles)

    def load_movies(self):
        # IMDB_LIST = [
        #     "tt0468492",
        #     "tt5034838",
        # ]
        imdb_list = settings.IMDB_LIST

        self.moviemons = [Moviemon(**API().search(imdb_id)) for imdb_id in imdb_list]

    def create_session(self):
        self.dump('session')

    def to_data(self):
        return {
            'map': [[x_tile.type for x_tile in y_tile] for y_tile in self.map],
            'movie_balls': self.movie_balls,
        }


class Game:
    def __init__(self, game_data):
        self.game_data: GameData = game_data

    def move_left(self):
        y, x = self.game_data.position
        if x:
            self.game_data.map[y][x] = Tile(type=Tile.Types.empty)
            self.game_data.map[y][x - 1] = Tile(type=Tile.Types.player)
            self.game_data.position = (y, x - 1)
            self.game_data.dump('session')

    def move_right(self):
        y, x = self.game_data.position
        if x != settings.MAP_SIZE - 1:
            self.game_data.map[y][x] = Tile(type=Tile.Types.empty)
            self.game_data.map[y][x + 1] = Tile(type=Tile.Types.player)
            self.game_data.position = (y, x + 1)
            self.game_data.dump('session')

    def move_up(self):
        y, x = self.game_data.position
        if y:
            self.game_data.map[y][x] = Tile(type=Tile.Types.empty)
            self.game_data.map[y - 1][x] = Tile(type=Tile.Types.player)
            self.game_data.position = (y - 1, x)
            self.game_data.dump('session')

    def move_down(self):
        y, x = self.game_data.position
        if y != settings.MAP_SIZE - 1:
            self.game_data.map[y][x] = Tile(type=Tile.Types.empty)
            self.game_data.map[y + 1][x] = Tile(type=Tile.Types.player)
            self.game_data.position = (y + 1, x)
            self.game_data.dump('session')
