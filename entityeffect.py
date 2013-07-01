import messenger
import numpy


# Effect types in execution order
class EffectTypes(object):
    STATUS_REMOVER = 0
    BLOCKER = 1
    STATUS_ADDER = 2
    HEAL = 3
    DAMAGE = 4

    ALLTYPES = [STATUS_REMOVER, BLOCKER, STATUS_ADDER, HEAL, DAMAGE]


class DamageTypes(object):
    PHYSICAL = 0
    MAGIC = 1


class EffectQueue(object):
    def __init__(self):
        self._effect_queue = [None for x in range(EffectTypes.DAMAGE + 1)]
        for effect_type in EffectTypes.ALLTYPES:
            self._effect_queue[effect_type] = []

    def add(self, effect):
        self._effect_queue[effect.effect_type].append(effect)

    def remove(self, effect):
        self._effect_queue[effect.effect_type].remove(effect)

    def remove_status_adder_of_status(self, status_to_remove):
        for effect in self._effect_queue[EffectTypes.STATUS_ADDER]:
            if(effect.status_flag == status_to_remove):
                self._effect_queue[EffectTypes.STATUS_ADDER].remove(effect)

    def update(self):
        for effect_type_queue in EffectTypes.ALLTYPES:
            for effect in self._effect_queue[effect_type_queue]:
                effect.update()


class EntityEffect(object):
    def __init__(self, source_entity, target_entity,
                 time_to_live, effect_type):
        self.source_entity = source_entity
        self.target_entity = target_entity
        self.time_to_live = time_to_live
        self.effect_type = effect_type
        self.is_blocked = False

    def message(self):
        pass

    def update(self):
        pass

    def tick(self):
        if(self.time_to_live is numpy.inf):
            return
        self.time_to_live = self.time_to_live - 1
        if(self.time_to_live < 1):
            self.target_entity.effect_queue.remove(self)


class StatusRemover(EntityEffect):
    def __init__(self, source_entity, target_entity,
                 status_type_to_remove, time_to_live=1):
        super(StatusRemover,
              self).__init__(source_entity,
                             target_entity,
                             time_to_live,
                             EffectTypes.STATUS_REMOVER)
        self.status_type_to_remove = status_type_to_remove

    def update(self):
        effect_queue = self.target_entity.effect_queue
        effect_queue.remove_status_adder_of_status(self.status_type_to_remove)
        self.tick()


class StatusAdder(EntityEffect):
    def __init__(self, source_entity, target_entity,
                 status_flag, time_to_live=1):
        super(StatusAdder,
              self).__init__(source_entity,
                             target_entity,
                             time_to_live,
                             EffectTypes.STATUS_ADDER)
        self.status_flag = status_flag

    def update(self):
        self.target_entity.add_status(self.status_flag)
        self.tick()


class Damage(EntityEffect):
    def __init__(self, source_entity, target_entity, effect_type, damage,
                 damage_types=[DamageTypes.PHYSICAL], time_to_live=1):
        super(Damage, self).__init__(source_entity=source_entity,
                                     target_entity=target_entity,
                                     effect_type=effect_type,
                                     time_to_live=time_to_live)
        self.damage = damage
        self.damage_types = damage_types

    def message(self):
        message = "%s hits %s for %d damage." %\
            (self.source_entity.name, self.target_entity.name, self.damage)
        messenger.messenger.message(messenger.Message(message))

    def update(self):
        self.target_entity.hurt(self.damage)
        self.message()
        self.tick()