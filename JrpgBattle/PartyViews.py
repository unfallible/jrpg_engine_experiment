from abc import ABC

from JrpgBattle.Party import Party
from JrpgBattle.CharacterViews import PublicCharacterView, PrivateCharacterView

"""
These PartyView classes serve a very similar function to the CharacterView classes.
However, it should be noted that the inheritance hierarchy is slightly different here.
That's because the PublicPartyView's iterator returns a PublicCharacterView objects, while
PrivatePartyView's iterator returns PrivateCharacterView objects.
TODO: Since the Private and Public PartyViews are only contain getters, it may be safe for 
the Private view to extend the Public view. It's at least worth investigating
"""

class PartyView(ABC):
    def __init__(self, party: Party):
        self._party = party

    def is_wiped_out(self) -> bool:
        return self._party.is_wiped_out()

    def get_mp(self) -> int:
        return self._party.get_mp()


class PublicPartyView(PartyView):
    def __init__(self, party):
        super(PublicPartyView, self).__init__(party)
        
    @property
    def __iter__(self) -> PublicCharacterView:
        for character in self._party:
            yield PublicCharacterView(character)


class PrivatePartyView(PartyView):
    def __init__(self, party):
        super(PublicPartyView, self).__init__(party)

    @property
    def __iter__(self) -> PrivateCharacterView:
        for character in self._party:
            yield PrivateCharacterView(character)
