import unittest
import aiounittest

from obvs.core import SubjectMessageBus, ServiceBusClient, DefaultRequestCorrelator
from tests.fakes import FakeServiceEndpoint, FakeMessageOne


class TestSubjectMessageBus(aiounittest.AsyncTestCase):
    def test_can_create_subject_message_bus(self):
        mb = SubjectMessageBus()
        self.assertIsInstance(mb, SubjectMessageBus)

    async def test_can_publish_and_receive_message(self):
        mb = SubjectMessageBus()
        received = []
        mb.messages.subscribe(lambda msg: received.append(msg))
        await mb.publish('some message')
        self.assertIn('some message', received, 'Message was not received')


class TestServiceBusClient(aiounittest.AsyncTestCase):
    def test_can_create_service_bus_client(self):
        sb = ServiceBusClient(
            [FakeServiceEndpoint(type(FakeMessageOne))],
            DefaultRequestCorrelator()
        )
        self.assertIsInstance(sb, ServiceBusClient)

    async def test_can_send_command(self):
        fake_endpoint_1 = FakeServiceEndpoint(type(FakeMessageOne('')))
        sb = ServiceBusClient(
            [fake_endpoint_1],
            DefaultRequestCorrelator()
        )
        received = []
        fake_endpoint_1.commands_subject.subscribe(lambda msg: received.append(msg))
        cmd = FakeMessageOne('command1')
        await sb.send(cmd)
        self.assertIn(cmd, received, 'Command was not received')


if __name__ == '__main__':
    unittest.main()
