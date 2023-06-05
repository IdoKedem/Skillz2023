from penguin_game import *
import Forces, Ices, Formulas, Attack, Smart, Needed, Challenge1, LOL, Challenge3, Challenge2
import Assassins as ass
from Globals import Global
import Globals

def do_turn(game):
    
    if game.turn == 1:
        game.get_my_icebergs()[0].send_penguins(game.get_all_icepital_icebergs()[0], 4)
        game.get_my_icebergs()[0].send_penguins_to_set_siege(game.get_enemy_icebergs()[0], game.get_enemy_icebergs()[0].penguin_amount / game.go_through_siege_cost)
    
    for force in game.get_my_penguin_groups():
        if force.id == 0:
            force.accelerate()
    
    enemy_icepital = None
    if game.get_enemy_icepital_icebergs():
        enemy_icepital = game.get_enemy_icepital_icebergs()[0]
        

    
    #print "accelerating icebersg: " + str(Global.accelerating_icebergs)
    #print "accelerate_forces: " + str(Global.accelerating_forces)
    
    Globals.set_globals(game)
    #print Global.enemy_forces
    Global.update_accelerating_dicts()
    Global.update_accelerating_cpu()
    
    #print "accelerating icebersg: " + str(Global.accelerating_icebergs)
    #print "accelerate_forces: " + str(Global.accelerating_forces)
    
    Attack.set_crucials(game, Ices.get_my_smart_capital(game))
    
    Global.accelerate_forces()
    
    Challenge1.accelerate_attacks(game)
    #print game.siege_max_turns 
    
    #if game.turn == 1:
    #    Global.pov = game.get_neutral_icebergs()[0].unique_id
    
    #print "CHECK"
    #for ice in game.get_all_icebergs():
    #    if ice.unique_id == Global.pov:
    #        print ice
    #print "CHECK"
    #Forces.get_enemy_forces_to2(game, enemy_icepital)
    
    #print Global.enemy_forces
    
    #set_globals(game)

    #print game.get_cloneberg()
    
    #for force in game.get_enemy_penguin_groups():
     #   print force
      #  print force.cloneberg_pause_turns
    
    #print "Tau:"
    #print game.cloneberg_max_pause_turns
    
    
    
    #ass.accelerate_assassinations(game)
    
    #if not game.get_my_icepital_icebergs():
        #return
    
    if 2 <= game.turn <= 5:
        game.get_my_icebergs()[0].upgrade()
        return
    
    units = Attack.get_units(game)
    #print "units : " + str(units)
    #avg_runtime = 0
    #runtimes = []

    if units:
        for unit in units:
            if not unit.FORCE_QUIT:
                unit.initiate()
    
    
    Challenge3.break_sieges(game)
    
    Challenge3.block_forces(game)
    
    Challenge3.block_ices(game)
    
    for ice in Ices.get_friendly_smarts(game):
        if not ice.did_upgrade and (ice.far_cloner or ice.close_cloner):
            #print ice
            #print "spam_cloneberg"
            Challenge2.spam_cloneberg(ice)
    
    #Challenge1.accelerate_neutral_attacks(game)
    
    #print "af"
    #print game.acceleration_factor
    #print "ac"
    #print game.acceleration_cost
    #
    #print game.get_max_turn_time()
    #print game.get_max_turn_time() - game.get_time_remaining()
    
