from collections import defaultdict
import Forces, Ices, Formulas, math, Smart, Units, Needed, LOL, Challenge1
import Challenge2
import Assassins as ass
from Globals import Global

def best_target(game, targets, ice):
    
    if not targets:
        return None
    
    best_target = targets[0]
    best_d = ice.get_turns_till_arrival(best_target)
    
    
    #print "checking target:"
    #print "of " + str(ice)
    
    #print "best target: " + str(best_target)
    #print "best_d: " + str(best_d)
    
    for cur_target in targets[1:]:
        
        cur_d = ice.get_turns_till_arrival(cur_target)
        same_d = False
 
        #print "cur_target: " + str(cur_target)
        #print "cur_d: " + str(cur_d)
 
        if best_d > cur_d:
            farther_ice = best_target
            closer_ice = cur_target
 
        elif cur_d > best_d:
            farther_ice = cur_target
            closer_ice = best_target
            
        else: 
            same_d = True
 
        if same_d:
            # CHECK DISTANCE DIFFERENCE DOC FOR EXPLANATION
            penguin_diff = Formulas.distance_difference(game, ice, best_target, cur_target)
            
            if penguin_diff < 0:
                best_target = cur_target
                best_d = cur_d
                
            elif not penguin_diff: # go to higher level ice
                if cur_target.level > best_target.level:
                    best_target = cur_target
                    best_d = cur_d
                    
            #print "best target: " + str(best_target)
            #print "best_d: " + str(best_d)
            continue
 
        # NOT SAME D:
 
        penguin_diff = Formulas.distance_difference(game, ice, farther_ice, closer_ice)
        #print "distance digfefcne: " + str(penguin_diff)
 
        # consider level differences
        if farther_ice.level > closer_ice.level:
            
            delta_d = ice.get_turns_till_arrival(farther_ice) - ice.get_turns_till_arrival(closer_ice)
            penguin_diff += Formulas.level_difference(closer_ice, farther_ice, delta_d, targets_compare=True)
            #print "penguin_diff: " + str(penguin_diff)
 
 
        if penguin_diff < 0:
            best_target = closer_ice
            best_d = ice.get_turns_till_arrival(best_target)
            
        elif not penguin_diff: # go to higher level ice
        
            if cur_target.level > best_target.level:
                best_target = cur_target
                best_d = cur_d
                
            elif cur_target.level == best_target.level:
                best_target = closer_ice
                best_d = ice.get_turns_till_arrival(best_target)
            
        else:
            best_target = farther_ice
            best_d = ice.get_turns_till_arrival(best_target)
        
        #print "best target: " + str(best_target)
        #print "best_d: " + str(best_d)
    
    #print "final best target for: " + str(ice) + " is: " + str(best_target)
    
    return best_target


def assemble_cpu(game, ID, capital, friendly_ices):
    """
    This function receives a capital that needs to be attacked and 
    the current friendly_ices, and returns a unit that contains only
    attackers and has the capital as the target
    """
    #print "ASSEMMMEBLE"
    needed = capital.needed
    
    #print "needed : " + str(needed) 
    
    attackers = []
    sum_attackers = 0
    
    potential_attackers = [ice for ice in friendly_ices]
    
    potential_attackers = Ices.get_sorted_by_distance(capital, potential_attackers)
    #print "ptui9wno  jaytroiwA: "
    Ices.print_(potential_attackers)
    
    if game.get_myself() == capital.owner:
        max_d = Challenge1.max_bullet_time(game, capital.enemy_forces[-1].turns_till_arrival)
        #print "max_d : " + str(max_d)
        
    #print "needed : " + str(needed) 
    
    for ice in potential_attackers:
        
        #print ice
        #print "sum_attackers : " + str(sum_attackers)
        if ice.is_icepital:
            continue
        
        p = ice.penguin_amount
        if capital.owner == game.get_myself():
            
            ice_d = ice.get_turns_till_arrival(capital)
            
            ice_bullet = Challenge1.max_bullet_time(game, ice_d)
            times = capital.max_times
            p = Challenge1.accelerated_amount(ice, times)
            
            #print "p : " + str(p)
            #print "ice_bullet : " + str(ice_bullet)
            #print "ice_d : " + str(ice_d)
            #print "ice_bullet : " + str(ice_bullet)
            
            if p == 0 or ice_bullet > max_d:
                continue
        if sum_attackers > needed:
            break
        #print p
        attackers.append(ice)
        sum_attackers += p
        friendly_ices.remove(ice)
        
        #print "appended"
    
    return Units.Unit(game, ID, capital, attackers, is_cpu=True)

def set_crucials(game, capital):
    
    crucials = [capital]
    
    icebergs = Ices.get_all_smarts(game)
    if capital:
        icebergs.remove(capital)
        capital.is_crucial = True
    
    icebergs = Ices.get_sorted_by_distance(capital, icebergs)
    
    d = 0
    for ice in icebergs:
        if ice.get_turns_till_arrival(capital) > d and d != 0:
            break
    
        ice.is_crucial = True
        
        #print "ice is crucial: " + str(ice)
        
        d = ice.get_turns_till_arrival(capital)
        
    
    
    

def get_losing_crucials(game, capital):
    """
    Determines if an iceberg is crucial based on its distance to
    the nearest capital
    """
    crucials = []
    
    capital = Smart.SmartIce(game, game.get_all_icepital_icebergs()[0])
    
    if capital.is_losing:
        return capital
    return []
    

def capital_lockdown(capital):
    if True:
        return
    if not "capital" in Global.lockdowns.keys():
    
        sum_penguin_amount = 0
        
        game = capital.game
        is_lock = False
        
        enemy_ices = Ices.get_enemy_smarts(game)
        closest = Ices.closest_to_target(capital, enemy_ices)
        
        min_times = Challenge1.calc_times(game, closest.get_turns_till_arrival(capital))
        
        
        for force in capital.enemy_forces:
            if force.penguin_amount > capital.penguin_amount:
                is_lock = True
                
            sum_penguin_amount += force.penguin_amount
            
        if not capital.is_underspam and sum_penguin_amount > capital.penguin_amount:
            is_lock = True
        
        sum_enemy_p_on_ices = 0
        for ice in enemy_ices:
            sum_enemy_p_on_ices += ice.penguin_amount
            
        sum_friendly_p_on_ices = 0
        for ice in Ices.get_friendly_smarts(capital.game):
            sum_friendly_p_on_ices += ice.available_penguins
        
        if sum_friendly_p_on_ices * game.acceleration_cost ** min_times <= sum_enemy_p_on_ices:
            is_lock = True
        
        if ass.scan_for_enemy_assassination(capital.game, Ices.get_enemy_smarts(capital.game), capital):
            is_lock = True
        
        Global.lockdowns["capital"] = is_lock
        
        
    return Global.lockdowns["capital"]


def get_units(game):
    """
    The function creates a list that describes the units according 
    to the current state of the game and the two-three best targets
    output: [unit_objects]
    """
    
    #print game.get_my_icebergs()
    friendly_ices = Ices.get_friendly_smarts(game)
    friendly_copy = [ice for ice in friendly_ices]
    
    my_capital = Ices.get_capital_from_smarts(friendly_ices, game.get_myself())
    #bailed = []
    
    only_crucial = get_losing_crucials(game, my_capital)
    
    #for ice in friendly_ices:
        #if ice.belong_to != -1 and ice.is_losing and not ice.is_icepital \
            #and not ice.friendly_forces and not ice in only_crucial and False:
            
            #Challenge2.bail(game, ice)
            #bailed.append(ice)
            
            
    #friendly_ices = Formulas.list_difference(friendly_ices, bailed)
    
    enemy_smarts = Ices.get_enemy_smarts(game)
    
    enemy_icepital = Ices.get_capital_from_smarts(enemy_smarts, game.get_enemy())
    
    remove_icepital = False
    
    #print "Global.cpu_forces = " + str(Global.cpu_forces)
    if my_capital:
        if Global.cpu_forces and my_capital.enemy_forces:
            #print "accelerate_defenses"
            
            capital_accelerates_done = Challenge1.accelerate_defenses(game, my_capital)
            sum_my_forces = sum(force.penguin_amount for force in Forces.get_friendly_forces_to(game, my_capital))
            sum_my_forces += my_capital.penguin_amount
            sum_enemy_forces = sum(force.penguin_amount for force in Forces.get_enemy_forces_to(game, my_capital))
            if capital_accelerates_done and sum_enemy_forces < sum_my_forces:
                remove_icepital = True
        
    
    if enemy_icepital:
        assassin = ass.get_assassin(enemy_icepital, friendly_ices)
        if assassin:
            friendly_ices.remove(assassin)
            if not ass.assassination_wait(assassin, enemy_icepital):
                ass.initiate_assassin(game, assassin, enemy_icepital)
        
   # if game.get_time_remaining() < -50:
       # print "Sorry mate the jolly friends were too much"
       # return None
    #print "friendly_ices : "
   # Ices.print_(friendly_ices)
    
    neutral_smarts = Ices.get_neutral_smarts(game)
    all_smarts = friendly_ices + enemy_smarts + Ices.get_neutral_smarts(game)
    #Ices.print_(friendly_ices)
    
    if my_capital:
        ass.scan_for_enemy_assassination(game, enemy_smarts, my_capital)
    
    targets = Ices.get_targets(game, all_smarts)
    if not targets:
        #print "zero bitches"
        return None
    
    #print "madafucking targets: "
    Ices.print_(targets)
    
    #for target in targets:
        #print "hi im target: " + str(target)
        #print "d to cap: " + str(target.get_turns_till_arrival(my_capital))
        #print "close cloner? " + str(target.close_cloner)
        #print "far cloner? " + str(target.far_cloner)
    
  #  if game.get_time_remaining() < -100:
    #    print "zero time to breath"
    #    return None
        
    
    #enemy_icepital = SmartIce.SmartIce(game, enemy_icepitals[0])
    
    
    to_remove = []
    upgrade_undersiege = []
    
    for ice in friendly_ices:
        if ice.is_icepital and not ice.is_underspam and capital_lockdown(ice):
            to_remove.append(ice)
            continue
        for target in targets:
            if target.ice == ice.ice:
                to_remove.append(ice)
                continue
        if ice in friendly_ices and ice.current >= 0:
            to_remove.append(ice)
        if not ice.can_act:
            #print "cant act baby"
            #print ice
            upgrade_undersiege.append(ice)
            
    friendly_ices = Formulas.list_difference(friendly_ices, to_remove)
    friendly_ices = Formulas.list_difference(friendly_ices, upgrade_undersiege)
    
    for ice in upgrade_undersiege:
        if Ices.can_upgrade_safely(game, ice):
            ice.upgrade()
    
    to_remove = []
    #print "targets : "
  # # #Ices.print_(targets)
    
    #print "friendly_ices after change: " 
    #Ices.print_(friendly_ices)
        
    units = []
    
    targets_to_remove = []
    
    capital_accelerates_done = False
    
    
    
    if len(targets) > 0:
        for target in targets:
            if target.is_icepital:
                if not target.is_underspam and target.owner == game.get_myself():
                    #print "cpu forces: " + str(Global.cpu_forces)
                    if Global.cpu_forces:
                        if remove_icepital:
                            targets_to_remove.append(target)
                            continue
                #print target 
                #print " is icepital"
                units.append(assemble_cpu(game, len(units) + 1, target, Ices.get_friendly_smarts(game)))
                targets_to_remove.append(target)
    
    targets = Formulas.list_difference(targets, targets_to_remove)
        
    if LOL.initiate_lolz(game, wait_turns=0):
        #print "lol"
        return
    
    #print targets
    #print "########"
    
    
    
    #print "friendly_ices : "
    #for ice in friendly_ices:
        #print ice
    
    


    
    num_cpu = len(units)
    
    units_dict = defaultdict(list)
    
    if not game.get_neutral_icebergs():
        
        #print "crucials: "
        #Ices.print_(only_crucial)
        
        #print "taergets: "
        #Ices.print_(targets)
        
        if only_crucial:
            #friendly_targets = []
            #intersection = Formulas.list_intersection(targets, only_crucial)
            #if intersection:
            #    targets = intersection
            targets = [ice for ice in targets if ice.belong_to == -1]
       # print "new_targets: "
        #Ices.print_(targets)
    
    for ice in friendly_ices:
        target = best_target(game, targets, ice)
        units_dict[target].append(ice)
    
    
    if targets:
        for ID, (target, members) in enumerate(units_dict.items()):
            if not target:
                continue
            if target in members:
                members.remove(target)
            units.append(Units.Unit(game, ID + num_cpu + 1, target, members))
            
        leftovers = {}
        to_remove = []
        for unit in units:
            if unit.FORCE_QUIT:
                #print "UNIT: " + str(unit.ID) + " QUIT"
                #print "DESCRIPTION:"
                #print(unit)
                
                to_remove.append(unit)
                
                #print "removing in attack: " + str(unit.ID)
                #print "target: " + str(unit.target)
                
                leftovers[unit.target] = unit.members
        units = Formulas.list_difference(units, to_remove)
        
        if len(to_remove) == 1:
            to_remove[0].upgrade_removed()
        
        elif len(leftovers) > 1:
            #print "CREATTING LEFTOVETER"
            target = Ices.get_leftover_target(leftovers)
            
            #print "leftover target: " + str(target)
            
            total_members = []
            for members in leftovers.values():
                total_members.extend(members)

            new_unit = Units.Unit(game, 10, target, total_members)
            #print
            #print
            #print "new_unit:"
            #print new_unit
            
            units.append(new_unit)
            
    return units
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
