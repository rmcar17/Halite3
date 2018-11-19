import hlt
from hlt import constants
from hlt.positionals import Direction, Position
import random
import logging as log
from time import time

game = hlt.Game()

collectors = []
returners = []
explorers = []

game.ready(__file__)

log.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

while True:
    game.update_frame()
    now = time()

    me = game.me
    game_map = game.game_map

    alive_ids = set()
    
    #DECIDE ROLES
    ships = me.get_ships()
    for ship in ships:
        ship_id = ship.id
        alive_ids.add(ship_id)
        if ship_id not in (explorers + returners + collectors):
            explorers.append(ship_id)
        if (ship_id in explorers and game_map[ship.position].halite_amount > constants.MAX_HALITE / 10) or (ship_id not in collectors and ship.halite_amount < constants.MOVE_COST_RATIO * game_map[ship.position].halite_amount):
            if ship_id in explorers:
                explorers.remove(ship_id)
            else:
                returners.remove(ship_id)
            collectors.append(ship_id)
        elif (ship_id in returners and ship.position == me.shipyard.position) or (ship_id in collectors and game_map[ship.position].halite_amount < constants.MAX_HALITE / 10):
            if ship_id in collectors:
                collectors.remove(ship_id)
            else:
                returners.remove(ship_id)
            explorers.append(ship_id)
        elif ship_id in collectors and ship.halite_amount >= constants.MAX_HALITE / 2:
            collectors.remove(ship_id)
            returners.append(ship_id)
    #REMOVE DEAD SHIPS
    collectors = list(set(collectors) & alive_ids)
    returners = list(set(returners) & alive_ids)
    explorers = list(set(explorers) & alive_ids)
    
    
    #MOVE
    current_moves = []
    command_queue = []

    for s_id in collectors:
        ship = me.get_ship(s_id)
        current_moves.append(ship.position)
        command_queue.append(ship.stay_still())
    
    for s_id in returners:
        ship = me.get_ship(s_id)
        move = game_map.naive_navigate(ship, me.shipyard.position)
        new_position = game_map.normalize(ship.position+Position(move[0],move[1]))
        if new_position not in current_moves:
            current_moves.append(new_position)
            command_queue.append(ship.move(move))
        else:
            current_moves.append(ship.position)
            command_queue.append(ship.stay_still())
    
    for s_id in explorers:
        ship = me.get_ship(s_id)
        found_move = False
        moves = [Direction.North, Direction.South, Direction.East, Direction.West]
        random.shuffle(moves)
        for move in moves:
            new_position = game_map.normalize(ship.position+Position(move[0],move[1]))
            if new_position not in current_moves:
                found_move = True
                break
        if found_move:
            current_moves.append(new_position)
            command_queue.append(ship.move(move))
        else:
            current_moves.append(ship.position)
            command_queue.append(ship.stay_still())
        
    log.info(current_moves)
    #SPAWN SHIPS
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and me.shipyard.position not in current_moves:
        command_queue.append(me.shipyard.spawn())
    
    #END TURN
    game.end_turn(command_queue)
    log.info(time()-now)
        
