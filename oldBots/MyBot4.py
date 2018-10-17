#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

from hlt import constants

from hlt.positionals import Direction, Position

import random

import logging

game = hlt.Game()

ship_status = {}

game.ready(__file__)

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

while True:
    game.update_frame()
    
    me = game.me
    game_map = game.game_map

    command_queue = []

    current_moves = [ship.position for ship in me.get_ships()]

    for ship in me.get_ships():
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))

        #ROLE ASSIGNMENT
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"
        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                if game_map.normalize(ship.position+Position(move[0],move[1])) not in current_moves:
                    current_moves.append(game_map.normalize(ship.position+Position(move[0],move[1])))
                    command_queue.append(ship.move(move))
                else:
                    command_queue.append(ship.stay_still())
                continue
        elif ship.halite_amount >= constants.MAX_HALITE / 2:
            ship_status[ship.id] = "returning"
            
        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            move = random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])
            if game_map.normalize(ship.position+Position(move[0],move[1])) not in current_moves:
                    current_moves.append(game_map.normalize(ship.position+Position(move[0],move[1])))
                    command_queue.append(ship.move(move))
            continue
        command_queue.append(ship.stay_still())

    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and me.shipyard.position not in current_moves:
        command_queue.append(me.shipyard.spawn())

    game.end_turn(command_queue)
