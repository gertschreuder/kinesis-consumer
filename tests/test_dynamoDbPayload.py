#!/usr/bin/env python3
# coding=utf-8

import json
import os
import unittest

from src.data.repository import Repository
from src.utils.payloadHelper import PayloadHelper


class DynamoDbPayloadTests(unittest.TestCase):

    def setUp(self):
        self.repo = Repository()

        # heartbeat
        script_dir = os.path.dirname(__file__)
        rel_path = 'data/source/heartbeatPayload.json'
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path) as hartbeatData:
            hartbeatJson = json.load(hartbeatData)
            self.helper = PayloadHelper()

        self.heartbeatPayload = self.helper.map(hartbeatJson[0])

    def test_hartbeat(self):
        self.assertIsNotNone(self.heartbeatPayload)
        self.assertIsNotNone(self.heartbeatPayload.heartbeat)

        payload = self.repo.toDynamoDbJson(
            self.heartbeatPayload.heartbeat)

        self.assertIsNotNone(payload)
        self.assertEqual(payload["id"]["N"],
                         str(self.heartbeatPayload.heartbeat.id))

    def tearDown(self):
        self.heartbeatPayload = None
        self.assertIsNone(self.heartbeatPayload)
        self.repo = None
        self.assertIsNone(self.repo)
        pass


if __name__ == '__main__':
    unittest.main(exit=False)
