import rx
from rx.core.typing import Disposable, Scheduler
from rx.operators import as_observable, subscribe_on
from rx.subject import Subject

from obvs.core import typing


class SubjectMessageBus(typing.MessageBus, Disposable):
    def dispose(self) -> None:
        self.subject.dispose()

    def __init__(self, scheduler: Scheduler = None):
        self.subject = Subject()
        if scheduler is None:
            self.msgs = self.subject.pipe(as_observable())
        else:
            self.msgs = self.subject.pipe(
                subscribe_on(scheduler),
                as_observable())

    async def publish(self, msg):
        self.subject.on_next(msg)
        return

    @property
    def messages(self) -> rx.Observable:
        return self.msgs
