import abc


class MessageSerializer(abc.ABC):
    @abc.abstractmethod
    def serialize(self, message) -> object:
        raise NotImplementedError


class MessageDeserializer(abc.ABC):
    @abc.abstractmethod
    def deserialize(self, data) -> object:
        raise NotImplementedError
