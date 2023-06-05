import math
import Forces, Ices, Challenge1, Formulas, Smart, Needed
from Globals import Global
    
    
def get_assassin(target, ices):
    
    if not target.is_losing_ice_without_needed:
        return
    
    potentials = [ice for ice in ices if not Forces.enemy_to_me(ice, target)]
    
    if potentials:
    
        ice = max(potentials, key=lambda ice: (ice.penguin_amount, ice.get_turns_till_arrival(target), ice.id))
        
        if can_assasinate(ice, target):
            return ice
            
    return
    
    
def can_assasinate(assassin, target):
    
    if assassin.is_underspam:
        return False
    
    cost = assassination_cost(assassin, target)
    
    #print "Pendejo"
    #print cost
    
    if assassin.is_icepital:
        return Ices.can_send_safely(assassin.game, assassin, cost)
    
    if assassin.penguin_amount >= cost:
        return True
        
    return assassination_wait(assassin, target)


def assassination_wait(assassin, target):
    cost = assassination_cost(assassin, target)
    time_to_wait = 3
    
    future_p = Needed.needed_before_capture(assassin.game, target, stop_at=time_to_wait + 1)
    
    return future_p > cost
  
  
def assassination_cost(assassin, target):
    game = assassin.game
    
    d = assassin.get_turns_till_arrival(target)
    #print d
    bullet_time = Challenge1.max_bullet_time(game, d)
    #print "max time: " + str(bullet_time)
    
    ac = game.acceleration_cost
    af = game.acceleration_factor
    times = Challenge1.calc_times(game, d)
    #print "times: " + str(times)
    
    p_on_arrival = target.penguin_amount + (bullet_time) * target.level + 1 + assassin.siege_amount
    #print target.penguin_amount
    #print (bullet_time + 1) * target.level
    #print "p_on_arrival: " + str(p_on_arrival)
    
    resistance = Forces.enemy_to_me(assassin, target)
    
    arriving = Forces.get_enemy_forces_to(game, target)
    arriving_before = Forces.filter_forces_before_arrival(arriving, bullet_time + 1)
    
    #Ices.print_(arriving)
    
    sum_arriving = sum(force.penguin_amount for force in arriving_before)
    
    net_cost = Challenge1.add_acc_waste(p_on_arrival + sum_arriving, ac, af, times, d, resistance)
    #print "sum_arriving: " + str(sum_arriving)
    
    #print "net_cost: " + str(net_cost)
    
    #print "total: " + str(net_cost + sum_arriving)
    
    return net_cost + assassin.siege_amount
    

def initiate_assassin(game, assassin, target):
    print "SENDING PENDEJO"
    assassin.send_penguins(target, assassination_cost(assassin, target))
    Global.accelerating_icebergs[assassin] = \
        Challenge1.calc_times(game, assassin.get_turns_till_arrival(target))
    

def accelerate_assassinations(game):
    enemy_icepital = game.get_enemy_icepital_icebergs()[0]
    forces = Forces.get_friendly_forces_to(game, enemy_icepital)
    
    for force in forces:
        d = force.destination.get_turns_till_arrival(force.source)
        if math.log(force.current_speed, game.acceleration_factor) < Challenge1.calc_times(game, d):
            force.accelerate()


def enemy_assassination_cost(assassin, target, force=0):
    game = assassin.game
    
    d = assassin.get_turns_till_arrival(target)
    #print d
    bullet_time = Challenge1.max_bullet_time(game, d)
    #print "max time: " + str(bullet_time)
    
    ac = game.acceleration_cost
    af = game.acceleration_factor
    times = Challenge1.calc_times(game, d)
    #print "times: " + str(times)
    
    p_on_arrival = target.penguin_amount - force + (bullet_time) * target.level + 1
    #print target.penguin_amount
   # print (bullet_time + 1) * target.level
   # print force
   # print "p_on_arrival: " + str(p_on_arrival)
    
    resistance = Forces.me_to_enemy(assassin, target)
    
    arriving = Forces.get_friendly_forces_to(game, target)
    arriving_before = Forces.filter_forces_before_arrival(arriving, bullet_time + 1)
    
    #Ices.print_(arriving)
    
    sum_arriving = sum(force.penguin_amount for force in arriving_before)
    
    net_cost = Challenge1.add_acc_waste(p_on_arrival + sum_arriving, ac, af, times, d, resistance)
    #print "sum_arriving: " + str(sum_arriving)
    
    #print "net_cost: " + str(net_cost)
    
    #print "total: " + str(net_cost + sum_arriving)
    
    return net_cost + assassin.siege_amount


def can_enemy_assasinate(assassin, target, force=0):
    
   
    cost = enemy_assassination_cost(assassin, target, force)
    
    #print "Pendejo"
    #print cost
        
    return assassin.penguin_amount > cost


def scan_for_enemy_assassination(game, enemy_ices, my_icepital, force=0, time=0):
    
    for ice in Ices.get_friendly_smarts(game):
        if ice.is_cloner_defender:
            defnder = ice
    
    ice = max(enemy_ices,
        key=lambda ice: (ice.penguin_amount, ice.get_turns_till_arrival(my_icepital), ice.id))
     
    if force:  
        if can_enemy_assasinate(ice, my_icepital, force):
            #print "OPTIONAL ENEMY ASSASSINATION DETECTED - DONT SEND"
            return True
        return False
    
    if can_enemy_assasinate(ice, my_icepital):
        #print "OPTIONAL ENEMY ASSASSINATION DETECTED"
        Global.lockdowns["capital"] = True


print("MICHAEL GOAT")    
    
    
    
    
    
    
