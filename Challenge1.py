from penguin_game import *
from collections import defaultdict

import Forces, math, Ices, Needed
from Globals import Global



def are_not_accelerated(forces):
    for force in forces:
        if force.current_speed > 1:
            return False
    return True


def calc_bullet_time(game, times, d):
    af = game.acceleration_factor
    add_one = 0
    
    max_speed_travel = (float)(d - (af**(times+1) - 1)/(af - 1))
    bullet_time = int(times + 1 + math.ceil(max_speed_travel / af**times))
    
    #if times == 1 and d == 16:
    #print "IM CALCULATING BITCHHH"
    #    print math.ceil(max_speed_travel / af**times)
    #    print max_speed_travel
    #    print times + 1
    #print bullet_time
    #print add_one
    
    return bullet_time + add_one


def max_bullet_time(game, d):
    return calc_bullet_time(game, calc_times(game, d), d)

def accelerated_amount(ice, times):
    game = ice.game
    p = ice.penguin_amount
    accelerated_amount = p / game.acceleration_cost**times
    
    if accelerated_amount > 0:
        return int(accelerated_amount)
    return 0

def calc_bullet_force(game, force, times):
    
    final_value = force
    
    for _ in range(times):
        final_value = math.ceil(final_value * game.acceleration_cost)
        
    return int(final_value)

def calc_bullet_forces(attacker_amounts, target):
    
    game = target.game
    output = {}
    
    for sender, force in attacker_amounts.items():
        
        times = calc_times(game, sender.get_turns_till_arrival(target))
        #print "times " + str(times)
        #print "relative_force : " + str(relative_force)
        output[sender] = calc_bullet_force(game, force, times)
        
    return output
        
def net_bullet_coming(game, force, times=-1):
    
    if times == -1:
        times = calc_times(game, force.turns_till_arrival)
    ac = game.acceleration_cost
    final_value = force.penguin_amount
    
    for _ in range(times):
        final_value = math.floor(final_value / ac)
    
    #print final_value
    return int(final_value)
        
    
    

def calc_min_bullet_force(game, force, times):
    return force / (game.acceleration_cost ** times)



def acceleration_profit(game, sender, target, force_amount):
    """
    Calculates the penguin profit for capturing a neutral iceberg
    acounting for only a single acceleration
    
    ALWAYS RETURNS AN INTEGER
    
    POSITIVE VALUE - should acc
    NEGATIVE VALUE - should not acc
    0 - doesnt matter
    """
    d = sender.get_turns_till_arrival(target)
    
    #print "ACC PROFIT"
    #print "d: " + str(d)
    
    #print "send_amount: " + str(force_amount)
    
    
    #print "force type: "
    #print str(type(force))
    
    new_force_amount = int(math.ceil(force_amount * game.acceleration_cost))
    #print "new send amount: " + str(new_force_amount)
    
    bullet_time = calc_bullet_time(game, 1, d)
    
    #print "bullet_time: " + str(bullet_time)
    
    normal_send = force_amount
    acc_send = new_force_amount - target.level * (d - bullet_time)
    
    #print normal_send - acc_send
    
    return normal_send - acc_send
    
    #acceleration_waste = int(math.ceil(float(force) * (game.acceleration_cost - 1)))
    
    #extra_production = (d - int(round(d / game.acceleration_factor))) * target.level
    #return extra_production - acceleration_waste



def accelerate_neutral_attacks(game):
    """
    Accelerates the friendly_forces that need to be accelerated
    """
    
    neuts = game.get_neutral_icebergs()
    just_sent = Forces.just_sent(game)
    #print just_sent
    
    for neut in neuts:
        
        if not neut in just_sent.keys():
            continue
        
        if Ices.same_radius(neut, [force.source for force in just_sent[neut]]):
            continue
        
        force = max(just_sent[neut], key=lambda force: (force.turns_till_arrival, force.id)) ##########################
        sum_others = sum([other.penguin_amount if other != force else 0 for other in just_sent[neut]]) 
        #print sum_others
        #print "force::::::: " + str(force)
        #print "amount bitvch: " + str(force.penguin_amount)
        #print "fisjd igfds: " + str(game.acceleration_cost)
        
        if int(math.floor(force.penguin_amount / game.acceleration_cost)) > neut.penguin_amount - sum_others:
            #print "MADAFAKAAAAAAAAAAAAAAAAAAAAA"
            force.accelerate()
    
    
def accelerate_defenses(game, defended_ice):
    
    
    enemy_max_speed = max(defended_ice.enemy_forces, key=lambda force: force.current_speed).current_speed
    #print "enemy_max_speed bitch: " + str(enemy_max_speed)
    
    #if enemy_max_speed == 1:
        #if my_max_speed == 1:
            #for force in Global.cpu_forces:
                #force.accelerate()
    
    #    return False
    
    accelerated = False
    
    if not defended_ice.is_icepital: #and first_speed < 4: ######################
        return False
    
    for force in Global.cpu_forces:
        
        #print force
        #print force.current_speed
        #print is_acceleration_necessary(game, force)
        #print force.turns_till_arrival
        
        if force.current_speed < enemy_max_speed and is_acceleration_necessary(game, force):
            #print "when you think u have friends"
            if int(force.penguin_amount / game.acceleration_cost) > 0:
                #print "but they are true"
                force.accelerate()
                accelerated = True
            else:
                pass
               # print "sike"
    
    return accelerated


def calc_times(game, d):
    
    af = game.acceleration_factor
    if d == 0:
        return 0
    times = int(math.log(d, af))
    
    for time in range(times):
        d -= af ** time
        #print time
        #print "d = " + str(d)
        #print "af ** (time + 1) = " + str(af ** (time + 1))
        if d <= af ** time:
            #print "im out motherfucker"
            #print "time : " + str(time)
            return time
    
    return times


def acc_diff(ice):
    
    game = ice.game
    
    farthest_d = ice.all_forces[-1].turns_till_arrival
    
    return farthest_d - max_bullet_time(game, farthest_d)
    


def is_acceleration_necessary(game, force):
    return force.turns_till_arrival > 1
    

def add_acc_waste(force, ac, af, times, d, resistance):
    
    net_cost = force
    
    distance_passed = 0
    
    for acc in range(times):
        current_distance = distance_passed + af ** acc
        sum_resistance = 0
        
        for force in resistance:
            if distance_passed < force.turns_till_arrival < current_distance:
                sum_resistance += force.penguin_amount
        
        net_cost = math.ceil(net_cost * ac)
        net_cost += sum_resistance
    
    return int(net_cost)
    
    
    
def gross_force(sender, target, force):
    """
    Calculate the gross force if sent to icepital
    """
    
    game = sender.game
    
    d = sender.get_turns_till_arrival(target)
    ac = game.acceleration_cost
    af = game.acceleration_factor
    times = Challenge1.calc_times(game, d)
    
    resistance = Forces.enemy_to_me(sender, target)
    return add_acc_waste(force, ac, af, times, d, resistance)
    

def anti_sweep(target, game):
    if len(target.friendly_forces) == 1 and len(target.enemy_forces) == 1:
        enemy = target.enemy_forces[0]
        friendly = target.friendly_forces[0]
        if enemy.current_speed > 1 and enemy.penguin_amount > game.acceleration_cost \
            and enemy.turns_till_arrival > friendly.turns_till_arrival:
                
            times = calc_times(game, friendly.turns_till_arrival) + 1
            profit_dict = {i: target.penguin_amount - net_bullet_coming(game, friendly, i) for i in range(times)}
            
            print "profit_dict: " + str(profit_dict)
            
            friendly.accelerate()



def accelerate_attacks(game):
    
    targets = Ices.get_friendly_smarts(game) + Ices.get_enemy_smarts(game) + Ices.get_neutral_smarts(game)
    ac = game.acceleration_cost
    
    #print "LEAVING"
    
    for target in targets:
        #print "target is:" + str(target)
        
        
        if not target.friendly_forces:
            #print 1
            continue
        
        if not target.is_losing_ice_without_needed:
            #print 2
            continue
        
        
        if target.owner == game.get_neutral():
            
            anti_sweep(target, game)
            
            #print "regular neutral"
            continue
        
        
        control = target.belong_to
        
        target_l = target.level
        
        closest_friendly = Forces.get_closest_friendly_force_to(game, target)
        closest_friendly_d = closest_friendly.turns_till_arrival
        
        #print "closest_friendly: " + str(closest_friendly)
        
        acc_friendly_d = int(math.ceil(closest_friendly_d / 2.0))
        
        #print "and d is " + str(closest_friendly_d)
        
        force_acc_p = int(math.floor(closest_friendly.penguin_amount / ac))
        
        
        if force_acc_p <= 0:
            #print 3
            continue
        
        if closest_friendly in Global.accelerating_forces:
            #print 4
            continue
        
        
        #print 'acc_friendly_d: ' + str(acc_friendly_d)
        
        #print "force_acc_p: " + str(force_acc_p)
        
        
        acc_p_on_arrival = Needed.needed_before_capture(game, target, stop_at=acc_friendly_d)
        #print "acc_p_on_arrival: " + str(acc_p_on_arrival)
        
        if acc_p_on_arrival <= 0:
            #print 5
            continue
        
        after_me = Forces.filter_forces_after_arrival(target.enemy_forces, acc_friendly_d)
        
        #print "after_me: "
        #Ices.print_(after_me)
        
        
        if after_me:
            compare_d = after_me[0].turns_till_arrival
        else:
            compare_d = closest_friendly_d
        
        #print "compare_d: " + str(compare_d)
        
        delta_d = compare_d - acc_friendly_d
        
        if force_acc_p <= acc_p_on_arrival:
            #print 6
            continue
            
        if target_l * delta_d > closest_friendly.penguin_amount - force_acc_p:
            
            closest_friendly.accelerate()
            #print 7
            continue
            
        
        
            
                
                
        
        
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    


    
    
    
    
    
