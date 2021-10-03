from abc import ABC
from typing import Iterator

from JrpgBattle.Party import Party, PartyIdentifier
from JrpgBattle.CharacterViews import PublicCharacterView, PrivateCharacterView

"""
These PartyView classes serve a very similar function to the CharacterView classes.
However, it should be noted that the inheritance hierarchy is slightly different here.
That's because the PublicPartyView's iterator returns a PublicCharacterView objects, while
PrivatePartyView's iterator returns PrivateCharacterView objects.
TODO: Since the Private and Public PartyViews are only contain getters, it may be safe for 
the Private view to extend the Public view. It's at least worth investigating
"""


class PartyView(ABC, PartyIdentifier):
    def __init__(self, party: Party):
        PartyIdentifier.__init__(self, party.name)
        self._party = party

    def is_wiped_out(self) -> bool:
        return self._party.is_wiped_out()

    def get_mp(self) -> int:
        return self._party.get_mp()


class PublicPartyView(PartyView):
    def __init__(self, party):
        super(PublicPartyView, self).__init__(party)
        
    @property
    def __iter__(self) -> Iterator[PublicCharacterView]:
        for character in self._party:
            yield PublicCharacterView(character)


class PrivatePartyView(PartyView):
    def __init__(self, party: Party):
        super(PrivatePartyView, self).__init__(party)

    @property
    def __iter__(self) -> Iterator[PrivateCharacterView]:
        for character in self._party:
            yield PrivateCharacterView(character)
