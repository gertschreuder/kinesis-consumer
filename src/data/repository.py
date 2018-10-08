import datetime
import time
from multiprocessing import Process

import boto3
from botocore.exceptions import ClientError

from src.data.dbItemWrapper import Wrapper
from src.data.queue import Queue
from src.mappers.heartbeatMapper import Heartbeat
from src.utils.config import Config
from src.utils.payloadHelper import PayloadHelper


class Repository(object):
    def __init__(self):
        self.inserted = False
        self.cfg = Config()
        self.dynamo_db = boto3.client('dynamodb', region_name=self.cfg.AWSRegion,
                                      endpoint_url=self.cfg.DynamoDbEndPoint)
        helper = PayloadHelper()
        self.options = {
            "Status": {
                "mapper": helper.resolveStatus,
                "table": self.cfg.HeartbeatTable,
                "existsCheck": True,
                "checkFunc": self.heartbeatCheck,
                "getKey": self.getHeartbeatKey
            }
        }

    def save(self, deserialized_data):
        batch = Wrapper()
        for item in deserialized_data:
            for key in self.options:
                if key in item:
                    mappedItem = self.options[key]["mapper"](item)
                    if mappedItem is not None:
                        insert = True
                        dbJson = self.toDynamoDbJson(mappedItem)

                        if self.options[key]["existsCheck"]:
                            insert = self.options[key]["checkFunc"](
                                key, mappedItem)

                        if insert:
                            batch.load(self.options[key]["table"], dbJson)

        self.saveItems(batch)

    def saveItems(self, batch):
        processes = []
        for tableName in batch.__dict__:
            result = None
            max = 25
            start = 0
            end = max
            if len(batch.__dict__[tableName]) < max:
                end = len(batch.__dict__[tableName])
            proceed = False
            index = 1
            while True:
                if not proceed and len(batch.__dict__[tableName]) % 25 > 0 and len(batch.__dict__[tableName]) <= end:
                    end = len(batch.__dict__[tableName])
                    self.submitBatch(
                        {tableName: batch.__dict__[tableName][start:end]})
                    break
                else:
                    self.submitBatch(
                        {tableName: batch.__dict__[tableName][start:end]})

                start = end
                index = index + 1
                end = max * index
                proceed = len(batch.__dict__[tableName]) > end

    def submitBatch(self, requestItems, retryCount=0):
        RETRY_EXCEPTIONS = (
            'ProvisionedThroughputExceededException', 'ThrottlingException')
        maxRetryCount = 10
        addToRetryQueue = False
        queue = Queue()
        processData = requestItems
        try:
            result = self.dynamo_db.batch_write_item(RequestItems=processData)
            if "UnprocessedItems" in result and len(result["UnprocessedItems"]) > 0 and retryCount > 0:
                retryCount = retryCount + 1
                if retryCount == maxRetryCount and "UnprocessedItems" in result and len(result["UnprocessedItems"]) > 0:
                    processData = result["UnprocessedItems"]
                    queue.put(processData)
                else:
                    time.sleep(1)
                    processData = result["UnprocessedItems"]
                    self.submitBatch(processData, retryCount)

        except ClientError as err:
            if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                queue.put(processData)
                raise
            retryCount = retryCount + 1
            time.sleep(1)
            self.submitBatch(processData, retryCount)

    def getItem(self, key, tableName):
        try:
            item = None
            response = self.dynamo_db.get_item(TableName=tableName, Key=key)
            if response is not None and 'Item' in response:
                item = response["Item"]
            return item
        except Exception:
            return None

    def toDynamoDbJson(self, data):
        if data is None:
            return data
        if hasattr(data, "__dict__"):
            data = data.__dict__
        item = {}
        for k, v in data.items():
            if v is None:
                item[k] = {"NULL": True}
            elif isinstance(v, str):
                if v is '':
                    item[k] = {"NULL": True}
                else:
                    item[k] = {"S": v}
            elif type(v) in (float, int, complex):
                item[k] = {"N": str(v)}
            elif isinstance(v, bool):
                item[k] = {"BOOL": v}
            elif isinstance(v, bytes):
                item[k] = {"B": v}
            elif isinstance(v, list):
                lys = []
                [lys.append({"M": self.toDynamoDbJson(i)}) for i in v]
                item[k] = {"L": lys}
            else:
                item[k] = {"M": self.toDynamoDbJson(v)}

        return item

    def heartbeatCheck(self, key, mappedItem: Heartbeat):
        tableKey = self.options[key]["getKey"](mappedItem)
        item = self.getItem(tableKey, self.options[key]["table"])
        return not (item is not None and mappedItem.status != item["status"])

    def getHeartbeatKey(self, heartbeat: Heartbeat):
        return {'id': {'S': heartbeat.id}, 'providerId': {'S': heartbeat.providerId}}
