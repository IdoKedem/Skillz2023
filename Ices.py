from penguin_game import *
from collections import defaultdict
import Forces, Smart, Needed, Attack, math
import Assassins as ass
from Globals import Global


def get_enemy_smarts(game):
    
    if not Global.enemy_smarts:
        enemy = game.get_enemy_icebergs()
        Global.enemy_smarts = Smart.convert_ices(game, enemy)
    return Global.enemy_smarts[:]

def get_friendly_smarts(game):
    
    if not Global.friendly_smarts:
        frirendly = game.get_my_icebergs()
        Global.friendly_smarts = Smart.convert_ices(game, frirendly)
    return Global.friendly_smarts[:]
    
def get_neutral_smarts(game):
    if not Global.neutral_smarts:
        neutrals = game.get_neutral_icebergs()
        Global.neutral_smarts = Smart.convert_ices(game, neutrals)
    return Global.neutral_smarts[:]
    
    
def get_all_smarts(game):
    return get_friendly_smarts(game)[:] + get_enemy_smarts(game)[:] + get_neutral_smarts(game)[:]




def can_icepital_send(game, icepital, force, is_target_upgrading=False, stop_at=1000000):
    """
    This function is checking if our icepital can send a 
    certain force without losing the control even once, if losing 
    returning False
    else True
    also checking if can upgrade in the same way but the force is the 
    upgrade cost
    """
    me = game.get_myself()
    enemy = game.get_enemy()
    
    force_ = force
    needed = icepital.penguin_amount - force # An updating variable
    #print needed
    control = icepital.belong_to

    if icepital.owner == me:
        needed *= -1
        control = -1
    #print needed
    #print "belong to : " + str(control)
    forces = icepital.all_forces
    
    #print forces
    
    united_forces = Forces.unite_forces(game, forces)
    used_forces = []
    
    d = 0 # Force distance to target
    l = icepital.level
    
    if is_target_upgrading:
        l += 1
        needed += 1
        
    #print needed
    for force in forces:
        #print "united_forces" + str(united_forces)
        #print "used_forces" + str(used_forces)
        if force.turns_till_arrival > stop_at:
            needed += force_
            break
        
        if force.turns_till_arrival not in united_forces: # A single force
            delta_d = force.turns_till_arrival - d
            d = force.turns_till_arrival
            p = Forces.net_force(game, force)
            is_friendly_force = me == force.owner
            
        else:# Multiple forces
            force.turns_till_arrival
            if force.turns_till_arrival not in used_forces: # Wasnt used
                delta_d = force.turns_till_arrival - d
                d = force.turns_till_arrival
                
                p_total = Forces.combined_force(game, icepital, forces, d, control) 
                #print "p" + str(p) + "for forces : " + str(force)
                used_forces.append(d)
            else:
                continue
        
        is_friendly_target = control == -1
                
        
        needed += delta_d * l * control # Adding target production in delta_d
     
        needed1 = int(math.ceil(needed/2.0))
        needed2 = int(needed/2.0)  
        
        if force.turns_till_arrival in united_forces:
            p = p_total[1]
            is_friendly_force = True
            needed1 -= p
            p = p_total[0]
            is_friendly_force = False
            
            if control == 0:
                needed2 -= p
            else:
                needed2 += p
            needed = needed1 + needed2
            if needed > 0:
                return False
            elif needed < 0:
                control = -1
        else:
            if is_friendly_force:
                if not is_friendly_target:
                    if p > needed:
                        control = -1
                    elif p == needed:
                        control = 0
                elif needed == 0: # Neutral
                    control = -1
                needed -= p
     
     
            elif not is_friendly_force:
                
                if control == 0 and needed != 0: # Special Case:
                    # Enemy force arriving to an initially neutral ice
                    if p > needed:
                        needed = p - needed
                        return False
                    elif p < needed:
                        needed -= p
                    else: # Nullify the target
                        needed = 0
                else:
                    if is_friendly_target: # needed < 0
                        if p > -needed:
                            return False
                        elif p == needed:
                            control = 0
                    elif needed == 0: # Neutral
                        return False
                    needed += p
        #print "needed " + str(needed) + " after the force : " + str(force)
    
    return True
    
    
def control_changes_in(game, icepital, force=0, is_target_upgrading=False, stop_at=1000000):
    """
    This function checks when the icebergs control changes
    if not, returns -1
    """
    me = game.get_myself()
    enemy = game.get_enemy()
    
    force_ = force
    needed = icepital.penguin_amount - force # An updating variable
    #print needed
    control = icepital.belong_to

    if icepital.owner == me:
        needed *= -1
        control = -1
    #print needed
    #print "belong to : " + str(control)
    forces = icepital.all_forces
    
    #print forces
    
    united_forces = Forces.unite_forces(game, forces)
    used_forces = []
    
    d = 0 # Force distance to target
    l = icepital.level
    
    if is_target_upgrading:
        l += 1
        needed += 1
        
    #print needed
    for force in forces:
        #print "united_forces" + str(united_forces)
        #print "used_forces" + str(used_forces)
        if force.turns_till_arrival > stop_at:
            needed += force_
            break
        
        if force.turns_till_arrival not in united_forces: # A single force
            delta_d = force.turns_till_arrival - d
            d = force.turns_till_arrival
            p = Forces.net_force(game, force)
            is_friendly_force = me == force.owner
            
        else:# Multiple forces
            force.turns_till_arrival
            if force.turns_till_arrival not in used_forces: # Wasnt used
                delta_d = force.turns_till_arrival - d
                d = force.turns_till_arrival
                
                p_total = Forces.combined_force(game, icepital, forces, d, control) 
                #print "p" + str(p) + "for forces : " + str(force)
                used_forces.append(d)
            else:
                continue
        
        is_friendly_target = control == -1
                
        
        needed += delta_d * l * control # Adding target production in delta_d
     
        needed1 = int(math.ceil(needed/2.0))
        needed2 = int(needed/2.0)  
        
        if force.turns_till_arrival in united_forces:
            p = p_total[1]
            is_friendly_force = True
            needed1 -= p
            p = p_total[0]
            is_friendly_force = False
            
            if control == 0:
                needed2 -= p
            else:
                needed2 += p
            needed = needed1 + needed2
            if needed < 0:
                return force.turns_till_arrival
            elif needed > 0:
                control = 1
        else:
            if is_friendly_force:
                if not is_friendly_target:
                    if p > needed:
                        return force.turns_till_arrival
                    elif p == needed:
                        control = 0
                #elif needed == 0: # Neutral
                    #return force.turns_till_arrival
                needed -= p
     
     
            elif not is_friendly_force:
                
                if control == 0 and needed != 0: # Special Case:
                    # Enemy force arriving to an initially neutral ice
                    if p > needed:
                        needed = p - needed
                        return force.turns_till_arrival
                    elif p < needed:
                        needed -= p
                    else: # Nullify the target
                        needed = 0
                else:
                    if is_friendly_target: # needed < 0
                        if p > -needed:
                            return force.turns_till_arrival
                        elif p == needed:
                            control = 0
                    elif needed == 0: # Neutral
                        return force.turns_till_arrival
                    needed += p
        #print "needed " + str(needed) + " after the force : " + str(force)
    
    return -1
    

def can_send_safely(game, ice, force):
    
    p = ice.available_penguins
    

    if ice.is_icepital:
        if ass.scan_for_enemy_assassination(game, get_enemy_smarts(game), ice, force):
            return False
        
        return can_icepital_send(game, ice, force) and force <= p and force > 0
    
    
    #print "can "+ str(ice) + ' send'
    
    #print "p : " + str(p)
    #print "force : " + str(force)
    
    needed = -Needed.needed_before_capture(game, ice, force=force)
    
    #print "needed is fun: " + str(needed)
    #print "can send : " + str(0 < needed + ice.level and force <= p and force > 0)
    
    return 0 < needed + ice.level and force <= p and force > 0


def can_upgrade_safely(game, ice):
    
    p  = ice.available_penguins
    #print "p : " + str(p)
    #if ice.is_icepital:
        #if ass.scan_for_enemy_assassination(game, get_enemy_smarts(game), ice, ice.upgrade_cost):
        #     return False
        
    #    return can_icepital_send(game, ice, ice.upgrade_cost, is_target_upgrading=True) \
    #            and ice.upgrade_cost < p and ice.level < ice.upgrade_level_limit
    #print "ice is trying to upgrade: "
    #print ice
    return 0 < -Needed.needed_before_capture(game, ice, force=ice.upgrade_cost,
                is_target_upgrading=True) + ice.level \
            and ice.upgrade_cost < p and ice.level < ice.upgrade_level_limit


def get_enemy_targets(game):
    enemys = get_enemy_smarts(game)
    return [enemy_ice for enemy_ice in enemys if Needed.get_needed(game, enemy_ice, enemy_ice) > 0]


def get_neutral_targets(game):
    neuts = get_neutral_smarts(game)
    return [neutral_ice for neutral_ice in neuts if Needed.get_needed(game, neutral_ice, neutral_ice) > 0]


def get_targets(game, targets):
    
    #print "TARGETSSSSS Frommm"
    #print_(targets)
    
    my_icepital = get_capital_from_smarts(get_friendly_smarts(game), game.get_myself())
    #print my_icepital
    #enemy_icepitals = [target for target in targets if target.owner == game.get_enemy() and target.is_icepital]
    
    #print "raw targets: "
    #print_(targets)
    
    targets = [ice for ice in targets if ice.is_losing]
    
   # print "losing targets" + str(targets)
   # print_(targets)
    
    targets = get_sorted_by_distance(my_icepital, targets)
    
   # print "targets by ditscnace: "
   # print_(targets)
    
    if not targets:
        return None
    
    if targets[0].owner == game.get_myself() and targets[0].is_icepital:
        pass
    
    elif Attack.capital_lockdown(my_icepital) and my_icepital.enemy_forces:
        targets.insert(0, my_icepital)
    #print "targets : "
    #print_(targets)    
    try:
        objectives = []
        objectives.append(targets[0])
        objectives.append(targets[1])
    
        if targets[1].get_turns_till_arrival(my_icepital) == targets[2].get_turns_till_arrival(my_icepital):
            objectives.append(targets[2])
            #objectives.extend(enemy_icepitals)
        #print "TARGETSSSSS"
        #print_(objectives)
        return objectives

    except:
        return targets
    
    
def get_sorted_by_distance(target, ices):
    # ascending
    return sorted(ices, key=lambda ice: (ice.get_turns_till_arrival(target),
                            not ice.close_cloner, not ice.far_cloner, ice.id))
    
 
def farthest_from_target(target, ices):
    if ices:
        return get_sorted_by_distance(target, ices)[-1]
    return None
    
    
def one_before_farthest_from_target(target, ices):
    if ices:
        return get_sorted_by_distance(target, ices)[-2]
    return None


 
def closest_to_target(target, ices):
    if ices:
        return get_sorted_by_distance(target, ices)[0]
    return None
 
 
def sum_penguins_on_ices(game, ices):
    summ = 0
    for ice in ices:
        #print ice
        #print "current_penguins : " + str(current_penguins(game, ice))
        if abs(ice.current) > ice.penguin_amount:
            summ += ice.penguin_amount
        else:
            summ += abs(ice.current)
        #summ += ice.available_penguins
        #print "sum : " + str(summ)
    #print "sum on ices: " + str(summ)
    return summ
    

def current_penguins(game, ice, forces=[]):
    """
    calculates how much penguins and who the belong to (+/-) will be 
    on ice iceberg in the next turn
    
    NEGATIVE VALUE - friendly penguins
    POSITIVE VALYE - enemy OR neutral
    """
    enemy = game.get_enemy()
    me = game.get_myself()
    neutral = game.get_neutral()
    
    if isinstance(ice, Smart.SmartIce):
        forces = ice.all_forces
        control = ice.belong_to
    
    else:
        if ice.owner == me:
            control = -1
        elif ice.owner == enemy:
            control = 1
        else:
            control = 0
    
    combined_force = Forces.combined_force(game, ice, forces, 1, control)
    p = ice.penguin_amount
    if control != 0:
        p *= control
    #print forces
    if control == 0:
        p1 = int(math.ceil(p/2.0)) - combined_force[1]
        p2 = int(p/2.0) - combined_force[0]
        p = p1 + p2
    
    elif control == 1:
        p += combined_force[0]
    else:
        p -= combined_force[1]
        
    return p 


def ice_belong_to(game, ice):
    
    me = game.get_myself()
    enemy = game.get_enemy()
    neutral = game.get_neutral()
    
    forces = Forces.get_all_forces_to(game, ice)
    forces = Forces.get_all_forces_arriving_in(game, ice, forces, 1)
    
    if ice.owner == me:
        control = -1
    elif ice.owner == enemy:
        control = 1
    else:
        control = 0
    
    combined_force = Forces.combined_force(game, ice, forces, 1, control)
    
    p = ice.penguin_amount
    if ice.owner != neutral:
        p += ice.level
    if combined_force != 0:
        if ice.owner == me:
            p = -p
        if p + combined_force > 0:
            if ice.owner == neutral:
                return 0
            return 1
        if p + combined_force == 0:
            return control
        return -1
        
    else:
        if ice.owner == me:
            return -1
        elif ice.owner == enemy:
            return 1
        return 0
        
    
def print_(ices):
    for ice in ices:
        print str(ice)
        
        
def ices_l_sum(ices):
    l = 0
    for ice in ices:
        l += ice.level
    return l
    

def filter_ices_after_arrival(ices, target, distance):
    """
    Filters the forces param and returns only forces
    that will arrive later than a given distance
    """
    return [ice for ice in ices if ice.get_turns_till_arrival(target) > distance]


def unite_ices(game, target, ices):
    distance_sort = defaultdict(list)
    for ice in ices:
        distance_sort[ice.get_turns_till_arrival(target)].append(ice)
    return distance_sort
    

def get_closest_weakest(sender, ices):
    if sender in ices:
        ices.remove(sender)
    if ices:
        ices = sorted(ices, key=lambda ice: (ice.get_turns_till_arrival(sender),
                            ice.penguin_amount, not ice.close_cloner, not ice.far_cloner, ice.id))
        return ices[0]
    return 
    
    
def same_radius(target, ices):
    if not ices:
        return False
    d = ices[0].get_turns_till_arrival(target)
    for ice in ices[1:]:
        if ice.get_turns_till_arrival(target) != d:
            return False
    return True
    
def is_iceberg_in_smarts(ice, smarts):
    for smart in smarts:
        if smart.ice is ice:
            return True
    return False
        

def level_one(ices):
    if ices:
        l_one = []
        for ice in ices:
            if ice.level == 1:
                l_one.append(ice)
        return get_sorted_by_distance(ices[0].game.get_my_icepital_icebergs()[0], l_one)
    return None
    
def get_capital_from_smarts(ices, owner):
    if owner != ices[0].game.get_myself():
        for ice in ices:
            if ice.is_icepital and ice.owner == owner:
                return ice
    
    return ices[0]
    
    
def get_leftover_target(leftovers):
    
    total_members = []
    for members in leftovers.values():
        total_members.extend(members)
        
    distances_dict = {}
    for target in leftovers.keys():
        distances_sum = sum([member.get_turns_till_arrival(target)
                            for member in total_members])
        distances_dict[target] = distances_sum
    
    
    
    return min([target for target in leftovers.keys()],
                key=lambda target: (target.is_crucial, distances_dict[target], target.id))
    
    
def filter_max_level_ices(ices):
    output = []
    
    for ice in ices:
        if ice.level < ice.upgrade_level_limit:
            output.append(ice)
    return output
    
    
def spam_send(ice, dest, send):
    
    print "SPAM SEND"
    cloneberg = ice.game.get_cloneberg()
    
    if not cloneberg or True:
        ice.send_penguins(dest, send)
        return

    ice.send_penguins(dest, int(send / 2))
    ice.send_penguins(cloneberg, int(send / 2))
    
    
def get_my_smart_capital(game):
    return get_capital_from_smarts(get_friendly_smarts(game), game.get_myself())
    
    
    
    
    
    
    
    
    
    
