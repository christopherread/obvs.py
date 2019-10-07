import unittest
import aiounittest

from obvs.core import ServiceBusClient
from tests.fakes import FakeServiceEndpoint, FakeMessageOne, FakeResponseOne, FakeRequestOne


class TestServiceBusClient(aiounittest.AsyncTestCase):
    def test_create_service_bus_client(self):
        sbc = ServiceBusClient()
        self.assertIsInstance(sbc, ServiceBusClient)

    async def test_send_command(self):
        ep1 = FakeServiceEndpoint(type(FakeMessageOne('')))
        sbc = ServiceBusClient([ep1])
        received = []
        ep1.commands_subject.subscribe(lambda msg: received.append(msg))
        cmd = FakeMessageOne('command1')
        await sbc.send(cmd)
        self.assertIn(cmd, received, 'command1 was not received')
        self.assertEqual(len(received), 1, 'messages received')

    async def test_receive_event(self):
        ep1 = FakeServiceEndpoint(type(FakeMessageOne()))
        sbc = ServiceBusClient([ep1])
        received = []
        sbc.events.subscribe(lambda msg: received.append(msg))

        ev = FakeMessageOne('event1')
        ep1.events_subject.on_next(ev)
        self.assertIn(ev, received, 'event1 was not received')
        self.assertEqual(len(received), 1, 'messages received')

    async def test_send_request_receive_response(self):
        ep1 = FakeServiceEndpoint(type(FakeMessageOne()))
        sbc = ServiceBusClient([ep1])
        res = FakeResponseOne('response1')
        req = FakeRequestOne('request1')

        def on_request(r: FakeRequestOne):
            received.append(r)
            res.request_id = r.request_id
            res.requester_id = r.requester_id
            ep1.responses_subject.on_next(res)

        ep1.requests_subject.subscribe(lambda msg: on_request(msg))

        received = []
        sbc.get_responses(req).subscribe(lambda msg: received.append(msg))
        self.assertIn(req, received, 'request1 was not received')
        self.assertIn(res, received, 'response1 was not received')
        self.assertEqual(len(received), 2, 'messages received')


if __name__ == '__main__':
    unittest.main()
