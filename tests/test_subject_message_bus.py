import unittest
import aiounittest

from obvs.core import SubjectMessageBus


class TestSubjectMessageBus(aiounittest.AsyncTestCase):
    def test_can_create_subject_message_bus(self):
        mb = SubjectMessageBus()
        self.assertIsInstance(mb, SubjectMessageBus)

    async def test_can_publish_and_receive_message(self):
        mb = SubjectMessageBus()
        received = []
        mb.messages.subscribe(lambda msg: received.append(msg))
        await mb.publish('some message')
        self.assertIn('some message', received, 'message was not received')
        self.assertEqual(len(received), 1, 'messages received')


if __name__ == '__main__':
    unittest.main()
