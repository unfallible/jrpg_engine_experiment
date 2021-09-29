# from json import JSONEncoder
import json
from fractions import Fraction
from JrpgBattle.Character import CharacterTemplate, Multiplier
from JrpgBattle.Attack import Attack, VanillaAttack
from typing import Dict


def encode_jrpg_data(obj):
    print('in function')
    print(obj)
    if isinstance(obj, Fraction):
        print('got there')
        return (obj.numerator, obj.denominator)
    elif isinstance(obj, CharacterTemplate):
        return {'__class__': CharacterTemplate.__name__,
                'template_name': obj.template_name,
                'max_hp': obj.max_hp,
                'offensive_type_affinities': list(obj.get_offensive_type_affinities()),
                'defensive_type_affinities': list(obj.get_defensive_type_affinities()),
                'attack_list': list(obj.get_attack_list()),
                'parry_effectiveness': str(obj.get_parry_effectiveness())
                }
    elif isinstance(obj, VanillaAttack):
        return {'__class__': VanillaAttack.__name__,
                'template_name': obj.get_name(),
                'type': obj.get_attack_type(),
                'target_range': obj.get_target_range(),
                'sp_cost': obj.get_sp_cost(),
                'mp_cost': obj.get_mp_cost(),
                'damage': obj.damage
                }
    raise TypeError(repr(obj) + " is not JSON serializable")

def decode_jrpg_data(dict: Dict):
    if dict['__class__'] == VanillaAttack.__name__:
        return VanillaAttack(name=dict['template_name'],
                             attack_type=dict['type'],
                             target_range=dict['target_range'],
                             stamina_point_cost=dict['sp_cost'],
                             mana_point_cost=dict['mp_cost'],
                             damage=dict['damage'])
    elif dict['__class__'] == CharacterTemplate.__name__:
        return CharacterTemplate(name=dict['template_name'],
                                 max_hp=dict['max_hp'],
                                 offensive_type_affinities=dict['offensive_type_affinities'],
                                 defensive_type_affinities=dict['defensive_type_affinities'], )
