import rx
from rx.core.typing import Disposable

from obvs.core import typing


class ServiceEndpoint(typing.ServiceEndpoint, Disposable):
    def __init__(self,
                 request_source: typing.MessageSource,
                 command_source: typing.MessageSource,
                 event_publisher: typing.MessagePublisher,
                 response_publisher: typing.MessagePublisher,
                 service_type: type,
                 service_name: str):
        self.request_source = request_source
        self.command_source = command_source
        self.event_publisher = event_publisher
        self.response_publisher = response_publisher
        self.service_type = service_type
        self.service_name = service_name

    def dispose(self) -> None:
        self.request_source.dispose()
        self.command_source.dispose()
        self.event_publisher.dispose()
        self.response_publisher.dispose()

    def can_handle(self, message) -> bool:
        return isinstance(message, self.service_type)

    @property
    def name(self) -> str:
        return self.service_name

    @property
    def requests(self) -> rx.Observable:
        return self.request_source.messages

    @property
    def commands(self) -> rx.Observable:
        return self.command_source.messages

    async def publish(self, ev):
        return self.event_publisher.publish(ev)

    async def reply(self, request, response):
        return self.response_publisher.publish(response)