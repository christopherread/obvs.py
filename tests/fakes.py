import abc
import rx
from rx.operators import share
from rx.subject import Subject

from obvs.core.typing import ServiceEndpoint, ServiceEndpointClient


class FakeMessageOne:
    @property
    def data(self) -> str:
        return self._data

    def __init__(self, data: str):
        self._data = data


class FakeCommandOne(FakeMessageOne):
    def __init__(self, data: str):
        super().__init__(data)


class FakeServiceTwo(abc.ABC):
    pass


class FakeServiceEndpoint(ServiceEndpoint, ServiceEndpointClient):
    @property
    def events(self) -> rx.Observable:
        return self.events_subject

    async def send(self, command):
        print(self.name, 'send', command)
        self.commands_subject.on_next(command)

    def get_responses(self, request) -> rx.Observable:
        print(self.name, 'get_responses', request)
        return self.responses_subject.pipe(
            rx.operators.filter(lambda r: r.request_id == request.request_id),
            share())

    @property
    def requests(self) -> rx.Observable:
        return self.requests_subject

    @property
    def commands(self) -> rx.Observable:
        return self.commands_subject

    async def publish(self, ev):
        print(self.name, 'publish', ev)
        self.events_subject.on_next(ev)

    async def reply(self, request, response):
        print(self.name, 'reply', request, response)
        self.responses_subject.on_next(response)

    def can_handle(self, message) -> bool:
        print(self.name, 'can_handle', message, self.service_type)
        return isinstance(message, self.service_type)

    @property
    def name(self) -> str:
        return 'FakeServiceEndpoint'

    def dispose(self) -> None:
        self.events_subject.dispose()
        self.commands_subject.dispose()
        self.requests_subject.dispose()
        self.responses_subject.dispose()

    def __init__(self, service_type):
        self.service_type = service_type
        self.events_subject = Subject()
        self.commands_subject = Subject()
        self.requests_subject = Subject()
        self.responses_subject = Subject()
