import unittest
import aiounittest
import rx
import asyncio

from rx.scheduler import ThreadPoolScheduler

from obvs.core import SubjectMessageBus, ServiceBusClient, DefaultRequestCorrelator
from tests.fakes import FakeServiceEndpoint, FakeMessageOne, FakeResponseOne, FakeRequestOne


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
    def test_create_service_bus_client(self):
        sb = ServiceBusClient(
            [FakeServiceEndpoint(type(FakeMessageOne))],
            DefaultRequestCorrelator()
        )
        self.assertIsInstance(sb, ServiceBusClient)

    async def test_send_command(self):
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

    async def test_receive_event(self):
        fake_endpoint_1 = FakeServiceEndpoint(type(FakeMessageOne('')))
        sb = ServiceBusClient(
            [fake_endpoint_1],
            DefaultRequestCorrelator()
        )
        received = []
        sb.events.subscribe(lambda msg: received.append(msg))

        ev = FakeMessageOne('event1')
        fake_endpoint_1.events_subject.on_next(ev)
        self.assertIn(ev, received, 'Event was not received')

    async def test_send_request_receive_response(self):
        ep = FakeServiceEndpoint(type(FakeMessageOne('')))
        rc = DefaultRequestCorrelator()
        sb = ServiceBusClient([ep], rc)
        res = FakeResponseOne('response1')
        req = FakeRequestOne('request1')

        def on_request(r: FakeRequestOne):
            received.append(r)
            res.request_id = r.request_id
            res.requester_id = r.requester_id
            ep.responses_subject.on_next(res)

        ep.requests_subject.subscribe(lambda msg: on_request(msg))

        received = []
        sb.get_responses(req).subscribe(lambda msg: received.append(msg))
        self.assertIn(req, received, 'Request was not received')
        self.assertIn(res, received, 'Response was not received')


if __name__ == '__main__':
    unittest.main()
