import rx
import abc

from rx.core.typing import Disposable


class MessageSource(Disposable, abc.ABC):
    @property
    @abc.abstractmethod
    def messages(self) -> rx.Observable:
        raise NotImplementedError


class MessagePublisher(Disposable, abc.ABC):
    @abc.abstractmethod
    async def publish(self, msg):
        raise NotImplementedError


class MessageConverter(Disposable, abc.ABC):
    @abc.abstractmethod
    def convert(self, msg):
        raise NotImplementedError


class MessageBus(MessageSource, MessagePublisher, abc.ABC):
    @abc.abstractmethod
    async def publish(self, msg):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def messages(self) -> rx.Observable:
        raise NotImplementedError


class ServiceBusClient(Disposable, abc.ABC):

    @property
    @abc.abstractmethod
    def events(self) -> rx.Observable:
        raise NotImplementedError

    @abc.abstractmethod
    async def send(self, command):
        raise NotImplementedError

    @abc.abstractmethod
    def get_responses(self, request) -> rx.Observable:
        raise NotImplementedError


class ServiceBus(ServiceBusClient, abc.ABC):

    @property
    @abc.abstractmethod
    def requests(self) -> rx.Observable:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def commands(self) -> rx.Observable:
        raise NotImplementedError

    @abc.abstractmethod
    async def publish(self, ev):
        raise NotImplementedError

    @abc.abstractmethod
    async def reply(self, request, response):
        raise NotImplementedError


class Endpoint(Disposable, abc.ABC):

    @abc.abstractmethod
    def can_handle(self, message) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError


class ServiceEndpoint(Endpoint, abc.ABC):

    @property
    @abc.abstractmethod
    def requests(self) -> rx.Observable:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def commands(self) -> rx.Observable:
        raise NotImplementedError

    @abc.abstractmethod
    async def publish(self, ev):
        raise NotImplementedError

    @abc.abstractmethod
    async def reply(self, request, response):
        raise NotImplementedError


class ServiceEndpointClient(Endpoint, abc.ABC):

    @property
    @abc.abstractmethod
    def events(self) -> rx.Observable:
        raise NotImplementedError

    @abc.abstractmethod
    async def send(self, command):
        raise NotImplementedError

    @abc.abstractmethod
    def get_responses(self, request) -> rx.Observable:
        raise NotImplementedError


class RequestCorrelator(abc.ABC):

    @abc.abstractmethod
    def set_request_correlation_ids(self, request) -> None:
        raise NotImplementedError

    def set_correlation_ids(self, request, response) -> None:
        raise NotImplementedError

    def are_correlated(self, request, response) -> bool:
        raise NotImplementedError
