import unittest
import aiounittest

from obvs.core import ServiceBus
from tests.fakes import FakeServiceEndpoint, FakeMessageOne, FakeMessageTwo, FakeResponseOne, FakeResponseTwo, \
    FakeRequestOne


class TestServiceBus(aiounittest.AsyncTestCase):
    def test_create_service_bus(self):
        sb = ServiceBus()
        self.assertIsInstance(sb, ServiceBus)

    async def test_publish_events(self):
        ep1 = FakeServiceEndpoint(type(FakeMessageOne()))
        ep2 = FakeServiceEndpoint(type(FakeMessageTwo()))
        sb = ServiceBus([ep1, ep2], [])
        received = []
        ep1.events.subscribe(lambda msg: received.append(msg))
        ep2.events.subscribe(lambda msg: received.append(msg))
        ev1 = FakeMessageOne('event1')
        ev2 = FakeMessageOne('event2')
        await sb.publish(ev1)
        await sb.publish(ev2)
        self.assertIn(ev1, received, 'event1 was not received')
        self.assertIn(ev2, received, 'event2 was not received')
        self.assertEqual(len(received), 2, 'messages received')

    async def test_receive_command(self):
        ep1 = FakeServiceEndpoint(type(FakeMessageOne('')))
        ep2 = FakeServiceEndpoint(type(FakeMessageTwo('')))
        sb = ServiceBus([ep1, ep2])
        received = []
        sb.commands.subscribe(lambda msg: received.append(msg))

        cmd1 = FakeMessageOne('command1')
        cmd2 = FakeMessageOne('command2')
        await ep1.send(cmd1)
        await ep2.send(cmd2)
        self.assertIn(cmd1, received, 'command1 was not received')
        self.assertIn(cmd2, received, 'command2 was not received')
        self.assertEqual(len(received), 2, 'messages received')

    async def test_reply_to_request(self):
        ep1 = FakeServiceEndpoint(type(FakeMessageOne('')))
        ep2 = FakeServiceEndpoint(type(FakeMessageTwo('')))
        sb = ServiceBus([ep1, ep2])

        received = []
        ep1.responses_subject.subscribe(lambda msg: received.append(msg))
        ep2.responses_subject.subscribe(lambda msg: received.append(msg))

        res1 = FakeResponseOne('response1')
        res2 = FakeResponseTwo('response2')
        await sb.reply(FakeRequestOne('request1'), res1)
        await sb.reply(FakeRequestOne('request2'), res2)
        self.assertIn(res1, received, 'response1 was not received')
        self.assertIn(res2, received, 'response2 was not received')
        self.assertEqual(len(received), 2, 'messages received')


if __name__ == '__main__':
    unittest.main()
