import math, sys
from random import random
from .roomList import names
from adventure.models import Room

class World:
    def __init__(self):
        self.rooms = []
        self.players = ()

    def generate_rooms(self, count):
        start_room = Room(
            title = 'Foyer',
            description = 'A dingy foyer where the floor is filled with torn papers of an unknown book. What happened here?'
        )
        start_room.save()
        current_room = start_room

        # create rooms by looping up to count number
        for i in range(1, count):
            random_room = names[math.floor(len(names) * random())]
            # Create room
            new_room = Room(
                title = random_room[0],
                description = random_room[1],
                w_to = current_room.id
            )
            new_room.save()
            # mark new_to as next room
            current_room.connectRooms(new_room, 'e')
            # change current_room
            current_room = new_room

        print(f"{count} rooms created. Enjoy!")

    def player_tracker(self, user):
        if players[user]:
            players.append(user)
        return len(players)