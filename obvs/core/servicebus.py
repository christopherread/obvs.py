import rx
from asyncio import gather
from rx.operators import share, merge_all

from obvs.core import typing, ServiceBusClient, DefaultRequestCorrelator


class ServiceBus(ServiceBusClient, typing.ServiceBus):
    __requests: rx.Observable
    __commands: rx.Observable
    __endpoints: [typing.ServiceEndpoint]

    def __init__(self,
                 endpoints: [typing.ServiceEndpoint] = None,
                 endpoint_clients: [typing.ServiceEndpointClient] = None,
                 request_correlator: typing.RequestCorrelator = DefaultRequestCorrelator()):

        super().__init__(endpoint_clients, request_correlator)

        if endpoints is None:
            self.__endpoints = []
        else:
            self.__endpoints = endpoints

        self.__requests = rx.from_iterable(map(lambda ep: ep.requests, self.__endpoints)).pipe(merge_all(), share())
        self.__commands = rx.from_iterable(map(lambda ep: ep.commands, self.__endpoints)).pipe(merge_all(), share())

    @property
    def requests(self) -> rx.Observable:
        return self.__requests

    @property
    def commands(self) -> rx.Observable:
        return self.__commands

    async def publish(self, ev):
        endpoints = self.__can_handle(ev)
        await gather(*list(map(lambda ep: ep.publish(ev), endpoints)))

    async def reply(self, request, response):
        endpoints = self.__can_handle(response)
        self._request_correlator.set_correlation_ids(request, response)
        await gather(*list(map(lambda ep: ep.reply(request, response), endpoints)))

    def dispose(self) -> None:
        super().dispose()
        for ep in self.__endpoints:
            ep.dispose()

    def __can_handle(self, message) -> [typing.ServiceEndpoint]:
        return list(filter(lambda ep: ep.can_handle(message), self.__endpoints))

    @staticmethod
    def configure():
        return Configurator()


class Configurator:
    __endpoints: [typing.ServiceEndpoint]
    __endpoint_clients: [typing.ServiceEndpointClient]
    __request_correlator: typing.RequestCorrelator

    def __init__(self):
        self.__endpoints = []
        self.__endpoint_clients = []
        self.__request_correlator = None

    def with_endpoint(self, endpoint: typing.ServiceEndpoint):
        self.__endpoints.append(endpoint)
        return self

    def with_endpoint_client(self, endpoint: typing.ServiceEndpointClient):
        self.__endpoint_clients.append(endpoint)
        return self

    def correlate_requests_with(self, correlator: typing.RequestCorrelator):
        self.__request_correlator = correlator
        return self

    def create(self):
        return ServiceBus(self.__endpoints, self.__endpoint_clients, self.__request_correlator)

    def create_client(self):
        return ServiceBusClient(self.__endpoint_clients, self.__request_correlator)
