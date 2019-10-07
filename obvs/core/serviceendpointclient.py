import rx
from rx.core.typing import Disposable

from obvs.core import typing


class ServiceEndpointClient(typing.ServiceEndpointClient, Disposable):
    def __init__(self,
                 event_source: typing.MessageSource,
                 response_source: typing.MessageSource,
                 request_publisher: typing.MessagePublisher,
                 command_publisher: typing.MessagePublisher,
                 service_type: type,
                 service_name: str):
        self.event_source = event_source
        self.response_source = response_source
        self.request_publisher = request_publisher
        self.command_publisher = command_publisher
        self.service_type = service_type
        self.service_name = service_name

    def dispose(self) -> None:
        self.event_source.dispose()
        self.response_source.dispose()
        self.request_publisher.dispose()
        self.command_publisher.dispose()

    def can_handle(self, message) -> bool:
        return isinstance(message, self.service_type)

    @property
    def name(self) -> str:
        return self.service_name

    @property
    def events(self) -> rx.Observable:
        return self.event_source.messages

    @property
    def responses(self) -> rx.Observable:
        return self.response_source.messages

    async def send(self, ev):
        return self.command_publisher.publish(ev)

    async def get_responses(self, request) -> rx.Observable:
        def subscribe(o, s) -> rx.typing.Disposable:
            disposable = self.response_source.messages.subscribe(o, s)
            self.request_publisher.publish(request)
            return disposable
        return rx.create(subscribe)
