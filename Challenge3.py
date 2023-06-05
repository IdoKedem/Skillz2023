import Forces, Ices, Formulas, math, Needed
from collections import defaultdict
from Globals import Global



def decline_clones(game, friendly_ices, enemy_ices):
    
    pass
    

def sum_siege_range_forces(ice, radius=None):
    
    game = ice.game
    
    if not radius or radius > game.siege_max_turns or radius == -1:
        radius = game.siege_max_turns
    
    forces = Forces.get_enemy_forces_to(game, ice)
    
    summ = 0
    add_smalls = 0
    cost = game.go_through_siege_cost
    
    for force in forces:
        if Global.set_siege_time < force.turns_till_arrival < Global.set_siege_time + radius:
            if force.penguin_amount < cost:
                add_smalls = 1
            else:
                summ += force.penguin_amount - force.penguin_amount % cost
    
    return summ + add_smalls
    
def sum_blocked_by_siege(ice, radius=None):
    
    game = ice.game
    
    if not radius or radius > game.siege_max_turns or radius == -1:
        radius = game.siege_max_turns
    
    forces = Forces.get_enemy_forces_to(game, ice)
    
    summ = 0
    cost = game.go_through_siege_cost
    
    for force in forces:
        summ += force.penguin_amount
    
    return summ


def block_forces(game):
    
    print "SENDING BERAIJING: "
    
    enemy_ices = Ices.get_enemy_smarts(game)
    friendly_ices = [ice for ice in Ices.get_friendly_smarts(game) 
                        if not ice.is_losing]
    
    enemy_siegable_forces = []
    
    for ice in enemy_ices:
        #print "LOOGIKNG AT: " + str(ice)
        
        if ice.is_under_siege and ice.siege_turns > Global.set_siege_time + 1:
            #print "already has siege"
            continue
        
        if ice.to_be_sieged:
            continue
        
        #if not ice.is_losing: spiege l abal
        #    continue
        
        enemy_forces = Forces.get_enemy_forces_to(game, ice)
        
        if not enemy_forces:
            #print "no enemies cumming"
            continue
        #print "enemis yes cumming"
        #Ices.print_(enemy_forces)
        
        
        relevante_bad_boy = Forces.filter_forces_on_arrival(enemy_forces, Global.set_siege_time + 1)
        #print "arrogante bad boy: " + str(relevante_bad_boy)
        
        if not relevante_bad_boy:
            #print "not relavant"
            continue
        
        p_on_arrival = Needed.needed_before_capture(game, ice, stop_at=Global.set_siege_time + 1)
        #print "p_on_arrival: " + str(p_on_arrival)
        
        if p_on_arrival < 0:
            #print "starting control is me"
            continue
        control_change_d = Ices.control_changes_in(game, ice)
        #print "control_change_d: " + str(control_change_d)
        
        item = ice, sum_siege_range_forces(ice, radius=control_change_d), sum_blocked_by_siege(ice, radius=control_change_d)
        
        enemy_siegable_forces.append(item)
    
    
    enemy_siegable_forces.sort(key=lambda item: (item[1], item[0].id), reverse=True)
    
    #Ices.print_(enemy_siegable_forces)
    
    friendly_ices.sort(key=lambda ice: (ice.available_penguins, ice.id), reverse=True)
    
    for ice in friendly_ices:
        
        print "current bad boy: " + str(ice)
        
        if not enemy_siegable_forces:
            break
        
        to_remove = []
         
        for enemy in enemy_siegable_forces:
            #print "enemy in block_forces"
            #print enemy[0]
            #print enemy
            
            needed_siege = int(math.ceil(enemy[1] / (float)(game.go_through_siege_cost)))
            sender_siege = ice.siege_amount
            
            #print needed_siege
            #print sender_siege
            
            if Ices.can_send_safely(game, ice, needed_siege) and enemy[2] > sender_siege:
                print "siegel"
                ice.send_penguins_to_set_siege(enemy[0], needed_siege + sender_siege)
                
                enemy[0].to_be_sieged = True
                to_remove.append(enemy)
            else:
                print "cant send bad boy"
                pass
        
        enemy_siegable_forces = Formulas.list_difference(enemy_siegable_forces, to_remove)


def block_ices(game):
    
    enemy_ices = Ices.get_enemy_smarts(game)
    enemy_ices.sort(key=lambda ice: (ice.available_penguins, ice.id), reverse=True)
    
    friendly_ices = [ice for ice in Ices.get_friendly_smarts(game) 
                    if not ice.is_losing and (not ice.wanna_upgrade or 
                    (ice.enemy_sieges and ice.siege_turns == 0))]
    friendly_ices.sort(key=lambda ice: (ice.available_penguins, ice.id), reverse=True)
    
    print "friendly_ices: "
    Ices.print_(friendly_ices)
    
    for enemy in enemy_ices:
        #print "enemy : " + str(enemy)
        if enemy.is_under_siege and enemy.siege_turns > Global.set_siege_time + 1:
            continue
        if enemy.to_be_sieged:
            continue
        if enemy.enemy_forces:
            continue
        if not enemy.is_losing:
            continue
        
        p_on_arrival = float(enemy.penguin_amount + Global.set_siege_time * enemy.level)
        send_amount = int(math.ceil((p_on_arrival / game.go_through_siege_cost) / 2.0))
        
        to_remove = []
        
        for friendly in friendly_ices:
            print str(friendly) + " trying for " + str(enemy)
            print friendly.siege_turns
            
            if Ices.can_send_safely(game, friendly, send_amount) and not friendly.is_under_siege:
                    
                #print "enemy : " + str(enemy)
                #print "friendly : " + str(friendly)
                friendly.send_penguins_to_set_siege(enemy, send_amount)
                enemy.to_be_sieged = True
                
                to_remove.append(friendly)
                break
        friendly_ices = Formulas.list_difference(friendly_ices, to_remove)
    

def break_sieges(game):
    
    friendly_ices = Ices.get_friendly_smarts(game)
    trash_target = Ices.get_enemy_smarts(game)[0]
    cost = game.go_through_siege_cost
    
    #print "\nBREAK_SIEGES:"
    #print "go_through_siege_cost = " + str(cost)
    
    for ice in friendly_ices:
        
        if not ice.is_under_siege:
            continue
        
        siege_amount = ice.siege_amount
        to_send = siege_amount
        
        if ice.available_penguins < siege_amount:
            continue
        
        sum_siege_waste = 0
        
        #print "ice : " + str(ice)
        #print "siege ends in " + str(ice.siege_turns)
        
        for force in ice.friendly_forces:
            
            #print "HIII " + str(force)
            
            if force.turns_till_arrival == 1:
                
                siege_amount -= (force.penguin_amount - (force.penguin_amount % cost))
                to_send = siege_amount
                
                if siege_amount <= 0:
                    break
                
                #print "distance 1 passed"
                
                continue
            
            if force.turns_till_arrival > ice.siege_turns:
                #print "byebye"
                break
            
            force_waste = force.penguin_amount % cost
            
            siege_amount -= (force.penguin_amount - force_waste)
            sum_siege_waste += force.penguin_amount % cost
            
            if siege_amount <= 0:
                #print "breaked"
                break
            
            #print "Im adding daddy"
            #print "adding: " + str(force_waste)
            #print "sum_siege_waste" + str(sum_siege_waste)
        
        #print "sum_siege_waste : " + str(sum_siege_waste)
        #print "to_send: " + str(to_send)
        
        if sum_siege_waste > to_send > 0:
            if Ices.can_send_safely(game, ice, to_send) and not ice.did_upgrade:
                #print "BREAK SIEGE"
                ice.send_penguins(trash_target, to_send)  
                
                
                
                
                
                
                
                
                
                
                
                
                
                
