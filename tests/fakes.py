import abc
import rx
from rx.subject import Subject

from obvs.core.typing import ServiceEndpoint, ServiceEndpointClient


class FakeMessageOne:
    @property
    def data(self) -> str:
        return self._data

    def __init__(self, data: str = ''):
        self._data = data


class FakeCommandOne(FakeMessageOne):
    def __init__(self, data: str):
        super().__init__(data)


class FakeRequestOne(FakeMessageOne):
    request_id: str = ''
    requester_id: str = ''

    def __init__(self, data: str):
        super().__init__(data)


class FakeResponseOne(FakeMessageOne):
    request_id: str = ''
    requester_id: str = ''

    def __init__(self, data: str):
        super().__init__(data)


class FakeMessageTwo(abc.ABC):
    @property
    def data(self) -> str:
        return self._data

    def __init__(self, data: str = ''):
        self._data = data


class FakeCommandTwo(FakeMessageTwo):
    def __init__(self, data: str):
        super().__init__(data)


class FakeRequestTwo(FakeMessageTwo):
    request_id: str = ''
    requester_id: str = ''

    def __init__(self, data: str):
        super().__init__(data)


class FakeResponseTwo(FakeMessageTwo):
    request_id: str = ''
    requester_id: str = ''

    def __init__(self, data: str):
        super().__init__(data)


class FakeServiceEndpoint(ServiceEndpoint, ServiceEndpointClient):
    @property
    def events(self) -> rx.Observable:
        return self.events_subject

    async def send(self, command):
        print(self.name, 'send', command.data)
        self.commands_subject.on_next(command)

    def get_responses(self, request) -> rx.Observable:
        print(self.name, 'get_responses', request.data)

        def subscribe(o, s) -> rx.typing.Disposable:
            print(self.name, 'get_responses subscribe', request.data)
            disposable = self.responses_subject.subscribe(o, s)
            self.requests_subject.on_next(request)
            return disposable

        return rx.create(subscribe)

    @property
    def requests(self) -> rx.Observable:
        return self.requests_subject

    @property
    def commands(self) -> rx.Observable:
        return self.commands_subject

    async def publish(self, ev):
        print(self.name, 'publish', ev.data)
        self.events_subject.on_next(ev)

    async def reply(self, request, response):
        print(self.name, 'reply', request.data, response.data)
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
