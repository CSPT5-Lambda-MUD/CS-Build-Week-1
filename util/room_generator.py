from random import random
from math
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
        rooms = []
        players = ()

    def generate_rooms(self, count):
        count_iter = count
        create_start_room = Room(1, 'Foyer', 'A dingy foyer where the floor is filled with torn papers of an unknown book. What happened here?', None, None, None, None, None)
        count_iter -= 1
        current_room = create_start_room

        print('testing')

        # create rooms by looping up to count number
        for i in range(count_iter):
            random_numb = random()
            # Create room
            new_room = Room(i + 1, room.get(room[math.floor(i * random_numb)]), room[math.floor(i // random_numb)], None, None, current_room, None, None)
            # insert room to world
            self.room.append(new_room)
            # increment counter - 1
            count_iter -= 1
            # change current_room
            current_room = new_room

    def player_tracker(self, user):
        if players[user]:
            players.append(user)
        return len(players)