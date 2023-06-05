import Ices, Needed, Forces, Challenge1, Formulas, math, copy, Challenge2
from collections import defaultdict
from Globals import Global

class Unit:
    
    def __init__(self, game, ID, target, members, is_cpu=False):
        
        self.game = game
        self.me = self.game.get_myself()
        self.ID = ID
        self.FORCE_QUIT = False
        self.is_cpu = is_cpu
        
        self.target = target
        
        #print "sikjfoid\spijgfx"
        #Ices.print_(Forces.get_enemy_forces_to(self.game, self.target))
        
        #print "dishinbiu"
        
        self.members = Ices.get_sorted_by_distance(target, members) 
        
        self.unit_history = [member for member in self.members]
        self.acteds = []
        
        
        self.cloneberg = self.game.get_cloneberg()
        
        self.my_icepital = None
        if self.game.get_my_icepital_icebergs():
            self.my_icepital = self.game.get_my_icepital_icebergs()[0]
            
        #self.enemy_icepital = game.get_enemy_icepital_icebergs()
        
        if not self.members:
            return
        
        self.set_vars(check_force_quit=True)
        if self.FORCE_QUIT:
            return
        
        self.filter_supporters()
        
        self.filter_attackers()
        
        if not (self.target.is_icepital and self.target.owner is self.me):
            self.filter_upgrades()
            
        self.filter_sweep_case()
        
        #if self.cloneberg:
            #self.filter_cloners()
        
        self.filter_sieges()
        
        if self.members:
            if not (self.target.is_icepital and self.target.is_underspam_plus):
                #print "SENOCE SER VARS"
                self.set_vars() # reassignment
        else:
            self.upgrade_removed()
        
    
    def __str__(self):
        ID_text = "UNIT ID: " + str(self.ID) + "\n"
        target_text = "TARGET: \n" + str(self.target) + '\n\n'
        
        if not self.members:
            return '\n' + ID_text + target_text + "EMPTY"
        
        unit_div_text = ""
        
        for attacker in self.attackers:
            unit_div_text += "ATTACKER: \n" + str(attacker) + "\n\n"
            unit_div_text += "SUPPORTERS: \n\n"
            
            for supporter in self.divisions[attacker]:
                unit_div_text += str(supporter) + '\n'

            unit_div_text += "\n"
        
        cloner_text = "CLONERS: \n"
        for cloner in self.cloning_amounts.keys():
            cloner_text += cloner + " \n"
        
        return '\n' + ID_text + target_text + unit_div_text #+ cloner_text
    
    
    
    def set_vars(self, check_force_quit=False):
        """
        this is used to set variables outside the _init_ in order to
        call it multiple times
        """
        
        #print "SET VARS:"
        
        self.divisions = self.divide_attack_support() # {attacker: [supporters], ...}
        self.attackers = self.divisions.keys()
        
        self.attackers = Ices.get_sorted_by_distance(self.target, self.attackers)
        
        self.cloning_amounts = {}
        
        #print "early div: "
        #print self
        
        #if self.cloneberg:
            #self.farthest_cloner = Ices.farthest_from_target(self.cloneberg, self.cloning_amounts.keys())
            #self.farthest_cloner_d = 0
        
            #if self.farthest_cloner:
                #self.farthest_cloner_d = self.farthest_cloner.get_turns_till_arrival(self.cloneberg)
                #self.farthest_cloner_d *= self.game.cloneberg_multi_factor
                #self.farthest_cloner_d += self.game.cloneberg_max_pause_turns
                
            
        self.farthest_attacker = Ices.farthest_from_target(self.target, self.attackers)
        
        self.farthest_attacker_d =  \
            self.farthest_attacker.get_turns_till_arrival(self.target)
        
        self.upgradeable_members = Ices.filter_max_level_ices(self.members)
        self.sum_upgradeable_l  = Ices.ices_l_sum(self.members)
        
        self.unit_p_sum = \
            Ices.sum_penguins_on_ices(self.game, self.members)# + self.sum_members_l
        
        self.set_total_attack_send()
        
        if check_force_quit and self.ID != 10 and not self.is_cpu:
            if self.unit_p_sum <= self.total_attack_send: #+ len(self.members):
                self.FORCE_QUIT = True
        if self.FORCE_QUIT:
            #print "unit_p_sum: " + str(self.unit_p_sum)
            #print "total_attack_send: " + str(self.total_attack_send)
            #print "quiting in vars: " + str(self.ID)
            #print "my members: "
            #Ices.print_(self.members)
            return
        
        self.same_attack_radius = Ices.same_radius(self.target, self.attackers)
        
        #print "total_attack_send vars: " + str(self.total_attack_send)
                                                
        #self.sum_net_force = \
            #Forces.get_net_force_sum(self.game, self.attackers, self.target)
        #print "sum_net_force : " + str(self.sum_net_force)
        #self.total_attack_send += self.sum_net_force
        #print "total_attack_send : " + str(self.total_attack_send)

        
        self.attackers_p_sum = \
        Ices.sum_penguins_on_ices(self.game, self.attackers)# - len(self.attackers)
        
        self.supporters_p_sum = self.unit_p_sum - self.attackers_p_sum
        
        self.sum_attackers_l = Ices.ices_l_sum(self.attackers)


        self.attacker_amounts = Formulas.get_relative_forces(self.game, self.target, 
                                            self.attackers, self.total_attack_send)
        self.acceleration_amounts = {}
        
        self.supporter_amounts = {}
        #print "attacker_amounts : " + str(self.attacker_amounts)
        
        if len(self.attacker_amounts) > 1:
            if not (self.target.is_icepital \
                    and self.target.owner is self.me):
            #if not self.target.is_underspam:
                self.update_attacker_amounts()
                
        elif len(self.attacker_amounts) == 1:
            
            attacker = self.attackers[0]
            send_amount = self.attacker_amounts[attacker]
            
            if self.target in Global.needed_dic.keys():
                if attacker in Global.needed_dic[self.target].keys():
                    
                    acc_amount = Global.needed_dic[self.target][attacker][0]
                    if acc_amount > 0:
                        send_amount += 1
                    #print "Needed : "+ str(Global.needed_dic[self.target][attacker])
                        
                    self.attacker_amounts[attacker] = \
                        Challenge1.calc_bullet_force(self.game, send_amount, acc_amount)
                    #print "self.attacker_amounts[attacker] : " + str(self.attacker_amounts[attacker])
        # {attacker: amount}
        
        #print "Unit: " + str(self.ID)
       # Ices.print_(self.members)
        #print "unit_sum: " + str(self.unit_p_sum)
        #print "total attacke send: " + str(self.total_attack_send)
        
        self.can_act = \
            bool(self.members) \
            and self.unit_p_sum > self.total_attack_send
                # + len(self.members)
        
        if not self.can_act and self.target.ice is self.my_icepital:
            self.can_act = True
            
        #print self.can_act
        
        #print "BEFORE UPDATE: \n"
        
        #print "supporters by var: "
        
        
        #print
        
        #print "supporters by dict: "
        
        #for lst in self.divisions.values():
           # Ices.print_(lst)
        
        
        #for sup, am in self.supporter_amounts.items():
         #   print str(sup) + ": " + str(am)
        
        #print "SET VARS UPFATE SUPPORTSD"
        
        self.update_supporters()
        
        self.set_total_attack_time()
        
        
         # {supporter: amount, ...}    
        
        #self.removed_ices = []
        
       # print "end of set vars"
       # print "attackers"
       # Ices.print_(self.attackers)
        #Ices.print_(self.supporters)
        
        
        #for lst in self.divisions.values():
         #   Ices.print_(lst)
        
        #for sup, am in self.supporter_amounts.items():
         #   print str(sup) + ": " + str(am)
    
    def get_farthest_supporter(self):
        """
        returns a tuple with the farthest supporter and his distance from his
        personal attacker
        """
        
        #print "GET FARTHEST SUPPORTER"
        
        max_supporter = None
        
        max_supporter_d = None
        
        #print "DICRT"
        #print self.divisions.items()
        
        for attacker, supporters in self.divisions.items():
            #print "attacker: " + str(attacker)
            #print "supporters: "
            #Ices.print_(supporters)
            
            if supporters:
                farthest_supporter = max(supporters, key=lambda ice: (ice.get_turns_till_arrival(attacker), ice.id))
                farthest_supporter_d = farthest_supporter.get_turns_till_arrival(attacker)
                
                if not max_supporter or max_supporter_d > farthest_supporter_d:
                    
                    max_supporter = farthest_supporter
                    max_supporter_d = farthest_supporter_d
                
        return max_supporter, max_supporter_d 
    
    def update_attackers(self):
        
        self.set_total_attack_time()
        self.update_attacker_amounts()
    
    def update_attacker_amounts(self):
       
        #print "UPDATE ATTACKER AMOUNTS KEDEM IS WORKING BAT ZONA!!!!!"
       
       
        if self.target.is_icepital and self.target.owner is self.me:
            return
        
        #print "type of a-amounts"
        #print type(self.attacker_amounts)
        
        self.attacker_amounts = \
            Formulas.sort_dict_by_keys_d(self.attacker_amounts, self.target)
            
        fakes = Forces.convert_ices_to_fake(self.attacker_amounts, self.target)
        
        
        for ice in self.attackers[::-1]:
            fakes_without = []
            for fake in fakes:
                if fake.id == ice.id:
                    continue
                fakes_without.append(fake)
            
            ice_needed = Needed.get_needed(self.game, self.target, ice, issac=True, fake_forces=fakes_without)
            
            print str(ice) + " needed: " + str(ice_needed)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        var = Needed.restruct_amounts_dict(self.game, self.target, self.attacker_amounts)
        
        #print "restruct_amounts_dict"
        #print var
        
        #print "attacker_amounts : " + str(self.attacker_amounts)
        
        
        #print "fakes!!!!!!!!"
        #Ices.print_(fakes)
        
        if not var:
            return
        
        for i in self.attacker_amounts.keys():
            if not isinstance(var, tuple):
                return
            #print "i : " + str(i)
            ice_stopped_at, continue_from_d = var
            
            
                
            attackers = Ices.filter_ices_after_arrival(self.attackers, self.target,
                                                                    continue_from_d)
            
            #print "friendly ice : " + str(self.farthest_attacker)
            #print "is_underspam : " + str(self.farthest_attacker.is_underspam)
            new_attacker_amounts = Formulas.get_relative_forces(self.game, self.target, 
                attackers, Needed.get_needed(self.game, self.target,
                            self.farthest_attacker, continue_from=continue_from_d)[1])
            
            
            #print "new_attacker_amounts : " + str(new_attacker_amounts)
            
            for attacker, amount in new_attacker_amounts.items():
                self.attacker_amounts[attacker] = amount
            
            #print "attacker_amounts yay-: " + str(self.attacker_amounts)
             
              
            var = Needed.restruct_amounts_dict(self.game, self.target,
                    new_attacker_amounts, continue_from=continue_from_d+1)
            
        
    def update_supporters(self):
        self.supporters = []
        
        #print "IN UPDATE_SUPPORTERS"
        #print "UPDATING SUPPORTERS"
        #print "SUPPPORTERS BY VAL"
        #Ices.print_(self.divisions.values())
        
        #print "DICT"
        
        div_items = self.divisions.items()
        
        for attacker, sub_supporters in div_items:
            #print "sub supporter: " + str(sub_supporters)
            #print str(len(sub_supporters))
            for supporter in sub_supporters:
                
                #print "available_penguins of: " + str(supporter)
               # print supporter.available_penguins
                
                if supporter.available_penguins > 0:
                    #print "adding: " + str(supporter)
                    self.supporters.append(supporter)
                else:
                    
                    #print "removing in update: " + str(supporter)
                    self.divisions[attacker].remove(supporter)
                    self.members.remove(supporter)
                    
                    #self.removed_ices.append(supporter)
                    if supporter in self.supporter_amounts.keys():
                        del self.supporter_amounts[supporter]
                #print "sub_supporters : " + str(sub_supporters)
                #print self.divisions.items()
       
       
        #print "SUPPORTERS BY VAR: " + str(self.supporters)
                
        self.farthest_supporter, self.farthest_supporter_d = self.get_farthest_supporter()
        #print "farathest suppotretr: " + str(self.farthest_supporter)
        
        
        self.set_total_attack_time()
        self.set_supporter_amounts_dict()
        
        #print str(self.supporters)
        
    def set_total_support_send(self):
        
        if not self.supporters:
            self.total_support_send = 0
            
        self.total_support_send = Needed.get_needed(self.game,
            self.target, self.farthest_supporter,
            override_d=self.total_attack_time)[1] #+ len(self.attackers)
        
        
        
        #print "total_support_send raw: " + str(self.total_support_send)
        #print
        
        for attacker, supporters in self.divisions.items():
            if not supporters:
                continue
            
            farthest_supporter = Ices.farthest_from_target(attacker, supporters)
            farthest_supporter_d = farthest_supporter.get_turns_till_arrival(attacker)
            
            #print "farthest_supporter: " + str(farthest_supporter)
            #print "to: " + str(attacker)
            
            if attacker.is_underspam:
                self.total_support_send += attacker.needed # friendly needed is negative
                self.total_support_send -= float(
                    farthest_supporter.get_turns_till_arrival(attacker) * attacker.level) ######
            else:
                # friendly needed is negative
                attacker_p_on_arrival = -Needed.get_needed(self.game, 
                              target=attacker, friendly_ice=farthest_supporter, disable_after=True)[1]
                
                #print "attacker_p_on_arrival: " + str(attacker_p_on_arrival)
                #print
                
                self.total_support_send -= attacker_p_on_arrival
                #print "total_support_send: " + str(self.total_support_send)
        

    def set_supporter_amounts_dict(self):
        """
        sets a dict in form of {supporter: amount, ...}    
        """
        if not self.supporters:
            return {}
        
        #print "set_supporter_amounts_dict: "
            
        #print "ID: " + str(self.ID)
        
        #print "supporters: "
        #Ices.print_(self.supporters)
        self.set_total_support_send()
        
        supporter_p_sum = \
            Ices.sum_penguins_on_ices(self.game, self.supporters)# - len(self.supporters)
        #supporter_p_sum += supporters_l_sum

        #print "supporter_p_sum : " +str(supporter_p_sum)
        #print "len supporters: " + str(len(self.supporters))
            
        #print "sum_attackers_l : " + str(self.sum_attackers_l)
        
        #print "total_support_send final: " + str(total_support_send)
        
        #print "total_attack_send: " + str(self.total_attack_send)
        
        for supporter in self.supporters:
            #print "supporter.penguin_amount: " + str(supporter.penguin_amount)
            
            self.supporter_amounts[supporter] = \
                supporter.penguin_amount * self.total_support_send / supporter_p_sum
                
            #print "result: " + str(self.supporter_amounts[supporter]) + '\n\n'
            
            #print str(self.supporter_amounts)
            
        self.supporter_amounts = Formulas.balance_sends(self.supporter_amounts, self.total_support_send)
        self.supporter_amounts = dict(sorted(self.supporter_amounts.items(),
            key=lambda item: (item[1], item[0].id), reverse=True))
        #print str(self.supporter_amounts)
        
        
    def set_total_attack_send(self):
        if self.target.is_underspam_plus or (self.target.is_icepital and self.target.owner == self.me):
            self.total_attack_send = self.target.needed
        else:
            #print "in else"
            #print "farthest_attacker: " + str(self.farthest_attacker)
            if len(self.attackers) == 1:
                self.total_attack_send = Needed.get_needed(self.game, self.target, 
                                                        self.farthest_attacker, issac=True)[1]
            else:
                self.total_attack_send = Needed.get_needed(self.game, self.target, 
                                                        self.farthest_attacker)[1]
                #print "we shur ataker is not wan"
                
        #print "unit: " + str(self.ID)
        #print self.farthest_attacker
        #print "total_attack_send: " + str(self.total_attack_send)
        #print "to: " + str(self.target)
        for attacker in self.attackers:
            self.total_attack_send += attacker.siege_amount
    
    def set_total_attack_time(self):
        self.total_attack_time = 0
        
        supporters_time, cloners_time = 0, 0
        
        if self.attackers:
            self.total_attack_time = self.farthest_attacker_d
        
        if self.supporters:
            supporters_time = self.farthest_supporter_d + 1
        #if self.cloning_amounts:
            #cloners_time = self.farthest_cloner_d
        
        self.total_attack_time += max(supporters_time, cloners_time)
    
    
    def divide_attack_support(self):
        """
        Returns a dict in the form of {attacker: [supporters], ...}
        """
        
        others = Ices.get_sorted_by_distance(self.target, self.members)
        
        #if self.my_icepital.get_turns_till_arrival(self.target.ice) \
            #< self.enemy_icepital.get_turns_till_arrival(self.target.ice):
                
            #return {ice: [] for ice in others}
        
        #if self.target.is_icepital:
            #return {ice: [] for ice in others}
        
        #if self.target.owner is self.game.get_neutral(): # \
            #or self.target.owner is self.game.get_myself():
                
            #return {ice: [] for ice in others}
        #if self.target.owner == self.game.get_neutral():
         #   return {ice: [] for ice in self.members}
            
        
        #Ices.print_(others)
        #print "DONE"
        
        attackers = [others[0]] # closest to target must be an attacker
        others.remove(others[0])
        
        divisions = defaultdict(list)
        
        divisions[attackers[0]] = []
       
        for ice in others:
            
            closest_attacker = Ices.closest_to_target(ice, attackers)
            
            if ice.get_turns_till_arrival(
                self.target) == closest_attacker.get_turns_till_arrival(self.target):
        
                attackers.append(ice)
                divisions[ice] = []
                continue
            
            if ice.get_turns_till_arrival(self.target) <= ice.get_turns_till_arrival(
                                                                closest_attacker):
                attackers.append(ice)
                divisions[ice] = []
                continue
            
            # add supporter
            divisions[closest_attacker].append(ice)
        
        #print "divisions: "
        #print divisions
        
        return sort_divisions(divisions)
    
    
    
    def filter_supporters(self):
        
        #print str(self)
        
        if self.attackers_p_sum > self.total_attack_send:
            for attacker, supporters in self.divisions.items():
               
                self.members = Formulas.list_difference(self.members, self.divisions[attacker])
                #self.removed_ices.extend(self.divisions[attacker])
                self.divisions[attacker] = []
            
            #print "removing all supporeters"
            self.update_supporters()

            return
        
        for attacker in self.attackers:
            if not self.divisions[attacker]:
                continue

            attacker_force = self.attacker_amounts[attacker]
            #print "attacker force: "
            #print attacker_force
            
            #print "SUPPORTERS"
            #Ices.print_(self.supporters)
            #print "done"
            
            #print "supporters by div: "
            #Ices.print_(self.divisions[attacker])
            
            supporters = self.divisions[attacker][:]
            
            for supporter in supporters:
                
                if supporter.available_penguins <= 0:
                    self.divisions[attacker].remove(supporter)
                    self.members.remove(supporter) # not needed for attack
                    #print "removed: " + str(supporter)
                
                if not self.divisions[attacker]:
                    continue
                
                farthest_supporter = Ices.farthest_from_target(attacker, 
                                                            self.divisions[attacker])
               # print "farthest_supporter: " + str(farthest_supporter)
                 
                        
                p_amount_on_arrival = -Needed.needed_before_capture(self.game,
                                    target=attacker, friendly_ice=farthest_supporter)[0]
                #print "p_amount_on_arrival: " + str(p_amount_on_arrival)
                
                if attacker_force <= p_amount_on_arrival:
                # will have enough by the time support arrives
                    #print "@@@@@@@@@@@@@@@@@@ \n"
                    #print str(self.divisions.values())
                    
                    #print "before removal: "
                    
                    self.divisions[attacker].remove(farthest_supporter)
                    self.members.remove(farthest_supporter) # not needed for attack

                    #print "REMOVED: " + str(farthest_supporter) + " 288"
                    #self.removed_ices.append(farthest_supporter)
                    
                    #print "after removal"
                    
                        #print supporter_1
                    
                    #print str(self.divisions.values())
                else:
                    break
     
        self.update_supporters()
    
    def filter_upgrades(self):
        """
        alters a divisions dict so that it remains without all the 
        icebergs that prefer to upgrade instead of attack, after reassignment
        """
        #print "FILTER UPGRADES"

        
        #print "ATTACKERS:"
        #print self.attackers
        #Ices.print_(self.attackers)
        #print "attacker_amounts"
        #print self.attacker_amounts
        #print "keys:"
        #Ices.print_(self.attacker_amounts.keys())
        #print "done"
        
        if len(self.game.get_my_icebergs()) == 1:
            return
        
        if self.target.level <= len(self.upgradeable_members):
            
            #print "testing ne wbitch"
            #print "attackers:"
            #Ices.print_(self.attackers)
            
            self.best_upgrades = Formulas.unit_level_difference(self)
            costs = [ice.p_to_upgrade for ice in self.best_upgrades]
            
            print "costs" + str(costs)
            
            upgrades_cost = sum(costs)
            
            #print "upgrades_cost" + str(upgrades_cost)
        
            if upgrades_cost <= self.total_attack_send:
                for ice in self.best_upgrades:
                    #print "now looking at: " + str(ice)
                    if Ices.can_upgrade_safely(self.game, ice):
                        ice.upgrade()
                    ice.wanna_upgrade = True
                    self.acteds.append(ice)
                    
                    if ice in self.attackers:
                        print "remove1"
                        self.attackers.remove(ice)
                    if ice in self.supporters:
                        print "remove12"
                        self.supporters.remove(ice)
                    if ice in self.members:
                        print "remove123"
                        self.members.remove(ice)
            return
                        
                #to_remove = []
                #for ice in self.members:
                    #if ice in self.attackers:
                        #print "remove1"
                       # self.attackers.remove(ice)
                    #if ice in self.supporters:
                        #print "remove12"
                        #self.supporters.remove(ice)
                   # if ice in self.members:
                        #print "remove123"
                        #to_remove.append(ice)
                #self.members = Formulas.list_difference(self.members, to_remove)
                
        
        attackers_to_remove = []
        supporters_to_remove = []
        
        for attacker in self.attackers:
            supporters = self.divisions[attacker][:]
            
            for supporter in supporters:
                
                #print supporter
                
                if supporter.level == supporter.upgrade_level_limit: #or \
                    #supporter.level + self.target.level > supporter.upgrade_level_limit:
                    #print 1
                    continue
                #if self.target.owner != self.game.get_enemy():
                    #if not Ices.can_upgrade_safely(self.game, supporter):
                        #print 2
                        #continue
                
                #print "upgrade-attack check: "
                
                
                #print "upgrades_cost: " + str(upgrades_cost)
                #print "wanna send: " + str(self.supporter_amounts[supporter])
                upgrades_cost =  \
                Formulas.level_difference(supporter, self.target, self.total_attack_time)
                
                if self.supporter_amounts[supporter] >= upgrades_cost:
                    supporters_to_remove.append(supporter)
                    self.members.remove(supporter)
                    #print "REMOVED: " + str(supporter) + " 328"
                    #self.removed_ices.append(supporter)
                    #if self.target.owner == self.game.get_enemy():
                    if Ices.can_upgrade_safely(self.game, supporter):
                        supporter.upgrade()
                    supporter.wanna_upgrade = True
                    self.acteds.append(supporter)
                    
                    
            self.divisions[attacker] = supporters
            
            # attacker check
            if attacker.level is attacker.upgrade_level_limit: #or \
                    #attacker.level + self.target.level > attacker.upgrade_level_limit:
                continue
            #if self.target.owner != self.game.get_enemy():
                #if not Ices.can_upgrade_safely(self.game, attacker):
                    #continue
            
            #if cant attack - conitnue
            
            if self.attacker_amounts[attacker] > Formulas.level_difference(
                        attacker, self.target, 
                        self.farthest_attacker.get_turns_till_arrival(self.target)):
                
                #if self.target.owner is self.game.get_enemy():
                    #if not Ices.can_upgrade_safely(self.game, attacker):
                        #continue
                
                #print str(attacker) + " rather upgrade"
                if attacker in self.members:
                    self.members.remove(attacker)
                print "REMOVED: " + str(attacker) +" 354"
                attackers_to_remove.append(attacker)
                #self.removed_ices.append(attacker)
                if Ices.can_upgrade_safely(self.game, attacker):
                    attacker.upgrade()
                attacker.wanna_upgrade = True
                self.acteds.append(attacker)
                
                
        self.attackers = Formulas.list_difference(self.attackers, attackers_to_remove)
        self.supporters = Formulas.list_difference(self.supporters, supporters_to_remove)
        #print "ATTACKERS:"
        #print self.attackers
        #Ices.print_(self.attackers)
        #print "attacker_amounts"
        #print self.attacker_amounts
        #Ices.print_(self.attacker_amounts.keys())
        
        # outside of for loop
    
    
    def filter_sweep_case(self):
        
        if self.target.owner != self.game.get_neutral():
           # print "im an asshole"
            return
        
        #print self.target
        
        enemy_forces = self.target.enemy_forces
        
        #for force in enemy_forces:
            #if force.owner is self.me:
                #enemy_forces.remove(force)
        
        #print enemy_forces
        
        if not enemy_forces:
            #print "im a pussy"
            return
        
        closest_enemy = enemy_forces[0]
        
        to_remove = []
        for attacker in self.attackers:
            #print "729 check is: " + str(attacker)
            
            if attacker.get_turns_till_arrival(self.target) <= closest_enemy.turns_till_arrival:
                print "removed 708: " + str(attacker)
                to_remove.append(attacker)
                self.members.remove(attacker)
        
        self.attackers = Formulas.list_difference(self.attackers, to_remove)
        
        #print "dumb motherfucker"
    
    def filter_cloners(self):
        
        if not self.supporters:
            self.update_supporters()
            return
        
        #print "filter clone:"
        
        self.cloning_amounts = defaultdict(lambda: 0)
        cloneberg_mult = self.game.cloneberg_multi_factor
        
        for attacker, supporters in self.divisions.items():
            
            if Challenge2.calc_clone_roundtrip(self.game, attacker) > self.farthest_supporter_d:
                continue
            
            for supporter in supporters:
                if self.supporters_p_sum - supporter.available_penguins < self.total_support_send: 
                    continue
                
                sup_amount = self.supporter_amounts[supporter]
                if attacker.available_penguins / cloneberg_mult < sup_amount:
                    continue
                if not Ices.can_send_safely(self.game, attacker, sup_amount / cloneberg_mult):
                    continue
                
                if attacker in self.attackers:
                    print "removed 738"
                    self.attackers.remove(attacker)
                
                self.cloning_amounts[attacker] += sup_amount / cloneberg_mult
                #print "removng sup: " + str(supporter)
                if supporter in self.supporters:
                    self.supporters.remove(supporter)
    
        self.update_supporters()
        #print "done"
        
    
    def filter_sieges(self):
        
        under_siege = [ice for ice in self.members if ice.is_under_siege]
        
        for ice in under_siege:
            if ice.siege_amount >= ice.available_penguins:
                if ice in self.supporters:
                    self.supporters.remove(ice)
                if ice in self.attackers:
                    self.attackers.remove(ice)
                if ice in self.cloning_amounts.keys():
                    del self.cloning_amounts[ice]
                
                self.members.remove(ice)
    
    def filter_attackers(self):
        
        #print "filter attackers!!!!"
        
        
        if self.target.owner is not self.game.get_neutral():
            return
        
        for attacker in self.attackers:
            if attacker.enemy_forces:
                return
        
        if self.is_cpu:
            return
        if len(self.attackers) == 1:
            return
        if self.supporters:
            return
        
        
        #print "not leaving!"
        
        to_remove = []
        for ind, attacker in enumerate(self.attackers[::-1]):
            ind = len(self.attackers) - (ind + 1)
            
            #print "attacker: " + str(attacker)
            
            if attacker is self.attackers[0]:
                #print "leaving now:"
                break
                
            remaining_p = self.attackers_p_sum - attacker.available_penguins
            #print 'rememvisnv p: ' + str(remaining_p)
            
            if remaining_p > self.total_attack_send:
                to_remove.append(attacker)
                del self.attacker_amounts[attacker]
                del self.divisions[attacker]
                self.members.remove(attacker)
                
                
                self.attackers_p_sum -= attacker.available_penguins
                self.unit_p_sum -= attacker.available_penguins
                self.sum_attackers_l -= attacker.level
            else:
                next_attacker = self.attackers[ind - 1]
                
                delta_d = attacker.get_turns_till_arrival(self.target) - next_attacker.get_turns_till_arrival(self.target)
                
                
                #print "in else:::::"
                if remaining_p + delta_d * (self.sum_attackers_l - attacker.level) > self.total_attack_send:
                    #print "xopgxig"
                    to_remove.append(attacker)
                    del self.attacker_amounts[attacker]
                    del self.divisions[attacker]
                    #self.members.remove(attacker)
                    
                    
                    self.attackers_p_sum -= attacker.available_penguins
                    self.unit_p_sum -= attacker.available_penguins
                    self.sum_attackers_l -= attacker.level
                else:
                    #print "fuck you"
                    break
                
        if to_remove:
            #print "removikng ::"
            #Ices.print_(to_remove)
            
            #print "attafckers before"
            
            self.attackers = Formulas.list_difference(self.attackers, to_remove)
        # 13, 6
        self.update_attackers()
    
    def add_accelerations(self):
        
        if self.target.belong_to != 0: # not neutral
            return
        
        if self.same_attack_radius:
            #print "Not worthy bc same_attack_radius"
            return
        
        farthest = self.farthest_attacker
        farthest_d = farthest.get_turns_till_arrival(self.target)
        
        if len(self.attackers) > 1:
            before_last = Ices.one_before_farthest_from_target(self.target, self.attackers)
            before_last_d = before_last.get_turns_till_arrival(self.target)
            
            if Challenge1.calc_bullet_time(self.game, 1, farthest_d) < before_last_d:
                return
        
        enemy_forces = self.target.enemy_forces
        
        
        enemy_forces = Forces.filter_forces_before_arrival(enemy_forces,
                farthest_d * self.game.acceleration_factor - 1) # *** time 2
        
        if enemy_forces:
            #print "there are enemy forcesa"
            return
        
        
        acc_profit = Challenge1.acceleration_profit(self.game,
            farthest, self.target, self.attacker_amounts[farthest])
                
        new_send_amount = \
            int(math.ceil(self.attacker_amounts[farthest] * self.game.acceleration_cost))
            
        if acc_profit <= 0: #shouldnt accelerate
            #print "no profit"
            return
    
        if Ices.can_send_safely(self.game, farthest, new_send_amount): # current turn check
            #print "updating dict samount"
            #print str(farthest) + " wanna acc now"
            self.attacker_amounts[farthest] = new_send_amount
            Global.accelerating_icebergs[farthest] = 1
            return
        
        spare_time = math.floor(acc_profit / self.target.level)
        
        if 0 < Needed.needed_before_capture(self.game, 
                farthest, force=new_send_amount, stop_at=spare_time):
            #print str(farthest) + " wanna acc wait"
            self.attacker_amounts[farthest] = new_send_amount        
        
        
        #next turn check
    
    
    
    def initiate(self):
        """
        Makes every iceberg in the unit send the proportional amount to the
        target or the fitting attacker
        """
        print str(self)
        
        if not self.members:
            return
        
        #self.add_accelerations()
        
        #print "IN INITIATE"
        #print "ATTACKERS:"
        #Ices.print_(self.attackers)
        
        #print "attacker_amounts"
        #print self.attacker_amounts
        #Ices.print_(self.attacker_amounts.keys())
        
        #print "history"
        #Ices.print_(self.unit_history)
        
        if not self.can_act:
            print "cant act"
            self.upgrade_removed()
            return
        ##################################################################
        
        #print "in initiate"
        
        #for supporters in self.divisions.values():
            #print "supporters by divisions"
            #Ices.print_(supporters)
        
        #print "supporters by class"
        #Ices.print_(self.supporters)
        
        #print "DONEEE"
        
        
        if self.supporters or self.cloning_amounts: # there is at least one supporter
        
            print "there are supporters/cloners"
            for attacker, supporters in self.divisions.items():
                #if self.game.get_time_remaining() < -170:
                  #  return 
                #supporter_amounts_dict is: {supporter: amount, ...}
                #print "Supporters send to " + str(attacker)
                for supporter in supporters:
                   # if self.game.get_time_remaining() < -170:
                       # return 
                    #print supporter
                    #print "amount : " + str(- self.supporter_amounts[supporter])
                    if Ices.can_send_safely(self.game, supporter, self.supporter_amounts[supporter]):
                        print "sending: " + str(self.supporter_amounts[supporter])
                        supporter.send_penguins(attacker, self.supporter_amounts[supporter])
                        self.acteds.append(supporter)
                        
            for cloner in self.cloning_amounts.keys():
                print "CLONERRRRR"
                print cloner
                if Ices.can_send_safely(self.game, attacker, sup_amount * cloneberg_mult):
                    cloner.send_penguins(self.cloneberg, self.cloning[cloner])
                    self.acteds.append(cloner)
                
                
            self.upgrade_removed()
            return 
        
        to_remove = []
        if self.target.is_icepital and self.target.owner is self.me:
            for attacker in self.attackers:
                send = min(attacker.penguin_amount, self.attacker_amounts[attacker])
                #print "HJ"
                attacker.send_penguins(self.target, send)
                Global.cpu_icebergs.append(attacker)
                
                print "removed 890"
                to_remove.append(attacker)
                self.acteds.append(attacker)
                
            #print "attacker amount: " + str(self.attacker_amounts[attacker])
            
            self.attackers = Formulas.list_difference(self.attackers, to_remove)
            self.upgrade_removed()
            return

    
        for attacker in self.attackers:
            #if self.game.get_time_remaining() < -170:
                #return 
            if self.attacker_amounts[attacker] <= 0:
                continue
            
            if self.attacker_amounts[attacker] <= attacker.siege_amount \
                or not Ices.can_send_safely(self.game, attacker, self.attacker_amounts[attacker]):
            
                #print str(attacker) + " cant send safely"
                #print  "cant attack safely"
                self.attackers = Formulas.list_difference(self.attackers, to_remove)
                self.upgrade_removed()
                return
            
       # print "Attackers attack " + str(self.target)
        # no supporters, send attacker force
        if len(self.attackers) == 1:
            print("i start bireudghjfkl")
            attacker = self.attackers[0]
            
            x = self.attacker_amounts[attacker]
            
            attacker_d = attacker.get_turns_till_arrival(self.target)
            
            acc_send_amount = int(math.ceil(x * self.game.acceleration_cost))
            
            if self.target.owner is self.game.get_neutral() and \
                x <= x * self.game.acceleration_cost - self.target.level * (attacker_d - Challenge1.calc_bullet_time(self.game, 1, attacker_d)) and not \
                self.target.enemy_forces:
                   
                print("mini sucsex")
                print(attacker.available_penguins)
                
                if attacker.available_penguins >= acc_send_amount:
                    attacker.send_penguins(self.target, acc_send_amount)
                    Global.accelerating_icebergs[attacker] = 1
                    print("sucsex")
                
            else:
                print("out 1")
                attacker.send_penguins(self.target, self.attacker_amounts[attacker])
                
                print "single attacker, sending: " + str(self.attacker_amounts[attacker])
                
                Global.accelerating_icebergs[attacker] = Global.needed_dic[self.target][attacker][0]
                
                print("acc amount")
                print(Global.needed_dic[self.target][attacker][0])
                
                self.acteds.append(attacker)
        else:
            for attacker in self.attackers:
                #print attacker
                #print "amount : " + str(self.attacker_amounts[attacker])
                
                attacker.send_penguins(self.target, self.attacker_amounts[attacker])
                self.acteds.append(attacker)
        
        self.target.is_losing = False
        
        self.upgrade_removed()
    
    
    
    
    def upgrade_removed(self):
        
        #print "acteds"
        #Ices.print_(self.acteds)
        
        #print "history"
        #Ices.print_(self.unit_history)
        total = Formulas.list_difference(self.unit_history, self.acteds)
        #total = Formulas.list_difference(total, self.attackers)
        #print "removed ices:"
        #Ices.print_(total)
        for removed in total:
            #print removed
            if removed in self.attackers:
                #Challenge2.spam_cloneberg(removed, self.target)
                continue
            
            if self.target.is_icepital and removed in self.attackers:
                continue
            if removed.is_underspam:
                continue
            
            #if Ices.can_upgrade_safely(self.game, removed):
                #print "im going in motherfucker"
                #removed.upgrade()
                #continue
            
            if not removed.is_max_level:
                
                if self.cloneberg:
                    
                    clone_total_d = Challenge2.calc_clone_roundtrip(self.game, removed)
                    clone_mult = self.game.cloneberg_multi_factor
                    
                    #print "IN HERE"
                    
                    #print "removed; " + str(removed)
                    #print "clone_total_d: " + str(clone_total_d)
                    
                    #print "ENTERING"
                    
                    upgrade_cost = Formulas.level_difference(removed,
                                        removed, clone_total_d, override_level=1)
                    
                    #if -upgrade_cost < clone_mult * removed.available_penguins:
                        #removed.send_penguins(self.cloneberg, removed.available_penguins)
                        #continue
                    
                    
                    p_on_arrival = -Needed.needed_before_capture(self.game, target=removed,
                        stop_at=clone_total_d + 1)
                        
                    missing_p = float(removed.upgrade_cost - p_on_arrival)
                    
                    time_till_upgrade = int(math.ceil(missing_p / removed.level))
                    
                    if clone_total_d >= time_till_upgrade:
                        if Ices.can_upgrade_safely(self.game, removed):
                            removed.upgrade()
                            #print 1
                            #Challenge2.spam_cloneberg(removed, self.target)
                        continue
                    
                    clone_send = int(math.ceil(p_on_arrival / clone_mult))
                    if Ices.can_send_safely(self.game, 
                                            removed, clone_send):
                        #print "removed to cloneberg"
                        removed.send_penguins(self.cloneberg, clone_send)
                        #print 2
                        
                elif Ices.can_upgrade_safely(self.game, removed):
                    removed.upgrade()
                    continue
                #Challenge2.spam_cloneberg(removed, self.target)
                
                continue
            
            
            
            send = int(round(removed.penguin_amount * 0.3))
            if not Ices.can_send_safely(self.game, removed, send):
                #Challenge2.spam_cloneberg(removed, self.target)
                continue
            
            #level_one = Ices.level_one(self.unit_history)
            #if level_one and removed.is_icepital:
               # print "1"
                #Ices.spam_send(removed, level_one[0], send)
            
            #elif self.attackers:
                #dest = Ices.get_closest_weakest(removed, self.attackers)
                #if dest:
                    #print 2
                    #removed.send_penguins(dest, send)
            elif self.members:
                cloneberg = self.game.get_cloneberg()
                if cloneberg:
                    print "bunch of prints"
                    
                    print "removed:" + str(removed)
                    
                    print "icoffr"
                    
                    dest = None
                    
                    try:
                        dest = min([ice for ice in Ices.get_friendly_smarts(self.game) 
                            if (ice.close_cloner or ice.far_cloner) and not ice.is_losing], 
                                key=lambda ice: (ice.get_turns_till_arrival(removed),  
                                ice.get_turns_till_arrival(cloneberg), ice.id))
                    except:
                        print(1)
                else:
                    dest = Ices.get_closest_weakest(removed, self.members)
                
                if dest:
                    #print 3
                    Ices.spam_send(removed, dest, send)
            #Challenge2.spam_cloneberg(removed)
    
    
def sort_divisions(divisions):
    
    sorted_dict = dict(sorted(divisions.items(),
        key=lambda item: (item[0].available_penguins, 
            sorted(item[1],
                key=lambda supporter: (supporter.available_penguins, supporter.id)), item[0].id)))
                
    return sorted_dict
    
    
    
    
    
