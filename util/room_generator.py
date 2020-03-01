from random import random
import math
from .roomList import names

class Room:
    def __init__(self, id, name, description, secret, n_room, e_room, s_room, w_room):
        self.id = id
        self.name = name
        self.description = description
        self.secret = secret
        self.n_room = n_room
        self.e_room = e_room
        self.s_room = s_room
        self.w_room = w_room

    def __str__(self):
        print(f'${self.name} is ${self.description}')

    def connect_room(self, to_room, dir):
        # direction = dir + '_room'
        # self.direction = to_room
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        reverse_dir = reverse_dirs[dir]
        setattr(self, f"{dir}_to", connecting_room)
        setattr(connecting_room, f"{reverse_dir}_to", self)

class World:
    def __init__(self):
        self.rooms = []
        self.players = ()

    def generate_rooms(self, count):
        start_room = Room(0, 'Foyer', 'A dingy foyer where the floor is filled with torn papers of an unknown book. What happened here?', None, None, None, None, None)
        # count_iter -= 1
        current_room = start_room

        # create rooms by looping up to count number
        for i in range(1, count):
            random_numb = random()
            # Create room
            new_room = Room(i, names[math.floor(i * random_numb)][0], names[math.floor(i // random_numb)][1], None, None, current_room, None, None)
            # insert room to world
            self.rooms.append(new_room)
            # change current_room
            current_room = new_room

    def player_tracker(self, user):
        if players[user]:
            players.append(user)
        return len(players)