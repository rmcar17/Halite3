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

class Navigator:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def normalise(self, pos):
        return Position(pos.x % self.width, pos.y % self.height)

    def random(self, ship_pos, bad_pos):
        found_move = False
        moves = Direction.get_all_cardinals()
        random.shuffle(moves)
        for move in moves:
            new_position = self.normalise(ship_pos.directional_offset(move))
            if new_position not in current_moves:
                found_move = True
                break
        if found_move:
            return move
        return Direction.Still

    def navigate(self, ship_pos, target_pos):
        moves = []
        
        ship_pos = self.normalise(ship_pos)
        target_pos = self.normalise(target_pos)
        distance = target_pos - ship_pos

        if (distance.x > 0 and abs(distance.x) <= self.width / 2) or (distance.x < 0 and abs(distance.x) >= self.width / 2):
            moves.append(Direction.East)
        if (distance.x > 0 and abs(distance.x) >= self.width / 2) or (distance.x < 0 and abs(distance.x) <= self.width / 2):
            moves.append(Direction.West)
        if (distance.y > 0 and abs(distance.y) <= self.height / 2) or (distance.y < 0 and abs(distance.y) >= self.height / 2):
            moves.append(Direction.South)
        if (distance.y > 0 and abs(distance.y) >= self.height / 2) or (distance.y < 0 and abs(distance.y) <= self.height / 2):
            moves.append(Direction.North)
        return moves
            

game.ready(__file__)

game_map = game.game_map

nav = Navigator(game_map.width, game_map.height)

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
        elif ship_id in collectors and ship.halite_amount >= constants.MAX_HALITE / 2:
            collectors.remove(ship_id)
            returners.append(ship_id)
        elif (ship_id in returners and ship.position == me.shipyard.position) or (ship_id in collectors and game_map[ship.position].halite_amount < constants.MAX_HALITE / 10):
            if ship_id in collectors:
                collectors.remove(ship_id)
            else:
                returners.remove(ship_id)
            explorers.append(ship_id)
        
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
        moves = nav.navigate(ship.position, me.shipyard.position)
        valid_moves = []
        move_score = []
        for move in moves:
            new_position = nav.normalise(ship.position.directional_offset(move))
            if new_position not in current_moves:
                valid_moves.append(move)
                move_score.append(game_map[new_position].halite_amount)
        if len(valid_moves) == 0:
            current_moves.append(ship.position)
            command_queue.append(ship.stay_still())
        else:
            move = valid_moves[move_score.index(min(move_score))]
            current_moves.append(ship.position.directional_offset(move))
            command_queue.append(ship.move(move))
    
    for s_id in explorers:
        ship = me.get_ship(s_id)
        move = nav.random(ship.position, current_moves)
        current_moves.append(nav.normalise(ship.position.directional_offset(move)))
        command_queue.append(ship.move(move))
        
    log.info(current_moves)
    #SPAWN SHIPS
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and me.shipyard.position not in current_moves:
        command_queue.append(me.shipyard.spawn())
    
    #END TURN
    game.end_turn(command_queue)
    log.info(time()-now)
        
