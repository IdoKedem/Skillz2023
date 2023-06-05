from penguin_game import *
from collections import defaultdict
import Smart, Ices, Forces, math, Challenge1
from Globals import Global



def insert_attacker_amounts(game, target, forces, attacker_amounts):
    """
    This function receives a list of forces and the attacker_amounts
    dict, and inserts the values (forces) into the fitting places
    in the forces list
    """
    inserted = []
    attackers = Ices.get_sorted_by_distance(target, attacker_amounts.keys())
    #print "attackers:"
    #Ices.print_(attackers)
    united_attackers = Ices.unite_ices(game, target, attackers)
    
    if not forces:
        return [ice for ice in united_attackers.values()]
    
    
    for force in forces:
        if isinstance(force, list):
            d = force[0].get_turns_till_arrival(target)
        else:
            d = force.turns_till_arrival
            
        for attacker_d, attackers in united_attackers.items():
            
            if d >= attacker_d:
                inserted.append(attackers)
                del united_attackers[attacker_d]
            else:
                inserted.append(force)
                break
            
    #print "inserted :" + str(inserted)
    return inserted
    
    # [force, force, force [ice, ice], force, [ice], ....]
    
    
def needed_before_capture(game, target, friendly_ice=None, force=0, is_target_upgrading=False, continue_from=0, override_d=0, stop_at=None, forces=None):
    """
    This function is used to determine how many penguins will be
    on the target upon the arrival of the force from friendly_ice and
    who they belong to
    NEGATIVE VALUE - friendly penguins
    POSITIVE VALUE - enemy penguins
    
    friendly_ice OPTIONAL - no friendly_ice means all forces 
    
    ***********
    NEEDED = PENGUIN AMOUNT ON TARGET
    ***********
    """
    #print ""
    #print "New MOther Fucker : **************" 
    #print "TARGET : " + str(target)
    me = game.get_myself()
    enemy = game.get_enemy()
    
    force_ = force
    needed = target.penguin_amount - force
    
    #if hasattr(target, 'available_penguins'):
    #    needed = target.available_penguins - force
    
        # An updating variable
    if isinstance(target, Smart.SmartIce):
        control = target.belong_to
    else: 
        control = Ices.ice_belong_to(game, target)
    if target.owner == me:
        needed *= -1
        control = -1

    if not forces:
        if isinstance(target, Smart.SmartIce):
            forces = target.get_all_forces_to()
            #print target.friendly_forces
            #print target.enemy_forces
            #print "forces"
        else:
            forces = Forces.get_all_forces_to(game, target)
         
    if target.owner == game.get_neutral() and control != 0:
        needed -= target.level * control
 
    #print "belong to : " + str(control)
    #print forces
    
    if friendly_ice:
        ice_to_target_d = friendly_ice.get_turns_till_arrival(target)
        #print "ice_to_target_d : " +str(ice_to_target_d)
        
    if override_d:
        ice_to_target_d = override_d
        #print "ice_to_target_d : " +str(ice_to_target_d)
    
    
    
    if continue_from != 0:
        if friendly_ice:
            forces = Forces.filter_forces_before_arrival(forces, ice_to_target_d)
    
    united_forces = Forces.unite_forces(game, forces)
    #print "united_forces : " +str(united_forces)
    used_forces = []
    
    d = continue_from # Force distance to target
    l = target.level
    p = 0
    
    if is_target_upgrading:
        l += 1
        needed += 1
    
    if friendly_ice:
        needed_dict = {i: needed for i in range(3)}
   # print "needed : " + str(needed)
    for force in forces:
        if friendly_ice:
            if force.turns_till_arrival > ice_to_target_d:
                break
        #print "NEEDED TO: " + str(target)
        #print "force is: " + str(force)
        
        if stop_at and force.turns_till_arrival > stop_at:
            needed += force_
            break
        
        if friendly_ice:
            for times, acc_needed in needed_dict.items():
                dis = Challenge1.calc_bullet_time(game, times, ice_to_target_d)
                if dis < force.turns_till_arrival and dis > d:
                    needed_dict[times] += (dis - d) * l * control
                   # print "times : " + str(times)
                    #print "needed : " + str(needed_dict[times])
        #print "united_forces" + str(united_forces)
        #print "used_forces" + str(used_forces)
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
                
                p_total = Forces.combined_force(game, target, forces, d, control) 
                #print "p_total " + str(p_total) + " for forces : " + str(force)
                used_forces.append(d)
            else:
                continue
        
        is_friendly_target = control == -1
        
       # print "continue_from : " + str(continue_from)
        #print "delta_d : " + str(delta_d)
        #print "l : " + str(l)
        #print "control : " + str(control)
                
        needed += delta_d * l * control # Adding target production in delta_d
        
        #print "needed: " + str(needed)
        
        needed1 = int(math.ceil(needed/2.0))
        needed2 = int(needed/2.0)
        #print "needed1 : " + str(needed1)
        #print "needed2 : " + str(needed2)
        
        if force.turns_till_arrival in united_forces:
            p = p_total[1]
            is_friendly_force = True
            #print "pF : " + str(p)
            needed1 -= p
            p = p_total[0]
            is_friendly_force = False
            
            #print "needed1 : " + str(needed1)
            #print "pE : " + str(p)
            if control == 0:
                needed2 -= p
            else:
                needed2 += p
           # print "needed2 : " + str(needed2)
            needed = needed1 + needed2
           # print "needed : " + str(needed)
            if needed > 0:
                control = 1
            elif needed < 0:
                control = -1
                
        else:
            if is_friendly_force:
                if not is_friendly_target:
                    if p > needed:
                        control = -1
                    #elif p == needed:
                     #   control = 0
                elif needed == 0: # Neutral
                    control = -1
                needed -= p
     
            elif not is_friendly_force:
                if control == 0 and needed != 0: # Special Case:
                    # Enemy force arriving to an initially neutral ice
                    if p > needed:
                        needed = p - needed
                        control = 1
                    elif p < needed:
                        needed -= p
                    else: # Nullify the target
                        needed = 0
                else:
                    if is_friendly_target: # needed < 0
                        if p > -needed:
                            control = 1
                        #elif p == needed:
                         #   control = 0
                    elif needed == 0: # Neutral
                        control = 1
                    needed += p
        #print "needed " + str(needed) + " after the force : " + str(force)
        if friendly_ice:
            for times, acc_needed in needed_dict.items():
                if Challenge1.calc_bullet_time(game, times, ice_to_target_d) > force.turns_till_arrival:
                    needed_dict[times] = needed
                    
        
    if friendly_ice:
        # Applying "for" logic for delta d till friendly_ice
        #print "ice_to_target_d : " + str(ice_to_target_d)
        #print "d : " + str(d)
        if not forces:
            for times, acc_needed in needed_dict.items():
                dis = Challenge1.calc_bullet_time(game,times, ice_to_target_d)
                #print "dis : " + str(dis)
                #print "needed : " + str(needed_dict[times])
                #print "control : " + str(control)
                #print "d : " + str(d)
                #print "l : " + str(l)
                needed_dict[times] += (dis - d) * l * control
               # print "times : " + str(times)
               # print "needed : " + str(needed_dict[times])
        else:
            for times, acc_needed in needed_dict.items()[1:]:
                dis = Challenge1.calc_bullet_time(game, times, ice_to_target_d)
                if dis > d:
                    #print "dis : " + str(dis)
                    #print "needed : " + str(needed_dict[times])
                    #print "control : " + str(control)
                    #print "d : " + str(d)
                    #print "l : " + str(l)
                    needed_dict[times] += (dis - d) * l * control
                    #print "times : " + str(times)
                    #print "needed : " + str(needed_dict[times])
            
            needed_dict[0] += (ice_to_target_d - d) * l * control
        
        #print "needed before : " + str(needed_dict[0])
        
        if target.owner == game.get_neutral() and target.enemy_forces:
            return {0: needed_dict[0]}
        
        return needed_dict
    
    if stop_at:
        needed += (stop_at - d) * l * control
    
    return needed
    
 
def needed_after_capture(game, target, friendly_ice, override_d=0, forces=None):
    """
    This function is used to determine how many penguins will be
    on the target upon the arrival of the final force and who they 
    belong to
    NEGATIVE VALUE - friendly penguins
    POSITIVE VALUE - enemy penguins
 
    ***********
    NEEDED = PENGUIN AMOUNT ON TARGET
    ***********
    """

    
    me = game.get_myself()
    
    if not forces:
        if target.type == 'SmartIce':
            forces = target.all_forces
        else:
            forces = Forces.get_all_forces_to(game, target)
    
    if override_d:
        ice_to_target_d = override_d
    else:
        ice_to_target_d = friendly_ice.get_turns_till_arrival(target)
    
    #print "forces after : "
    
    #for force in forces:
        #print force
    
    united_forces = Forces.unite_forces(game, forces)
    used_forces = []
    
    needed_dict = {times: 0 for times in range(3)} # An updating value
    needed = 0
    control = -1 # Target ownership
    
    d = friendly_ice.get_turns_till_arrival(target) # Force distance to target
    l = target.level
    
    for force in forces:
        
        if force.turns_till_arrival <= Challenge1.calc_bullet_time(game, 2, ice_to_target_d):
            continue
        
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
                
                p_total = Forces.combined_force(game, target, forces, d, control) 
                #print "p" + str(p) + "for forces : " + str(force)
                used_forces.append(d)
            else:
                continue
        
        is_friendly_target = control == -1
        
        needed -= delta_d * l # Adding target production in delta_d
        #print "needed after 284 : " + str(needed)
        if force.turns_till_arrival in united_forces:
            p = p_total[1]
            is_friendly_force = True
            needed1 = int(math.ceil(needed/2.0))
            needed2 = int(needed/2)
            
        if is_friendly_force:
            if force.turns_till_arrival in united_forces:
                needed1 -= p
                p = p_total[0]
                is_friendly_force = False
                
            else:
                needed -= p
        elif not is_friendly_force:
            if force.turns_till_arrival in united_forces:
                needed2 += p
                needed = needed1 + needed2
            else:
                needed += p
        #print "needed after 305 : " + str(needed)
        
        for times, acc_needed in needed_dict.items():
            if Challenge1.calc_bullet_time(game, times, ice_to_target_d) < force.turns_till_arrival:
                acc_needed = needed
                needed_dict[times] = acc_needed
        
    return needed_dict
 
 
def get_needed(game, target, friendly_ice, continue_from=0, override_d=0, issac=False, disable_after=False, fake_forces=None):
    """
    This function returns the amount of penguins needed for friendly_ice to
    capture the target with one of our penguins left on it
    NEGATIVE VALUE - friendly penguins
    POSITIVE VALUE - enemy penguins
 
    ***********
    NEEDED = PENGUIN AMOUNT ON TARGET
    ***********
    """
    #print "\nTARGET : " 
    #print "target : " + str(target)
    #print "friendly_ice : " + str(friendly_ice)
    
    if target in Global.needed_dic.keys() and issac and not override_d:
        #print 1
        if friendly_ice in (Global.needed_dic[target]).keys():
            #print 2
            return Global.needed_dic[target][friendly_ice]
    #print 3
    if isinstance(target, Smart.SmartIce):
        forces = target.get_all_forces_to()
        #print target.friendly_forces
        #print target.enemy_forces
        #print "forces"
    else:
        forces = Forces.get_all_forces_to(game, target)
        
    if fake_forces:
        forces = Forces.get_sorted(forces + fake_forces)
        
    
    needed_dict_before = needed_before_capture(game, target, friendly_ice,
            continue_from=continue_from, override_d=override_d, forces=forces) 
    #print "needed_before_capture : " + str(needed_dict_before)
    # If friendly_ice == target, needed = target.penguin_amount
    
    
    for times, needed in needed_dict_before.items():
        
        d = Challenge1.calc_bullet_time(game, times, target.get_turns_till_arrival(friendly_ice))
        #print "d : " + str(d)
        
        #print forces#OZOZOZOZOZOZOZ
        if not Forces.filter_forces_before_arrival(forces, d):
            control = target.belong_to
            
        elif needed > 0:
            control = 1
        else: ######################           
            control = -1
        #if issac:
        #    print "control : " + str(control) 
        needed1 = int(math.ceil(needed/2.0))
        needed2 = int(needed/2.0)
        #if issac:
        #    print "needed1 : " + str(needed1)
        #    print "needed2 : " + str(needed2)
        
        #print Forces.combined_force(game, target, forces, friendly_ice.get_turns_till_arrival(target), control)
        p_total = Forces.combined_force(game, target, forces, d, control)
        #print "p_total : " + str(p_total)
        needed1 -= p_total[1]
        if control == 0:
            needed2 -= p_total[0]
        else:
            needed2 += p_total[0]
        needed = needed1 + needed2 
        #if issac:
         #   print "needed1 : " + str(needed1)
          #  print "needed2 : " + str(needed2)
        
        needed_dict_before[times] = needed
        #if issac:
        #    print "times : " + str(times)
        #    print "needed while : " + str(needed)
    
    if not disable_after:
        needed_dict_after = needed_after_capture(game, target, friendly_ice, override_d=override_d, forces=forces)
        #print "dfsgisjgk"
        #print needed_dict_before
        
        
        for times, needed in needed_dict_before.items():
            if needed_dict_after[times] > 0:
                needed += needed_dict_after[times]
                needed_dict_before[times] = needed
                
    #print "FROM : " + str(friendly_ice)
    #print "TO " + str(target)
    #print "total needed " + str(needed_dict_before)
    #print "DONE"
    
    #print "Dict"
   # print needed_dict_before
    
    min_key = min(needed_dict_before, key=lambda key: (Challenge1.calc_bullet_force(game, needed_dict_before[key] + 1, times)))
    #print "keys"
    #print min_key
    #print "dpme"
    
    Global.needed_dic[target][friendly_ice] = min_key, needed_dict_before[min_key]
    
    if not issac:
        #print "last needed bitch issac : " + str(needed_dict_before[0])
        return 0, needed_dict_before[0]
    return (min_key, needed_dict_before[min_key])
    

def restruct_amounts_dict(game, target, amounts_dict, continue_from=0):
    
    """
    This function is used to determine how many penguins will be
    on the target upon the arrival of the force from friendly_ice and
    who they belong to
    NEGATIVE VALUE - friendly penguins
    POSITIVE VALUE - enemy penguins
    
    friendly_ice OPTIONAL - no friendly_ice means all forces 
    
    ***********
    NEEDED = PENGUIN AMOUNT ON TARGET
    ***********
    """
    #print "RESTRUCT BITCHHHHH"
    if len(amounts_dict) == 1:
        return 0
    #print "TARGET"
    #print target
    #print "amounts_dict"
    #print amounts_dict
    
    me = game.get_myself()
    enemy = game.get_enemy()
    
    #print "continue_from : " + str(continue_from)
    #print "target : " + str(target)
    #print "target belong_to : " + str(target.belong_to)
    #print "target amount : " + str(target.penguin_amount)
    
    needed = target.restruct_amount # An updating variable
    if isinstance(target, Smart.SmartIce):
        control = target.restruct_belong_to
    else: 
        control = ice_belong_to(game, ice)
    
    #print "control : " +str(control)
    if control == -1:
        needed *= -1
    
    #print "belong to : " + str(control)
    if isinstance(target, Smart.SmartIce):
        forces = target.all_forces
    else:
        forces = Forces.get_all_forces_to(game, target)
    #print forces
    
    if continue_from != 0:
        forces = Forces.filter_forces_after_arrival(forces, continue_from)
    
    united_forces = Forces.unite_forces(game, forces)
    
    forces = insert_attacker_amounts(game, target, forces, amounts_dict)
    
    used_forces = []
    
    p = 0
    d = continue_from # Force distance to target
    l = target.level
    count_attackers = 0
    
    #for force in forces:
    #    print force
    #print amounts_dict
    #print needed
    for force in forces:
        p_total = 0
        if count_attackers == len(amounts_dict) - 1:
            #print "fuck this shit im out"
            return 0
        is_friendly_target = control == -1
        if isinstance(force, list): # [ice, ...]
            #print "DETECTING"
            d = force[0].get_turns_till_arrival(target)
            delta_d = force[0].get_turns_till_arrival(target) - d
            
            if d in united_forces and d not in used_forces:
                p_icebergs = amounts_dict[force[0]]
            else:
                p = 0
                
            for ice in force:
                #print ice
                if d not in united_forces: # A single force
                    p += amounts_dict[ice]
                    count_attackers += 1
                    if count_attackers == len(amounts_dict):
                        #print "i am out baby"
                        return 0
                    #print "sum send : " + str(p)
                    is_friendly_force = True
                
                else:# Multiple forces
                    if d not in used_forces: # Wasnt used
                        count_attackers += 1
                        p_icebergs -= amounts_dict[ice] 
                        
                        count_attackers += 1
                        if count_attackers == len(amounts_dict):
                            #print "iam out baby"
                            return 0
                     #   print "  send : " + str(p)
                        is_friendly_force = True
                        #print "p" + str(p) + "for forces : " + str(force)
                        
                        
            needed += delta_d * l * control # Adding target production in delta_d
        
        else:  # if force
            #print "united_forces" + str(united_forces)
            #print "used_forces" + str(used_forces)
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
                    
                    p_total = Forces.combined_force(game, target, forces, d, control) 
                    #print "p" + str(p) + "for forces : " + str(force)

                    used_forces.append(d)
                else:
                    continue
                   
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
                    control = 1
                elif needed < 0:
                    control = -1
        #print "d " + str(d)
        #print "p " + str(p)
        
        if isinstance(force, list) and d in united_forces and d not in used_forces:
            
            p_total = Forces.combined_force(game, target, forces, d, control) 
            
            needed1 = int(math.ceil(needed/2.0))
            needed2 = int(needed/2.0)  
            
            if force[0].get_turns_till_arrival(target) in united_forces:
                p = p_total[1] + p_icebergs
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
                    control = 1
                elif needed < 0:
                    target.restruct_amount = abs(needed + (l * control) - p)
                    target.restruct_belong_to = -1 
                    return (force, d)
                
                used_forces.append(d)
     
        elif isinstance(force, list) or force.turns_till_arrival not in united_forces:
            if is_friendly_force:
                if not is_friendly_target:
                    if p > needed:
                        if isinstance(force, list):

                            target.restruct_amount = abs(needed + (l * control) - p)
                            target.restruct_belong_to = -1 
                            return (force, d)
                        control = -1
                elif needed == 0: # Neutral
                    control = -1
                needed -= p
     
     
            elif not is_friendly_force:
                if control == 0 and needed != 0: # Special Case:
                    # Enemy force arriving to an initially neutral ice
                    if p > needed:
                        needed = p - needed
                        control = 1
                    elif p < needed:
                        needed -= p
                    else: # Nullify the target
                        needed = 0
                else:
                    if is_friendly_target: # needed < 0
                        if p > -needed:
                            control = 1
                    elif needed == 0: # Neutral
                        control = 1
                    needed += p
        
        #print "needed " + str(needed) + " after the force : " + str(force)
    
    return needed
    
    
    
    
    
    
    
    
    
