#!/usr/bin/env python3
# coding=utf-8

import json
import os
import sys
import unittest

from src.utils.payloadHelper import PayloadHelper


class MappedPayloadTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_hartbeat(self):
        script_dir = os.path.dirname(__file__)
        rel_path = 'data/source/heartbeatPayload.json'
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path) as hartbeatData:
            self.hartbeatJson = json.load(hartbeatData)
            self.helper = PayloadHelper()

        for item in self.hartbeatJson:
            payload = self.helper.map(item)
            self.assertIsNotNone(payload.heartbeat)

    def tearDown(self):
        self.helper = None
        self.assertIsNone(self.helper)
        pass


if __name__ == '__main__':
    unittest.main(exit=False)
