from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from adventure.models import *
from rest_framework.decorators import api_view
import json
import random



class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0

    def generate_rooms(self, size_x, size_y, num_rooms):
        '''
        Fill up the grid, bottom to top, in a zig-zag pattern
        '''

        # Initialize the grid
        self.grid = [None] * size_y
        self.width = size_x
        self.height = size_y
        for i in range( len(self.grid) ):
            self.grid[i] = [None] * size_x
        
        dirs = ["n", "s", "e", "w"]

        # Start in center of generated grid
        x = size_x // 2 
        y = size_y // 2

        # Start at 1 because we already have an initial room created
        room_count = 1

        # Start with room at the center of the grid
        room = Room(id=0, title="Starting room", description="First room", x=x, y=y)
        room.save()
        self.grid[y][x] = room
        previous_room = room

        # While loop to generate num_rooms amount of rooms
        while room_count < num_rooms:

            # While loop to find a place to put a new room
            finding_space = True
            while finding_space:

                # Choose a direction at random
                rand_dir = random.choice(dirs)
                
                # Check direction and check if valid [y][x] positition
                # since we are generating a room north, check if we can move any higher on the grid
                if rand_dir == "n" and previous_room.y + 1 < size_y - 1:
                    
                    # Check if space is empty
                    if self.grid[previous_room.y + 1][previous_room.x] == None:
                        # If empty, create room at [y + 1][x]
                        new_room = Room(id=room_count, title="Northern Room", description="Room to the north", x=previous_room.x, y=previous_room.y + 1)
                        new_room.save()
                        self.grid[new_room.y][new_room.x] = new_room

                        # Connect this room to the previous one
                        previous_room.connectRooms(new_room, rand_dir)
                        previous_room = new_room
                        
                        # We found a space so stop looking
                        finding_space = False

                # Same as above
                elif rand_dir == "s" and previous_room.y - 1 > 0:

                    if self.grid[previous_room.y - 1][previous_room.x] == None:
                        new_room = Room(id=room_count, title="Southern Room", description="Room to the south", x=previous_room.x, y=previous_room.y - 1)
                        new_room.save()
                        self.grid[new_room.y][new_room.x] = new_room
                        previous_room.connectRooms(new_room, rand_dir)
                        previous_room = new_room
                        finding_space = False

                elif rand_dir == "e" and previous_room.x + 1 < size_x - 1:

                    if self.grid[previous_room.y][previous_room.x + 1] == None:
                        new_room = Room(id=room_count, title="Eastern Room", description="Room to the east", x=previous_room.x + 1, y=previous_room.y)
                        new_room.save()
                        self.grid[new_room.y][new_room.x] = new_room
                        previous_room.connectRooms(new_room, rand_dir)
                        previous_room = new_room
                        finding_space = False

                elif rand_dir == "w" and previous_room.x -1 > 0:

                    if self.grid[previous_room.y][previous_room.x - 1] == None:
                        new_room = Room(id=room_count, title="Western Room", description="Room to the west", x=previous_room.x - 1, y=previous_room.y)
                        new_room.save()
                        self.grid[new_room.y][new_room.x] = new_room
                        previous_room.connectRooms(new_room, rand_dir)
                        previous_room = new_room
                        finding_space = False
                        
            # Added a room so we increase our count
            room_count += 1
            

    def print_rooms(self):
        '''
        Print the rooms in room_grid in ascii characters.
        '''

        # Add top border
        str = "# " * ((3 + self.width * 5) // 2) + "\n"

        # The console prints top to bottom but our array is arranged
        # bottom to top.
        #
        # We reverse it so it draws in the right direction.
        reverse_grid = list(self.grid) # make a copy of the list
        reverse_grid.reverse()
        for row in reverse_grid:
            # PRINT NORTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.n_to is not None:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"
            # PRINT ROOM ROW
            str += "#"
            for room in row:
                if room is not None and room.w_to is not None:
                    str += "-"
                else:
                    str += " "
                if room is not None:
                    str += f"{room.id}".zfill(3)
                else:
                    str += "   "
                if room is not None and room.e_to is not None:
                    str += "-"
                else:
                    str += " "
            str += "#\n"
            # PRINT SOUTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.s_to is not None:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"

        # Add bottom border
        str += "# " * ((3 + self.width * 5) // 2) + "\n"

        # Print string
        print(str)

w = World()
num_rooms = 10
width = 20
height = 20
w.generate_rooms(width, height, num_rooms)
w.print_rooms()


# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)


@csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = request.data
    direction = data['direction']
    room = player.room()
    print(room.id)
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to

    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)

@csrf_exempt
@api_view(["GET"])
def room(request):
    new_list = []
    for x in range(len(w.grid)):
        for y in range(len(w.grid[x])):
            if w.grid[x][y] != None:
                if request.user.player.currentRoom == w.grid[x][y].id:
                    new_list.append({
                        "name": w.grid[x][y].title,
                        "n" : w.grid[x][y].n_to,
                        "s" : w.grid[x][y].s_to,
                        "e" : w.grid[x][y].e_to,
                        "w" : w.grid[x][y].w_to,
                        "x" : w.grid[x][y].x,
                        "y" : w.grid[x][y].y,
                        "current_room": True
                    })
                else:
                    new_list.append({
                        "name": w.grid[x][y].title,
                        "n" : w.grid[x][y].n_to,
                        "s" : w.grid[x][y].s_to,
                        "e" : w.grid[x][y].e_to,
                        "w" : w.grid[x][y].w_to,
                        "x" : w.grid[x][y].x,
                        "y" : w.grid[x][y].y,
                        "current_room": False
                })
            else:
                new_list.append("0")

    new_list.reverse()
    return JsonResponse({'rooms': new_list}, safe=True)

