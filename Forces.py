from penguin_game import *
from collections import defaultdict
import Ices, Smart, Needed
from Globals import Global
 

def get_enemy_forces_to(game, ice):
    
    if isinstance(ice, Smart.SmartIce):
        ice = ice.ice
    
    if ice not in Global.enemy_forces.keys():
        #print "UPDATING EMRMYE FORECSE FOR " + str(ice)
        
        enemy_forces = game.get_enemy_penguin_groups()
        
        clone = game.get_cloneberg()
        coming = []
        
        #print "enemy_forces1"
        #Ices.print_(enemy_forces)
        
        for force in enemy_forces:
            
            
            
            if force.is_siege_group:
                continue
            
            #print force
            #print "aspoiurce:" + str(force.source)
            #print "first or: " + str(force.destination is ice)
            #print "second or: " + str(force.source == ice and force.destination == clone)
            
            #print "and check"
            #print force.source == ice
            #print force.destination == clone
            
            
            if force.destination is ice \
                or (force.source == ice and force.destination == clone):
                
                #print "first or: " + str(force.destination is ice)
                #print "second or: " + str(force.source == ice and force.destination == clone)
                
                coming.append(Smart.SmartForce(game, force))
            
        #print "cumming: "
        #Ices.print_(coming)
        Global.enemy_forces[ice] = get_sorted(coming)
    #else:
        #print "NOT UPFATING FOR: " + str(ice)
        #pass
    #print "returning: "
    #Ices.print_(Global.enemy_forces[ice])
    
    return Global.enemy_forces[ice][:]



def get_friendly_forces_to(game, ice):
    
    if isinstance(ice, Smart.SmartIce):
        ice = ice.ice
    
    if ice not in Global.friendly_forces.keys():
        friendly_forces = game.get_my_penguin_groups()
        
        clone = game.get_cloneberg()
        coming = []
        
        for force in friendly_forces:
            
            if force.is_siege_group:
                continue
            
            if not force.destination is ice \
                and not (force.source == ice and force.destination == clone):
                continue
            
            coming.append(Smart.SmartForce(game, force))
            
        Global.friendly_forces[ice] = get_sorted(coming)
                    
    return Global.friendly_forces[ice][:]
 
 
def get_all_forces_to(game, ice):
    
    if isinstance(ice, Smart.SmartIce):
        ice = ice.ice
    
    if ice not in Global.enemy_forces.keys():
        enemy_forces = get_enemy_forces_to(game, ice)
        
    if ice not in Global.friendly_forces.keys():
        friendly_forces = get_friendly_forces_to(game, ice)
    
    
    all_forces = Global.enemy_forces[ice][:]
    all_forces += Global.friendly_forces[ice]

    Global.all_forces[ice] = get_sorted(all_forces)
    
    return Global.all_forces[ice][:]


def get_enemy_sieges_to(game, ice):
    
    if isinstance(ice, Smart.SmartIce):
        ice = ice.ice
    
    if ice not in Global.enemy_sieges.keys():
        #print "UPDATING EMRMYE FORECSE FOR " + str(ice)
        
        enemy_forces = game.get_enemy_penguin_groups()
        
        clone = game.get_cloneberg()
        coming = []
        
        for force in enemy_forces:
            
            if not force.is_siege_group:
                continue
            
            if not force.destination is ice \
                and not (force.source == ice and force.destination == clone):
                continue
            
            coming.append(Smart.SmartForce(game, force=force))
            
        Global.enemy_sieges[ice] = get_sorted(coming)

    return Global.enemy_sieges[ice][:]



def get_friendly_sieges_to(game, ice):
    
    if isinstance(ice, Smart.SmartIce):
        ice = ice.ice
    
    if ice not in Global.friendly_sieges.keys():
        friendly_forces = game.get_my_penguin_groups()
        
        clone = game.get_cloneberg()
        coming = []
        
        for force in friendly_forces:
            
            if not force.is_siege_group:
                continue
            
            if not force.destination is ice \
                and not (force.source == ice and force.destination == clone):
                continue
            
            coming.append(Smart.SmartForce(game, force))
            
        Global.friendly_sieges[ice] = get_sorted(coming)
                    
    return Global.friendly_sieges[ice][:]
 
 
def get_all_sieges_to(game, ice):
    
    
    if isinstance(ice, Smart.SmartIce):
        ice = ice.ice
    
    if ice not in Global.enemy_sieges.keys():
        enemy_sieges = get_enemy_sieges_to(game, ice)
        
    if ice not in Global.friendly_sieges.keys():
        friendly_sieges = get_friendly_sieges_to(game, ice)
    
    
    all_forces = Global.enemy_sieges[ice][:]
    all_forces += Global.friendly_sieges[ice]

    Global.all_sieges[ice] = get_sorted(all_forces)
    
    return Global.all_sieges[ice][:]


def is_enemy_between(game, ice1, ice2):
    if ice1 not in Global.enemy_forces.keys():
        forces = get_enemy_forces_to(game, ice1)
        
    forces = Global.enemy_forces[ice1]
    
    for force in forces:
        if force.source is ice1:
            return True
    return False
    
    
def get_all_forces_arriving_in(game, ice, forces, turns):
    out = []
    for force in forces:
        if isinstance(force, PenguinGroup) or isinstance(force, Smart.SmartForce):
            if force.turns_till_arrival == turns:
                out.append(force)
    return out
 
 
def get_sorted(forces):
    return sorted(forces, key=lambda force: (force.turns_till_arrival, force.penguin_amount, force.id))
 
 
def get_closest_enemy_force_to(ice):
    
    if isinstance(ice, Smart.SmartIce):
        ice = ice.ice
    
    if ice not in Global.enemy_forces.keys():
        forces = get_enemy_forces_to(game, ice)
    
    return Global.enemy_forces[ice][0]
 
 
def get_closest_friendly_force_to(game, ice):
    
    if isinstance(ice, Smart.SmartIce):
        ice = ice.ice
    
    return get_friendly_forces_to(game, ice)[0]
 
 
def get_closest_force_to(ice):
    
    if ice not in Global.all_forces.keys():
        return get_all_forces_to(ice)[0]
    return Global.all_forces[ice][0]
 
def filter_forces_before_arrival(forces, distance):
    """
    Filters the forces param and returns only forces
    that will arrive sooner than a given distance
    """
    return [force for force in forces if
            force.turns_till_arrival < distance]


    
def filter_forces_on_arrival(forces, distance):
    """
    Filters the forces param and returns only forces
    that will arrive at a given distance
    """
    return [force for force in forces if force.turns_till_arrival == distance]
 
 
def filter_forces_after_arrival(forces, distance):
    """
    Filters the forces param and returns only forces
    that will arrive later than a given distance
    """
    return [force for force in forces if force.turns_till_arrival > distance]


def unite_forces(game, forces):
    """
    Goes through the forces list and unites all the forces that have the same
    arrival time to one force (list) that represents the 
    of said forces
    """
    distance_sort = defaultdict(list)
    for force in forces:
        distance_sort[force.turns_till_arrival].append(force)
    unite = []
    for distance, force in distance_sort.items():
        if len(force) > 1:
            unite.append(distance)
    return unite


def net_force(game, force):
    """
    Get the net value of penguins that will reach the destination
    after all collisions
    """
    if force.source not in Global.all_forces.keys():
        forces = get_all_forces_to(game, force.source)
    else:
        forces = Global.all_forces[force.source]
    
    me = game.get_myself()
    
    opposite_forces = [f for f in forces if not f.owner is force.owner
                and (f.source is force.destination or force.source is f.source)]
    
    p = force.penguin_amount
    for opposite_force in opposite_forces:
        p -= opposite_force.penguin_amount
        
    return p if p > 0 else 0
    
def ice_net_force(game, ice, target):
    """
    returns the net value of penguins that will reach me
    after all collisions
    """
    minus = 0
    #print "ice.all_forces : " + str(ice.all_forces)
    
    opposite_forces = []
    
    if isinstance(target, Smart.SmartIce):
        target = target.ice
    
    #print "target" + str(target)
    for opposite_force in ice.all_forces:
        #print "opposite_force source" + str(opposite_force.source)
        if opposite_force.source == target:
            opposite_forces.append(opposite_force)
    
    
    #print "opposite_forces: " +str(opposite_forces)
    for opposite_force in opposite_forces:
        minus += opposite_force.penguin_amount
        
    return minus

    
def combined_force(game, ice, forces, turns, control):
    """
    recieves a list of forces that ALL ARRIVE ON THE SAME TIME
    this "combines" all the forces to an imaginary "single" group since
    they all arrive on the same time and returns an imaginary amount of
    that group
    
    NEGATIVE VALUE - THE GROUP BELONGS TO US
    POSITIVE VALUE - YOU ARE MY ENEMY!!!!!
    
    
    """
    forces = get_all_forces_arriving_in(game, ice, forces, turns)
    if not forces:
        return (0, 0)
        
    pF = 0
    pE = 0
    pT = 0
    me = game.get_myself()
    if control == 0:
        for subforce in forces:
            if subforce.owner == me:
                pF += net_force(game, subforce)
            else:
                pE += net_force(game, subforce)
        return (pE, pF)
        
    for subforce in forces:
        if subforce.owner == me:
            pT -= net_force(game, subforce)
        else:
            pT += net_force(game, subforce)
    #print "pT : " + str(pT)
    if pT > 0:
        return (pT, 0)
    else:
        return(0, -pT)
    
    
def cut_penguin_group(game, ice, forces):
    if ice == game.get_my_icepital_icebergs()[0]:
        my_icebergs = Ices.get_friendly_smarts(game)
        my_icebergs = Ices.get_sorted_by_distance(ice, my_icebergs)
        if len(my_icebergs) > 1:
            friendly_ice = my_icebergs[1]
            #print "friendly_ice : " + str(friendly_ice)
            d = friendly_ice.get_turns_till_arrival(ice) + 1
            cut = []
            if len(forces) <= d:
                return forces
            for i in range(d):
                cut.append(forces[i])
            #print "cut : " + str(cut)
            return cut
    return forces
    
    
def get_net_force_sum(game, ices, target):
    summ = 0
    for ice in ices:
        summ += ice_net_force(game, ice, target)
        
    return summ

def there_is_enemy_force(game, forces):
    me = game.get_myself()
    for force in forces:
        if force.owner != me:
            return True
    return False
    
    
def just_sent(game):
    """
    Returns a dict where the keys are targets and the values are 
    a list of forces sent in the previous turn
    """
    if not Global.just_sent:
        friendly_forces = game.get_my_penguin_groups()
        just_sent = defaultdict(list)
        
        for force in friendly_forces:
            if force.source.get_turns_till_arrival(force.destination) - force.turns_till_arrival == 1:
                just_sent[force.destination].append(force)
        Global.just_sent = just_sent
        
    return Global.just_sent
    

def enemy_to_me(friendly_ice, target):
    resistance = []
    
    if isinstance(target, Smart.SmartIce):
        target = target.ice
    
    for enemy in friendly_ice.enemy_forces:
        if enemy.source == target:
            resistance.append(enemy)
    
    #print "enemy_to_me"
    #print resistance
    
    return resistance
    
def me_to_enemy(enemy_ice, target):
    resistance = []
    
    if isinstance(target, Smart.SmartIce):
        target = target.ice
    
    for friendly in enemy_ice.friendly_forces:
        if friendly.source == target:
            resistance.append(friendly)
    
    #print "enemy_to_me"
    #print resistance
    
    return resistance
    
def just_sent_forces(game):
    
    if not Global.just_sent_forces:
        friendly_forces = game.get_my_penguin_groups()
        just_sent = []
        
        for force in friendly_forces:
            if force.source.get_turns_till_arrival(force.destination) - force.turns_till_arrival == 1:
                just_sent.append(force)
                
        Global.just_sent_forces = just_sent
        
    return Global.just_sent_forces

    
def sum_forces(forces):
    summ = 0
    for force in forces:
        summ += force.penguin_amount
    return summ
        
    
def convert_ices_to_fake(attacker_amounts, target):
    
    output = []
    
    for ice, amount in attacker_amounts.items():
        d = ice.get_turns_till_arrival(target)
        owner = ice.owner
        
        fake_force = Smart.SmartForce(distance=d, amount=amount,
            ice=ice, destination=target, is_fake=True)
            
        print "fake_force: " + str(fake_force)
        
        output.append(fake_force)
    
    return output
    
    
