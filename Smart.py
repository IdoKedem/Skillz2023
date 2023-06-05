from collections import defaultdict
import Ices, Forces, Needed, math, Challenge1, Challenge2, Attack, Formulas
from Globals import Global

class SmartIce:
    
    def __init__(self, game, iceberg):
        
        #print "I AM THE ONE AND ONLY " + str(iceberg)
    
        self.game = game
        self.ice = iceberg
        self.cost_factor = iceberg.cost_factor
        self.is_icepital = iceberg.is_icepital
        self.level = iceberg.level
        
        self.penguin_amount = iceberg.penguin_amount
        self.penguins_per_turn = iceberg.penguins_per_turn
        self.upgrade_cost = iceberg.upgrade_cost
        self.upgrade_level_limit = iceberg.upgrade_level_limit
        
        self.upgrade_value = iceberg.upgrade_value
        self.owner = iceberg.owner
        self.id = iceberg.id
        self.unique_id = iceberg.unique_id
        
        self.can_upgrade = iceberg.can_upgrade
        self.did_upgrade = False
        
        self.is_max_level = iceberg.level == iceberg.upgrade_level_limit
        self.restruct_amount = self.penguin_amount
        
        
        #print "CREATUBG: " + str(self)
        self.enemy_forces = Forces.get_enemy_forces_to(self.game, self.ice)
        #print "my enemy_forces: " + str(self.enemy_forces)
        
        
        self.friendly_forces = Forces.get_friendly_forces_to(self.game, self.ice)
        
        self.enemy_sieges = Forces.get_enemy_sieges_to(self.game, self.ice)
        self.friendly_sieges = Forces.get_friendly_sieges_to(self.game, self.ice)
        
        self.p_to_upgrade = 0
        
        self.is_enemy_ter = self.set_is_enemy_ter()
        
        #self.clonespam = self.clonespam()
        #self.level += self.clonespam
        self.all_forces = self.get_all_forces_to()
        
        self.type = 'SmartIce'
        
        self.belong_to = self.ice_belong_to()
        self.restruct_belong_to = self.belong_to
        
        self.is_losing_ice_without_needed = self.is_losing_ice_without_needed()
        
        self.needed = -1
        self.max_times = 0
        self.set_underspams()
        
        self.set_is_losing()
        
        self.current = Ices.current_penguins(self.game, self.ice, self.all_forces)
        
        self.available_penguins = self.penguin_amount
        if -self.current < self.penguin_amount:
            if self.is_icepital:
                self.available_penguins = -self.needed
            else:
                self.available_penguins = -self.current
            
        self.is_under_siege = self.ice.is_under_siege
        
        self.siege_turns = 0
        if self.owner == self.game.get_myself() and self.enemy_sieges and self.is_under_siege:
            try:
                self.siege_turns = Global.siege_turns_left[self.enemy_sieges[0].id]
            except:
                self.siege_turns = self.game.siege_max_turns
        
        self.siege_amount = 0
        self.can_act = True
        
        self.wanna_upgrade = False
        self.to_be_sieged = False
        
        self.set_siege_amount()
         
        self.close_cloner = self.is_close_cloner()
        self.far_cloner = self.is_far_cloner()
        
        self.is_cloner_defender = False
        
        self.is_crucial = False
        
    def update_send(self, p):
        self.available_penguins -= p
        self.penguin_amount -= p
        self.current += p
        self.needed += p
        
        
        
    def can_send_penguins(self, dest, p):
        if isinstance(dest, SmartIce):
            return self.ice.can_send_penguins(dest.ice, p)
        return self.ice.can_send_penguins(dest, p)
    
    def can_upgrade(self):
        return self.ice.can_upgrade()
    
    def get_turns_till_arrival(self, dest):
        if isinstance(dest, SmartIce):
            return self.ice.get_turns_till_arrival(dest.ice)
        if dest:
            return self.ice.get_turns_till_arrival(dest)
        else:
            return 0
    
    def send_penguins(self, dest, p):
        self.update_send(p)
        #print "SENIFDNHG to " + str(dest)
        if isinstance(dest, SmartIce):
            self.ice.send_penguins(dest.ice, p)
        else:
            self.ice.send_penguins(dest, p)
    
    def upgrade(self):
        self.ice.upgrade()
        self.did_upgrade = True
        
    def is_losing_ice_without_needed(self):
        if self.owner == self.game.get_myself() and not self.enemy_forces:
            #print self
            #print "like a bird freeeee"
            return False
        return True
    
    def is_losing_ice(self):
        if self.belong_to == -1:
            return self.needed > 0 
        #print self
        #print self.needed
        return self.needed > 0 
    
    def is_far_cloner(self):
        #print self  
        
        if self.close_cloner:
            #print "KAROV"
            return False
        
        #my_icepital = self.game.get_my_icepital_icebergs()[0]
        my_icepital = self.game.get_all_icepital_icebergs()[0]
        #enemy_icepital = self.game.get_enemy_icepital_icebergs()[0]
        
        cloneberg = self.game.get_cloneberg()
        
        if not cloneberg:
            #print "no cloneberg"
            return False
        
        
        
        if not self.is_enemy_ter:
            if cloneberg.get_turns_till_arrival(my_icepital) > self.get_turns_till_arrival(cloneberg) \
                and Challenge2.should_acc_to_clone(self):
                    
                #print 'ANI ASSSSAAAF'
                return True
        
        #print "cap to clone: " + str(cloneberg.get_turns_till_arrival(my_icepital))
        #print "d tp c;pmme: " + str(self.get_turns_till_arrival(cloneberg))
        
        #print 'PAHOT ASAFI'
        return False
        
    def set_is_losing(self):
        self.is_losing = self.is_losing_ice_without_needed
        #print self
        if not self.is_losing_ice_without_needed:
            #print "BTCH"
            return
        
        if self.is_icepital:
            
            if not Ices.can_icepital_send(self.game, self, force=0):
                #print "I cant send madafaka"
                self.is_losing = True
                
            self.needed = Needed.needed_before_capture(self.game, self) + 1

            self.is_losing = self.is_losing_ice()
    
            #if not (self.owner == self.game.get_myself() and Attack.capital_lockdown(self)):
            #    return ######################
            
            first_needed = self.needed
            
            if not self.enemy_forces:
                self.is_losing = self.is_losing_ice()
                return
            
            farthest_enemy = self.enemy_forces[-1]
            farthest_enemy_d = farthest_enemy.turns_till_arrival
            
            t_farthest = Challenge1.calc_times(self.game, farthest_enemy_d) 
            for t in range(t_farthest):
                #print t
                d = Challenge1.calc_bullet_time(self.game, t, farthest_enemy_d)
                current_needed = -(self.penguin_amount + self.level * d)
                #print "net:" + str(Challenge1.net_bullet_coming(self.game, self.all_forces[-1], t))
                current_needed += Challenge1.net_bullet_coming(self.game, self.all_forces[-1], t)
                current_needed = int(math.ceil(current_needed))
                #print "current_needed : " + str(current_needed)
                if current_needed >= self.needed:
                    self.needed = current_needed
                    self.max_times = t
            
            min_time = Challenge1.max_bullet_time(self.game, farthest_enemy_d)
            sum_enemy = 0
            for force in self.enemy_forces:
                sum_enemy += force.penguin_amount
            
            raw_needed = sum_enemy - min_time * self.level - self.penguin_amount
            
            self.needed = max(self.needed, raw_needed)
            
            
                    #print "current_needed : " + str(current_needed)
            #print "Thats new"
            #print self.needed
            #print "max_times : " + str(self.max_times)
        
        else:
            #print "is_losing without needed"
            self.needed = Needed.needed_before_capture(self.game, self) + 1
            #print self
            #print "needed : " + str(self.needed)
            self.is_losing = self.is_losing_ice()
    
    def is_close_cloner(self):
        #print self
        
        
        #my_icepital = self.game.get_my_icepital_icebergs()[0]
        my_icepital = self.game.get_all_icepital_icebergs()[0]
        
        #enemy_icepital = self.game.get_enemy_icepital_icebergs()[0]
    
        cloneberg = self.game.get_cloneberg()
        
        if not cloneberg:
            #print "no cloneberg"
            return False
    
        if cloneberg.get_turns_till_arrival(my_icepital) / 2 < self.get_turns_till_arrival(cloneberg):
            #print "not close enough"
            return False
        
        #print "too good to be true"
        return True
    
    def __str__(self):
        return str(self.ice) + ", " +str(self.penguin_amount)
        
    def get_all_forces_to(self):
        forces = self.friendly_forces + self.enemy_forces
        forces = Forces.get_sorted(forces)
        return forces
    
    def ice_belong_to(self):
        
        me = self.game.get_myself()
        enemy = self.game.get_enemy()
        neutral = self.game.get_neutral()
        
        forces = self.all_forces
        forces = Forces.get_all_forces_arriving_in(self.game, self.ice, forces, 1)
        
        if self.ice.owner == me:
            control = -1
        elif self.ice.owner == enemy:
            control = 1
        else:
            control = 0
            
        p = self.penguin_amount
        p *= control
        
        combined_force = Forces.combined_force(self.game, self.ice, forces, 1, control)
        
        if control == 0:
            p1 = int(math.ceil(p / 2.0)) - combined_force[1]
            p2 = int(p / 2.0) - combined_force[0]
            p = p1 + p2
        
        else:
            p += combined_force[0]
            p -= combined_force[1]
        
        if p < 0:
            return -1
        elif p > 0:
            return 1
        return control


    def set_underspams(self):
        forces_dict = defaultdict(list)
        # {sent from: [force], ...}
        
        self.is_underspam, self.is_underspam_plus = False, False
        
        for force in self.enemy_forces:
            forces_dict[force.source].append(force)
            
            if len(forces_dict[force.source]) > 10:
                self.is_underspam = True
            if len(forces_dict[force.source]) > 20:
                self.is_underspam_plus = True
                return
            
        
    def clonespam(self):
        """
        Checks if the iceberg is spammed from cloneberg, if not - returns zero
        Returns the laser value from the cloneberg
        """
        
        cloneberg = self.game.get_cloneberg()
        
        if not cloneberg:
            return 0
        
        forces = self.friendly_forces if self.owner == self.game.get_myself() else self.enemy_forces
        laser = [force for force in forces if force.source == cloneberg]
        
        if not laser:
            return 0
       
        if self.get_turns_till_arrival(cloneberg) == len(laser):
           # print "clone motherfucking spam"
            forces = Formulas.list_difference(forces, laser)
            if self.owner == self.get_myself:
                self.friendly_forces = forces
                #print self.friendly_forces
            else:
                self.enemy_forces = forces
                #print self.enemy_forces
            return laser[-1].penguin_amount
        
        return 0
    
    
    def can_send_penguins_to_set_siege(self, dest, p):
        if isinstance(dest, SmartIce):
            return self.ice.can_send_penguins_to_set_siege(dest.ice, p)
        return self.ice.can_send_penguins_to_set_siege(dest, p)
        
        
    def send_penguins_to_set_siege(self, dest, p):
        self.update_send(p)
        #print self
        #print "sendfingh seidgfvie to : " + str(dest)
        if isinstance(dest, SmartIce):
            self.ice.send_penguins_to_set_siege(dest.ice, p)
        else:
            self.ice.send_penguins_to_set_siege(dest, p)
    
    
    def set_siege_amount(self):
        
        if self.ice.owner == self.game.get_myself():
            sieges = self.enemy_sieges
        else:
            sieges = self.friendly_sieges
        
        if self.is_under_siege:
            #print "AGHH"
            
            cost = self.game.go_through_siege_cost
            
            for siege in self.enemy_sieges:
                #print 'ASSSSAAAF'
                #print siege
                if siege.turns_till_arrival <= 1:
                    self.siege_amount += siege.penguin_amount * cost
                    #print self.siege_amount
            
            if self.siege_amount > self.penguin_amount:
                self.can_act = False
        
    def set_is_enemy_ter(self):
        my_first = self.game.get_my_icebergs()[0]
        if not self.game.get_enemy_icebergs():
            return False
            
        enemy_first = self.game.get_enemy_icebergs()[0]
        
        return my_first.get_turns_till_arrival(self.ice) > enemy_first.get_turns_till_arrival(self.ice)


def convert_ices(game, ices):
    """
    receives a list of ices and converts them all to smart ices
    returns a list of SmartIces
    """
    out = [SmartIce(game, ice) for ice in ices]
    Challenge2.set_cloner_defender(game, out)
    
    return out




class SmartForce:
    
    def  __init__(self, game=None, force=None, distance=0, amount=0, ice=None, destination=None, is_fake=False):
        
        if is_fake:
            self.is_fake = is_fake
            self.turns_till_arrival = distance
            self.penguin_amount = amount
            self.owner = ice.owner
            self.source = ice
            self.id = ice.id
            self.destination = destination
        else:
            self.game = game
            
            self.force = force
            self.id = force.id
            self.unique_id = force.unique_id
            self.owner = force.owner
            
            self.is_fake = False
            
            self.penguin_amount = force.penguin_amount
            
            self.current_speed = force.current_speed
            
            self.turns_till_arrival = force.turns_till_arrival
            self.source = force.source
            self.destination = force.destination
            
            self.cloneberg_pause_turns = force.cloneberg_pause_turns
            self.is_siege_group = force.is_siege_group
            
            self.cloneberg = game.get_cloneberg()
            
            self.is_siege_group = self.force.is_siege_group
            
            
            if self.destination == self.cloneberg:
                d = self.source.get_turns_till_arrival(self.cloneberg)
                
                self.turns_till_arrival += d + self.cloneberg_pause_turns
                self.penguin_amount *= self.game.cloneberg_multi_factor
                self.destination = self.source
                
                #print "HELLO! I AM A SMART FORCE!"
                #print self
                #print "I AM GOING TO " + str(self.destination)
                #print "MY OWNER IS: " + str(self.owner)
            
            

    def accelerate(self):
        self.force.accelerate()
        #self.penguin_amount = int(self.penguin_amount / self.game.acceleration_cost)
        #self.current_speed *= self.game.acceleration_factor
    
    def __str__(self):
        
        if self.is_fake:
            id_text = "FAKE: \n"
        id_text = "ID: " + str(self.id)
            
        amount_text = ", amount: " + str(self.penguin_amount)
        tta_text = ", TTA: " + str(self.turns_till_arrival)
        
        
        return id_text + amount_text + tta_text
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
    
