from collections import defaultdict
import Forces
import Smart
import Formulas


class Global:
    
    game = None
    
    enemy_forces = {}
    friendly_forces = {}
    all_forces = {}
    
    enemy_sieges = {}
    friendly_sieges = {}
    all_sieges = {}
    
    just_sent = {}
    just_sent_forces = []
    
    
    accelerating_icebergs = {}
    accelerating_forces = {}
    
    cpu_icebergs = []
    cpu_forces = []
    
    enemy_smarts = []
    friendly_smarts = []
    neutral_smarts = []
    
    # {target: {sender: (acc_times, needed)}}
    needed_dic = defaultdict(dict)
    
    
    check_cloner_defender = True
    
    lockdowns = {}
    
    set_siege_time = 6
    
    siege_turns_left = {}
    
    
    #pov = 0
    
    @staticmethod
    def update_accelerating_dicts():
    
        game = Global.game
        me = game.get_myself()
        
        for force in Forces.just_sent_forces(game):
            #print "force: " + str(force)
            
            if isinstance(force, Smart.SmartForce):
                force = force.force
            
            if not force.owner is me:
                continue
            
            #print "passed"
            
            for ice, amount in Global.accelerating_icebergs.items():
                if isinstance(ice, Smart.SmartIce):
                    ice = ice.ice
                    
                if ice is force.source:
                    #print "ADDING"
                    Global.accelerating_forces[force] = amount
                    
        Global.accelerating_icebergs = {}
        Global.just_sent_forces = []
        
        
    @staticmethod
    def accelerate_forces():
        #print "accelerate_forces"
        for force, amount in Global.accelerating_forces.items():
            #print force
            #print amount
            if amount > 0:
                #print "accing"
                force.accelerate()
                Global.accelerating_forces[force] -= 1
                
            if amount == 0:
                del Global.accelerating_forces[force]
            
    
    
    @staticmethod
    def update_accelerating_cpu():
    
        game = Global.game
        me = game.get_myself()
        
        to_remove = []
        for force in Global.cpu_forces:
            if isinstance(force, Smart.SmartForce):
                force = force.force
                
            if not force in game.get_my_penguin_groups():
                to_remove.append(force)
                
        Global.cpu_forces = Formulas.list_difference(Global.cpu_forces, to_remove)
        
        
        
        for force in Forces.just_sent_forces(game):
            #print "force: " + str(force)
            
            if not force.owner is me:
                continue
            
            #print "passed"
            
            for ice in Global.cpu_icebergs:
                if isinstance(ice, Smart.SmartIce):
                    ice = ice.ice
                    
                if ice is force.source:
                    #print "ADDING"
                    Global.cpu_forces.append(force)
                    
        Global.cpu_icebergs = []
        Global.just_sent_forces = []
    
    
    
        
def set_globals(game):
    
    Global.game = game
    
    Global.enemy_forces = {}
    Global.friendly_forces = {}
    Global.all_forces = {}
    Global.just_sent = {}
    
    
    Global.enemy_smarts = []
    Global.friendly_smarts = []
    Global.neutral_smarts = []
    
    Global.enemy_sieges = {}
    Global.friendly_sieges = {}
    Global.all_sieges = {}
    
    # {target: {sender: (acc_times, needed)}}
    #print Global.needed_dic
    Global.needed_dic.clear()
    #print Global.needed_dic
    
    Global.check_cloner_defender = True
    
    Global.lockdowns = {}
    
    for force_id, turns in Global.siege_turns_left.items():
        
        if turns == 1:
            del Global.siege_turns_left[force_id]
            continue
        
        Global.siege_turns_left[force_id] -= 1
    
    for force in game.get_enemy_penguin_groups():
        
        #print force
        
        if not force.is_siege_group:
            #print "not siege"
            continue
        
        if force.turns_till_arrival != 0:
            #print "on the way"
            continue
        
        if force.id in Global.siege_turns_left.keys():
            #print 'already exists'
            continue
        
        #print "MATZATIII"
        #print "MESHANE"
        Global.siege_turns_left[force.id] = game.siege_max_turns - 1
        
    
    
    
    
    
    
    
    
    
    
    
