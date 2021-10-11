from __future__ import annotations
from abc import ABC, abstractmethod
from copy import copy
from typing import TypeVar, Generic, Set


class BattleEvent:
    def __init__(self, cause: BattleEvent = None):
        self.effects: Set[BattleEvent] = set()
        if cause is not None:
            cause.effects.add(self)
        self.cause = cause


E = TypeVar("E", bound=BattleEvent)


class EventObserver(Generic[E], ABC):
    """
    This is a general purpose Observer class.
    It does not know what subjects it has been registered to,
    but it can keep track of how many times it has been registered.
    """
    def __init__(self):
        self.subject_count: int = 0
        self.expired: bool = False

    """
    Once overriden, this code is used for handling events.
    Rather than directly calling handle_event, the subject calls the on_notify function.
    If the observer has already expired then handle_event is skipped.
    This function returns True if the subject should deregister this from after on_notify completes.
    This allows the observer to initiate deregistration one subject at a time, without expiring.
    If the function returns True when being called from multiple Subjects,
    it will be deregistered from all of them
    """
    @abstractmethod
    def handle_event(self, event: E) -> bool:
        pass

    """
    on_notify gets called the by EventSubject class when an event occurs.
    If the observer has not expired, then the handle_event code gets executed.
    Returns True if the subject should deregister the observer, either 
    because the observer has expired or because the event_handler specified that
    it should be deregistered by returning True.
    """
    def on_notify(self, event: E) -> bool:
        if not self.expired:
            return self.handle_event(event) or self.expired
        return self.expired

    def on_registration(self):
        self.subject_count += 1

    def on_deregistration(self):
        assert self.subject_count > 0
        self.subject_count -= 1

    def is_expired(self) -> bool:
        return self.expired


class EventSubject(Generic[E]):
    def __init__(self):
        self.observers: Set[EventObserver[E]] = set()

    def register_observer(self, observer: EventObserver[E]):
        self.observers.add(observer)
        observer.on_registration()

    def deregister_observer(self, observer: EventObserver[E]):
        self.observers.remove(observer)
        observer.on_deregistration()

    def notify_observers(self, event: E):
        current_observers = copy(self.observers)
        for observer in current_observers:
            if observer.is_expired():
                self.deregister_observer(observer)
            else:
                deregister = observer.on_notify(event)
                if deregister:
                    self.deregister_observer(observer)

    def clear_observers(self):
        current_observers = copy(self.observers)
        for observer in current_observers:
            self.deregister_observer(observer)


def notify_shared_observers(event: BattleEvent, *subjects: EventSubject):
    observer_list = set()
    for subject in subjects:
        observer_list |= subject.observers
    for observer in observer_list:
        if observer.is_expired():
            for s in subjects:
                s.deregister_observer(observer)
        else:
            deregister = observer.on_notify(event)
            if deregister:
                for s in subjects:
                    s.deregister_observer(observer)
