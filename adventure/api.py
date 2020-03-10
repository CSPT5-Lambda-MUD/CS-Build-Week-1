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
        
        room_count = 1
        dirs = ["n", "s", "e", "w"]
        previous_room = None

        # These can be modified to change generation pattern
        # min_sides_available checks if there are at least two directions we can go from current room
        min_sides_available = 2
        start_x = size_x // 2
        start_y = size_y // 2

        ##################################################

        # Initialize the grid
        def init_world():
            # pull our variables from parent function
            nonlocal previous_room
            nonlocal room_count
            nonlocal start_x
            nonlocal start_y
            
            # Room.objects.all().delete()

            # Make our grid
            self.grid = [None] * size_y
            self.width = size_x
            self.height = size_y
            for i in range( len(self.grid) ):
                self.grid[i] = [None] * size_x

            # Start at 2 because we already have an initial room created
            room_count = 1

            # Create starter room
            room = Room(id=1, title="Starting room", description="First room", x=start_x, y=start_y)
            room.save()
            self.grid[start_y][start_x] = room
            previous_room = room
        
        ##################################################

        # Create our grid
        init_world()

        ##################################################

        # Takes in x, y and checks how make availble
        # spots there are around x,y position on our grid
        # returns how many spots are found
        def check_spots_around(x, y):
            good_spots = 0

            # north
            if y + 1 < size_y - 1 and self.grid[y + 1][x] == None:
                good_spots += 1
            # south
            if y - 1 > 0 and self.grid[y - 1][x] == None:
                good_spots += 1
            # east
            if x + 1 < size_x - 1 and self.grid[y][x + 1] == None:
                good_spots += 1
            # west
            if x - 1 > 0 and self.grid[y][x - 1] == None:
                good_spots += 1
            
            return good_spots
        
        ##################################################

        # Takes in x, y and a direction to check if
        # we can place a room at this position + 1 in direction
        def check_valid_spot(direct, x, y):
            # north
            if direct == "n" and y + 1 < size_y - 1:
                if self.grid[y + 1][x] == None:
                    return True
            # south    
            elif direct == "s" and y - 1 > 0:
                if self.grid[y - 1][x] == None:
                    return True
            # east
            elif direct == "e" and x + 1 < size_x - 1:
                if self.grid[y][x + 1] == None:
                    return True
            # west
            elif direct == "w" and x - 1 > 0:
                if self.grid[y][x - 1] == None:
                    return True
            
            return False

        ##################################################
        
        # Takes in x,y position and goes 1 space in the direction
        # and places room in that spot
        def create_new_room(x, y, direct, title, desc):
            nonlocal previous_room
            
            if direct == "n":
                new_room = Room(id=room_count, title=title, description=desc, x=x, y=y + 1)
            elif direct == "s":
                new_room = Room(id=room_count, title=title, description=desc, x=x, y=y - 1)
            elif direct == "e":
                new_room = Room(id=room_count, title=title, description=desc, x=x + 1, y=y)
            elif direct == "w":
                new_room = Room(id=room_count, title=title, description=desc, x=x - 1, y=y)
            
            new_room.save()
            self.grid[new_room.y][new_room.x] = new_room

            # Connect this room to the previous one
            # so we can go back and forth
            old_room_dir = ""
            if direct == "n":
                old_room_dir = "s"

            if direct == "s":
                old_room_dir = "n"

            if direct == "e":
                old_room_dir = "w"

            if direct == "w":
                old_room_dir = "e"
            
            # Connect rooms in each direction
            new_room.connectRooms(previous_room, old_room_dir)
            previous_room.connectRooms(new_room, direct)

            # new room is now previous_room next loop
            previous_room = new_room
            
        ##################################################
        ##################################################
        ##################################################
        
        # While loop to generate num_rooms amount of rooms
        print("Generating map, this may take a minute...")
        while room_count < num_rooms:
            # self.print_rooms()
            
            # Keep track of attempts made to find a random space
            finding_space = True
            dirs_tried = []

            while finding_space:
                
                # Choose a direction at random
                rand_dir = random.choice(dirs)

                # If there are three or more directions in our tried list, that means there are no more directions left to try
                # we check for 3 because 1 is assumed to be taken by the previous room, we subtract that from our 4 directions
                if len(dirs_tried) >= 3:
                    init_world()
                    break
                
                # Check if random direction has already been tried
                # if so, loop again and get another rand_dir
                if rand_dir in dirs_tried:
                    continue

                
                # Check direction and check if valid [y][x] positition
                # since we are generating a room north, check if we can move any higher on the grid
                if rand_dir == "n":
                    # Check if there is room here
                    if check_valid_spot(rand_dir, previous_room.x, previous_room.y) == True:
                        # If so, check if we have a minimum available spots to create a room
                        if check_spots_around(previous_room.x, previous_room.y + 1) < min_sides_available:
                            # If the minimum spots are not available, this is not a valid direction
                            # Add rand_dir to our dirs_tried list so we don't attempt it again
                            dirs_tried.append(rand_dir)
                            continue
                    else:
                        # If this wasn't a valid direction, add it to our attempted list
                        dirs_tried.append(rand_dir)
                        continue
                

                    # If empty, create room at [y + 1][x]
                    create_new_room(previous_room.x, previous_room.y, rand_dir, "Northern Room", "Room to the north")
                    
                    # We found a space so stop looking
                    finding_space = False
                    continue

                # Same as above
                if rand_dir == "s":
                    if check_valid_spot(rand_dir, previous_room.x, previous_room.y) == True:
                        if check_spots_around(previous_room.x, previous_room.y - 1) < min_sides_available:
                            dirs_tried.append(rand_dir)
                            continue
                    else:
                        dirs_tried.append(rand_dir)
                        continue

                    # If empty, create room at [y + 1][x]
                    create_new_room(previous_room.x, previous_room.y, rand_dir, "Southern Room", "Room to the south")
                    
                    # We found a space so stop looking
                    finding_space = False
                    continue

                if rand_dir == "e":
                    if check_valid_spot(rand_dir, previous_room.x, previous_room.y) == True:
                        if check_spots_around(previous_room.x + 1, previous_room.y) < min_sides_available:
                            dirs_tried.append(rand_dir)
                            continue
                    else:
                        dirs_tried.append(rand_dir)
                        continue

                    # If empty, create room at [y + 1][x]
                    create_new_room(previous_room.x, previous_room.y, rand_dir, "Eastern Room", "Room to the east")
                    
                    # We found a space so stop looking
                    finding_space = False
                    continue

                if rand_dir == "w":
                    if check_valid_spot(rand_dir, previous_room.x, previous_room.y) == True:
                        if check_spots_around(previous_room.x - 1, previous_room.y) < min_sides_available:
                            dirs_tried.append(rand_dir)
                            continue
                    else:
                        dirs_tried.append(rand_dir)
                        continue

                    # If empty, create room at [y + 1][x]
                    create_new_room(previous_room.x, previous_room.y, rand_dir, "Western Room", "Room to the west")
                    
                    # We found a space so stop looking
                    finding_space = False
                    continue

            
            # Added a room so we increase our count
            room_count += 1

        ##################################################
        ##################################################
        ##################################################
            

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
num_rooms = 100
width = 20
height = 20
w.generate_rooms(width, height, num_rooms)
w.print_rooms()

players=Player.objects.all()
for p in players:
  p.currentRoom=Room.objects.first().id
  p.save()


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
        return JsonResponse({'name':player.user.username, 'room_id': nextRoom.id,'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'room_id': room.id, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)

@csrf_exempt
@api_view(["GET"])
def room(request):
    reverse_grid = list(w.grid)
    reverse_grid.reverse()
    new_list = []
    for x in range(len(reverse_grid)):
        for y in range(len(reverse_grid[x])):
            if reverse_grid[x][y] != None:
                if request.user.player.currentRoom == reverse_grid[x][y].id:
                    new_list.append({
                        "name": reverse_grid[x][y].title,
                        "n" : reverse_grid[x][y].n_to,
                        "s" : reverse_grid[x][y].s_to,
                        "e" : reverse_grid[x][y].e_to,
                        "w" : reverse_grid[x][y].w_to,
                        "x" : reverse_grid[x][y].x,
                        "y" : reverse_grid[x][y].y,
                        "current_room": True
                    })
                else:
                    new_list.append({
                        "name": reverse_grid[x][y].title,
                        "n" : reverse_grid[x][y].n_to,
                        "s" : reverse_grid[x][y].s_to,
                        "e" : reverse_grid[x][y].e_to,
                        "w" : reverse_grid[x][y].w_to,
                        "x" : reverse_grid[x][y].x,
                        "y" : reverse_grid[x][y].y,
                        "current_room": False
                })
            else:
                new_list.append("0")
    return JsonResponse({'rooms': new_list}, safe=True)

