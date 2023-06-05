from penguin_game import *
from Globals import Global
import math, Ices, Attack
    
    
def calc_clone_roundtrip(game, ice):
    
    clone = game.get_cloneberg()
    tao = game.cloneberg_max_pause_turns
    
    return ice.get_turns_till_arrival(clone) * 2 + tao
    

def spam_cloneberg(ice, target=None):
    
    #if target and target.is_crucial:
        #return 
    
    my_capital = Ices.get_my_smart_capital(ice.game)
    
    #not_owned_crucials = Attack.get_not_owned_crucials(ice.game)
    #print "not_owned_crucials: " + str(not_owned_crucials)
    
    if Attack.get_losing_crucials(ice.game, my_capital):
        return
    
    
    cloneberg = ice.game.get_cloneberg() 
    if not cloneberg or not (ice.close_cloner or ice.far_cloner) or ice.is_under_siege:
        return
    
    if ice.is_losing_ice_without_needed and not ice.is_losing:
        print "SPAM CLONEBERG"
        ice.send_penguins(cloneberg, int(math.ceil(-(ice.needed) / 2.0)))
        return
    print "send to cloneberg"
    
    if ice.far_cloner:
        #print "AVAL LAMAAAAA"
        Global.accelerating_icebergs[ice] = 1
    
    #print "lockdown?: " + str(Global.lockdowns["capital"])
    
    if not (ice.is_cloner_defender and Global.lockdowns["capital"]):
        #print "IM IDENTIFYING AS " + str(ice) + ", SENDING " + str(ice.available_penguins)
        ice.send_penguins(cloneberg, ice.available_penguins)
    else:
        ice.send_penguins(cloneberg, int(math.ceil(ice.available_penguins *0.1 )))
        #print "LOCKDONW OT SENDING!!!!!!"
        

def should_acc_to_clone(ice):
    game = ice.game
    acceleration_cost = game.acceleration_cost
    mult = game.cloneberg_multi_factor
    
    #print "AVAL"
    
    if acceleration_cost >= mult \
        or (ice.available_penguins <= math.ceil(acceleration_cost) and ice.owner is game.get_myself()) \
        or ice.enemy_sieges:
        
        return False
    
    return True
    
    
def set_cloner_defender(game, smarts):
    
    if not Global.check_cloner_defender:
        return
    
    cloneberg = game.get_cloneberg()
    cap = game.get_all_icepital_icebergs()[0]
    
    close_cloners = [ice for ice in smarts if ice.close_cloner]
    
    farthest = None
    if close_cloners:
        farthest = max(close_cloners, 
                key=lambda ice: (ice.get_turns_till_arrival(cloneberg), ice.id))
        farthest.is_cloner_defender = True
        #print "DEFEDEDERE: " + str(farthest)
            
    Global.check_cloner_defender = False
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
