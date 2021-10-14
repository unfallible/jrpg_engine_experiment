# from json import JSONEncoder
import json
from fractions import Fraction
from JrpgBattle.Character import CharacterTemplate
from JrpgBattle.Attack import Attack, VanillaAttack
from typing import Dict, Callable


class JrpgDataManager:
    """
    The JrpgDataManager is used to load up attack and character data from JSON files.
    It also maintains functionality for looking up CharacterTemplates and Attacks by their names.
    """

    def __init__(self):
        self.character_cache: Dict[str, CharacterTemplate] = {}
        self.attack_cache: Dict[str, Attack] = {}

    def get_jrpg_decoder_func(self) -> Callable:
        def decoder_func(data: Dict):
            if '__class__' not in data:
                return data
            elif data['__class__'] == VanillaAttack.__name__:
                attack = VanillaAttack(name=data['template_name'],
                                       attack_type=data['type'],
                                       target_range=data['target_range'],
                                       stamina_point_cost=data['sp_cost'],
                                       damage=data['damage'])
                assert attack.name not in self.attack_cache
                self.attack_cache[attack.name] = attack
                return attack
            elif data['__class__'] == CharacterTemplate.__name__:
                # print(str(data['attack_list']))
                character = CharacterTemplate(name=data['template_name'],
                                              max_hp=data['max_hp'],
                                              attack_list={self.attack_cache[atk_name] for atk_name in data['attack_list']},
                                              parry_effectiveness=Fraction(data['parry_effectiveness']))
                assert character.template_name not in self.character_cache
                self.character_cache[character.template_name] = character
                return character
        return decoder_func


def encode_jrpg_data(obj):
    # print('in function')
    # print(obj)
    if isinstance(obj, Fraction):
        # print('got there')
        return obj.numerator, obj.denominator
    elif isinstance(obj, CharacterTemplate):
        return {'__class__': CharacterTemplate.__name__,
                'template_name': obj.template_name,
                'max_hp': obj.max_hp,
                'attack_list': list(obj.get_attack_list()),
                'parry_effectiveness': str(obj.get_parry_effectiveness())
                }
    elif isinstance(obj, VanillaAttack):
        return {'__class__': VanillaAttack.__name__,
                'template_name': obj.get_name(),
                'event_type': obj.get_attack_type(),
                'target_range': obj.get_target_range(),
                'sp_cost': obj.get_sp_cost(),
                'damage': obj.damage
                }
    raise TypeError(repr(obj) + " is not JSON serializable")


def decode_jrpg_data(dictionary: Dict):
    if '__class__' not in dictionary:
        return dictionary
    elif dictionary['__class__'] == VanillaAttack.__name__:
        return VanillaAttack(name=dictionary['template_name'],
                             attack_type=dictionary['event_type'],
                             target_range=dictionary['target_range'],
                             stamina_point_cost=dictionary['sp_cost'],
                             damage=dictionary['damage'])
    elif dictionary['__class__'] == CharacterTemplate.__name__:
        return CharacterTemplate(name=dictionary['template_name'],
                                 max_hp=dictionary['max_hp'],
                                 attack_list=dictionary['attack_list'],
                                 parry_effectiveness=dictionary['parry_effectiveness'])
