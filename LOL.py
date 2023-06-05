import Forces, Ices, Formulas, Needed, Attack, Smart, Challenge1
from Globals import Global


def destroy(game):
    #print "LOLLING"
    friendly_ices = Ices.get_friendly_smarts(game)
    
    enemy_icepital = game.get_all_icepital_icebergs()[0]
    
    for ice in friendly_ices:
        if ice.is_icepital:
            continue
        ice.send_penguins(enemy_icepital, ice.penguin_amount)
        #Global.accelerating_icebergs[ice] = \
            #Challenge1.calc_times(game, ice.get_turns_till_arrival(enemy_icepital))
    
def initiate_lolz(game, wait_turns=0):
    """
    returns true if lolz are initiated
    """
    
    me = game.get_myself()
    enemy = game.get_enemy()
    
    enemy_ices = Ices.get_enemy_smarts(game)
    
    enemy_icepital = Ices.get_capital_from_smarts(enemy_ices, game.get_enemy())
    if not enemy_icepital:
        return False
        
    friendly_ices = Ices.get_friendly_smarts(game)
    
    my_capital = Ices.get_capital_from_smarts(friendly_ices, game.get_myself())
    
    #print "my_capital: " + str(my_capital)
    if my_capital:
        friendly_ices.remove(my_capital)
    
    if not friendly_ices:
        return False
    
    farthest_friendly = max(friendly_ices, key=lambda ice: ice.get_turns_till_arrival(enemy_icepital))
    farthest_friendly_d = farthest_friendly.get_turns_till_arrival(enemy_icepital)
    
    sum_friendly_penguins = 0
    for ice in friendly_ices:
        if wait_turns:
            sum_friendly_penguins -= Needed.needed_before_capture(game, ice, stop_at=wait_turns+1)
        else:
            sum_friendly_penguins += ice.penguin_amount
        sum_friendly_penguins -= ice.siege_amount
    
    
    sum_enemy_penguins = Ices.sum_penguins_on_ices(game, enemy_ices)
    for ice in friendly_ices:
        for force in ice.enemy_forces:
            sum_enemy_penguins += force.penguin_amount
    
    #print "sum_enemy_penguins: " + str(sum_enemy_penguins)
    
    
    forces_to_enemy_icepital = Forces.just_sent(game)[enemy_icepital]
    sum_forces_to_enemy_icepital = \
        sum(force.penguin_amount for force in forces_to_enemy_icepital)
    
    #print "sum_friendly_penguins: " + str(sum_friendly_penguins)
    
    my_farthest_from_cap = Ices.farthest_from_target(enemy_icepital, friendly_ices)
    max_d_from_cap = my_farthest_from_cap.get_turns_till_arrival(enemy_icepital)
    
    if game.max_turns_without_icepital - me.turns_without_icepital <= max_d_from_cap + 3 or \
        game.max_turns_without_icepital - enemy.turns_without_icepital <= max_d_from_cap + 3:
        
        destroy(game)
        print("NEW LOL INTIATATED")
        return True
    
    
    if sum_forces_to_enemy_icepital > sum_enemy_penguins:
        #print "first one"
        destroy(game)
        return True
        
    is_early_game = sum_friendly_penguins + sum_enemy_penguins <= 200
    
    max_time = Challenge1.max_bullet_time(game, farthest_friendly_d)
    
    enemy_icepital_p = \
        sum_enemy_penguins + enemy_icepital.level * (max_time + wait_turns)
    
    #print "enemy_icepital_p: " + str(enemy_icepital_p)
    if my_capital:
        if my_capital.is_losing:
            return False
        
    if not game.get_neutral_icebergs() and not is_early_game:
        #print "sum_friendly_penguins: " + str(sum_friendly_penguins)
        
        if sum_friendly_penguins / (game.acceleration_cost * Challenge1.calc_times(game, farthest_friendly_d)) > enemy_icepital_p: 
            destroy(game)
            #print "second"
            return True
        








