import rx
from asyncio import gather
from rx.operators import share, merge_all

from obvs.core import typing, DefaultRequestCorrelator


class ServiceBusClient(typing.ServiceBusClient):
    __events: rx.Observable
    _request_correlator: typing.RequestCorrelator

    @property
    def events(self) -> rx.Observable:
        return self.__events

    async def send(self, command):
        endpoints = self.__can_handle(command)
        await gather(*list(map(lambda ep: ep.send(command), endpoints)))

    def get_responses(self, request) -> rx.Observable:
        if self._request_correlator is None:
            raise Exception('Please configure the ServiceBus with a RequestCorrelator using the fluent configuration extension method .CorrelatesRequestWith()')

        self._request_correlator.set_request_correlation_ids(request)

        endpoints = self.__can_handle(request)

        responses = rx.from_iterable(map(lambda ep: ep.get_responses(request), endpoints))

        return responses.pipe(
            merge_all(),
            rx.operators.filter(lambda r: self._request_correlator.are_correlated(request, r)),
            share())

    def dispose(self) -> None:
        for ep in self.__endpoint_clients:
            ep.dispose()

    def __init__(self,
                 endpoint_clients: [typing.ServiceEndpointClient] = None,
                 request_correlator: typing.RequestCorrelator = DefaultRequestCorrelator()):

        if endpoint_clients is None:
            self.__endpoint_clients = []
        else:
            self.__endpoint_clients = endpoint_clients

        self._request_correlator = request_correlator
        self.__events = rx.from_iterable(map(lambda ep: ep.events, self.__endpoint_clients)).pipe(merge_all(), share())

    def __can_handle(self, message) -> [typing.ServiceEndpointClient]:
        return list(filter(lambda ep: ep.can_handle(message), self.__endpoint_clients))
