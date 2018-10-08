#!/usr/bin/env python3
# coding=utf-8

import json
import os
import unittest

import boto3

from src.handler import lambda_handler


class KinesisPayloadTests(unittest.TestCase):

    def setUp(self):

        script_dir = os.path.dirname(__file__)

        rel_path = 'data/kinesis/heartbeatEvent.json'
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path) as market:
            self.eventHeartbeat = json.load(market)
            self.assertIsNotNone(self.eventHeartbeat)

    def test_consumer(self):

        lambda_handler(self.eventHeartbeat, None)
        self.assertTrue(True)

    def tearDown(self):
        self.eventHeartbeat = None
        self.assertIsNone(self.eventHeartbeat)


if __name__ == '__main__':
    unittest.main(exit=False)
