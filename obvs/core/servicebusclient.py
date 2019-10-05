import rx
from asyncio import gather
from rx.operators import share, merge_all

from obvs.core import typing


class ServiceBusClient(typing.ServiceBusClient):
    __events: rx.Observable

    @property
    def events(self) -> rx.Observable:
        return self.__events

    async def send(self, command):
        endpoints = self.__endpoints_that_can_handle(command)
        await gather(*list(map(lambda ep: ep.send(command), endpoints)))

    def get_responses(self, request) -> rx.Observable:
        if self.request_correlator is None:
            raise Exception('Please configure the ServiceBus with a RequestCorrelator using the fluent configuration extension method .CorrelatesRequestWith()')

        self.request_correlator.set_request_correlation_ids(request)

        endpoints = self.__endpoints_that_can_handle(request)
        all_responses = rx.from_iterable(map(lambda ep: ep.get_responses(request), endpoints))

        return all_responses.pipe(
            merge_all(),
            rx.operators.filter(lambda r: self.request_correlator.are_correlated(request, r)),
            share())

    def dispose(self) -> None:
        for ep in self.endpoint_clients:
            ep.dispose()

    def __init__(self,
                 endpoint_clients: [typing.ServiceEndpointClient],
                 request_correlator: typing.RequestCorrelator):
        self.request_correlator = request_correlator
        self.endpoint_clients = endpoint_clients

        all_events = rx.from_iterable(map(lambda ep: ep.events, self.endpoint_clients))

        self.__events = all_events.pipe(merge_all(), share())

    def __endpoints_that_can_handle(self, message) -> [typing.ServiceEndpointClient]:
        return list(filter(lambda ep: ep.can_handle(message), self.endpoint_clients))
