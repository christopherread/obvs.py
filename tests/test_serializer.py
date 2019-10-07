import unittest
import aiounittest

from obvs.serialization.json import JsonMessageSerializer, JsonMessageDeserializer
from tests.fakes import FakeMessageOne


class TestJsonMessageSerializer(aiounittest.AsyncTestCase):
    def test_serialize(self):
        msg1 = FakeMessageOne('data1')
        ms = JsonMessageSerializer()
        json_encoded = ms.serialize(msg1)
        print(json_encoded)

        md = JsonMessageDeserializer()
        msg1_decoded = md.deserialize(json_encoded)

        self.assertEqual(msg1.data, msg1_decoded.data)
