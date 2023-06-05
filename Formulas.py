from penguin_game import *
import Ices
import math
import Needed
import Forces
import Challenge1 
 
def level_difference(upgrading_ice, other_ice, time, override_level=None, targets_compare=False):
    """
    receives two icebergs with different levels and returns the 
    amount of penguins the upgrading iceberg has to invest in order
    to level up other_ice.level levels, with respect for time
    """
    
    #print "LEVEL DIFFERENCE"
    
    #print str(upgrading_ice) + " to " + str(other_ice)
    
    
    
    l1 = upgrading_ice.level
    p1 = upgrading_ice.available_penguins
    
   # print "other_ice:"
    #print "p:" + str(other_ice.penguin_amount)
    #print "cur: " + str(other_ice.current)
    
    #print "l1: " + str(l1)
    
    #if -upgrading_ice.current < p1:
        #print "Changing to current: " + str(-upgrading_ice.current)
        #p1 = -upgrading_ice.current
        
    if upgrading_ice.is_losing_ice_without_needed \
        and not upgrading_ice.is_losing:
        p1 = upgrading_ice.needed
    
    
    if other_ice:
        l2 = other_ice.level
    
    if override_level:
        l2 = override_level
        
    #print "lt2: " + str(l2)
    
    #print "l2: " + str(other_ice.level)
    
    #if not other_ice.owner is other_ice.game.get_neutral():
        #l2 *= 2
    
    upgrade_delay = 0
    
    
    #print "upgrade_delay: " + str(upgrade_delay)
    
    if targets_compare:
        for l in range(l2 - l1 - 1):
            upgrade_delay += l1 + l + 1
    
        upgrades_cost = upgrade_levels_cost(upgrading_ice, l2 - l1)
    else:
        for l in range(l2 - 1):
            upgrade_delay += l1 + l + 1
    
        upgrades_cost = upgrade_levels_cost(upgrading_ice, l2)
 
    #print "upgrades_cost: " + str(upgrades_cost)
 
    time_till_upgrade = 0
    
    missing_p = float(upgrades_cost - p1)
    #print "missing_p: " + str(missing_p) + "for " + str(upgrading_ice)

    
    if upgrades_cost - upgrade_delay >= p1:
        time_till_upgrade = int(math.ceil((missing_p - upgrade_delay) / l1))
        #print "time_till_upgrade: " + str(time_till_upgrade)
    
    #print "time: " + str(time)
    
    penguin_profit = abs(time - time_till_upgrade) * l2
    #print "penguin_profit: " + str(penguin_profit)
    
    if time_till_upgrade <= time:
        total = upgrades_cost - (penguin_profit - upgrade_delay)
        #print "total1: " + str(total)
        return total
    
    if targets_compare:
        penguin_profit = 0
        
    total = upgrades_cost + penguin_profit + upgrade_delay
    #print "total2: " + str(total)
    return total
    
    
 
 
def calc_relative_force(target, sender, participants, total_amount):
    """
    returns an UNROUNDED relative force for 'sender' iceberg
    this function is used in the get_relative_forces_dict func
    """
    #print "total_amount : " + str(total_amount)
    #Ices.print_(participants)
    
    sum_penguins = Ices.sum_penguins_on_ices(target.game, participants)
    
    
    if len(participants) == 1:
        return total_amount
        
    p = sender.available_penguins   # ozays fault!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    
    #print "target: " + str(target)
    #print "sender: " + str(sender)
    
    sorted_participants = Ices.get_sorted_by_distance(target, participants)
    
    
    total = float(total_amount * p) #+ sender_d * l))
    #print "total: " + str(total)
    
    divide = sum_penguins # + (sum_ds * l)
    #print "divide: " + str(divide)

    relative_force = total / divide
    #print "relative_force: " + str(relative_force)
    
    if target.owner == target.game.get_myself() and target.is_icepital:
        relative_force = math.ceil(relative_force)
        #print "BULLET FORCE :" + str(relative_force)

        
    return relative_force



def get_relative_forces(game, target, participants, total_amount):
    """
    returns a dict containing the amount of relative pe nguins (f) each
    participant iceberg has to send, according to
    calc_relative_force func, in form of {participant: amount}
    """
    
    #print "IN relative FORCES BITTTTCHHH"
    #print "tota needed: " + str(total_amount + 1)
    attack_distribution = {}
    
    #print "target : " + str(target)
    
    #print "total_amount : " + str(total_amount + 1) 
    
    #print "attack_distribution"
    
    if len(participants) == 1:
        if target.owner == game.get_myself() and target.is_icepital:
            d = Challenge1.max_bullet_time(game, participants[0].get_turns_till_arrival(target))
            total_amount = Challenge1.calc_bullet_force(game, total_amount + 1, d)
            #print total_amount
        attack_distribution[participants[0]] = total_amount + 1
        #print attack_distribution
    
    else:
        for participant in participants:
            #print "participant : " + str(participant)
            attack_distribution[participant] = calc_relative_force(
                target, participant, participants, total_amount + 1)
            #print "amount : " + str(attack_distribution[participant])

        if participants:
            #print "before" + str(attack_distribution)
            attack_distribution = balance_sends(attack_distribution, total_amount + 1)
            #print "after" + str(attack_distribution)
    for participant in participants:
        attack_distribution[participant] += Forces.ice_net_force(game, participant, target)
    
    if target.is_icepital and target.owner == game.get_myself():
        attack_distribution = Challenge1.calc_bullet_forces(attack_distribution, target)
    
    return {ice: amt for ice, amt in sorted(attack_distribution.items(), 
            key=lambda item: (item[0].get_turns_till_arrival(target),
                not item[0].close_cloner, not item[0].far_cloner, item[0].id))}




def balance_sends(sends_dict, total_amount):
    """
    bla bla bla diborim vecaze
    """
    help_order = sorted(sends_dict, 
        key=lambda ice: (not ice.close_cloner, not ice.far_cloner, ice.id))
    ############################################################# d from icepital ^
    
    
    sum_penguins = 0
    
    for ice in sends_dict.keys():
        sends_dict[ice] = int(round(sends_dict[ice]))
        sum_penguins += sends_dict[ice]
    
    balance = total_amount - sum_penguins
    
    for ice in help_order:
        if ice.penguin_amount >= sends_dict[ice] + balance:
            sends_dict[ice] += balance
            break
    
    return sends_dict

    
    

    
def distance_difference(game, sender, farther_ice, closer_ice):
    """
    receives a sender, and two icebergs (can be same distance) and returns 
    the difference in penguins lost between capturing both of the ices
 
    NEGATIVE VALUE - you should send to closer ice
    POSITIVE VALUE - you should send to farther ice
    0 - same cost, should send to closer ice
 
    for example, if the returned value is -8, capturing the closer ice will 
    benefit us by 8 penguins
 
    ******************
    IF BOTH ICEBERGS ARE SAME DISTANCE
    NEGATIVE VALUE - YOU SHOULD SEND TO THE RIGHT PARAM ICE
    POSITIVE VALUE - YOU SHOULD SEND TO THE LEFT PARAM ICE
    0 - same cost, doesnt matter who to send to
    ******************
    """
 
 
    closer_d = sender.get_turns_till_arrival(closer_ice)
    closer_l = closer_ice.level
    #closer_needed = Ices.needed_before_capture(game, closer_ice)
    
    if closer_ice.is_underspam:
        closer_needed = closer_ice.needed
    else:
        closer_needed = Needed.get_needed(game, closer_ice, sender)[1]
 
    farther_d = sender.get_turns_till_arrival(farther_ice)
    
    if farther_ice.is_underspam:
        farther_needed = farther_ice.needed
    else:
        farther_needed = Needed.get_needed(game, farther_ice, sender)[1]
    #farther_needed = Ices.needed_before_capture(game, farther_ice)
    
    print "closer edneded: " + str(closer_needed)
    print "farhterre sdfendeded: " + str(farther_needed)
 
    return closer_needed - (closer_l * (farther_d - closer_d)) - farther_needed
    

def list_difference(list1, list2):
    """
    calcs the difference between list1 and list2 (list1 - list2) and returns a list
    """
    new_list = []
    for item in list1:
        if item not in list2:
            new_list.append(item)
    return new_list
    
def list_intersection(list1, list2):
    new_list = []
    for item in list1:
        if item in list2:
            new_list.append(item)
    return new_list
    
    
def upgrade_levels_cost(upgrading_ice, final_l):
    summ = 0
    
    cur_l = upgrading_ice.level
    c = upgrading_ice.upgrade_cost
    f = upgrading_ice.cost_factor
    
    #print "cur_l: " + str(cur_l)
    
    #print "final_l: " + str(final_l)
    
    for l in range(1, final_l + 1):
        summ += c + f * (l - 1) 
    return summ
    
    
def sort_dict_by_keys_d(old_dict, target):
    new_dict = {}
    for key in sorted(old_dict.keys(),
        key=lambda ice: (ice.get_turns_till_arrival(target),
            not ice.close_cloner, not ice.far_cloner, ice.id)):
                
        new_dict[key] = old_dict[key]
    return new_dict
    

def unit_level_difference(unit):
    
    target = unit.target
    members = unit.upgradeable_members
    
    #Ices.print_(members)
    
    target_level = target.level
    members_level = unit.sum_upgradeable_l
    
    total_amount = unit.total_attack_send + 1
    #print "total_attack_send: " + str(total_amount)
    
    time = unit.total_attack_time
    #print "time: " + str(time)
    
    upgrades_costs = {}
    
    for member in members:
        member.p_to_upgrade = \
            level_difference(member, target, time, override_level=1)
            
    #print "embers"
    
    #for ice in members:
        #print str(ice)
        #print ice.p_to_upgrade
    
    
    min_costs = sorted(members, key=lambda ice: (ice.p_to_upgrade,
        not ice.close_cloner, not ice.far_cloner, ice.id))[:target_level]
    
    #print "bestsss"
    
    #for ice in min_costs:
        #print str(ice)
        #print ice.p_to_upgrade
    
    return min_costs
    
    
    
    
    
    
    
    
