import base64
import json

import boto3

from src.data.repository import Repository


def lambda_handler(event, context):
    try:
        if not event.get('async'):
            invoke_self_async(event, context)
            return

        decoded_record_data = [base64.b64decode(
            record['kinesis']['data']) for record in event['Records']]
        deserialized_data = [json.loads(decoded_record)
                             for decoded_record in decoded_record_data]

        repo = Repository()
        repo.save(deserialized_data[0])
    except Exception as e:
        print(e)


def invoke_self_async(event, context):
    event['async'] = True
    called_function = context.invoked_function_arn

    boto3.client('lambda').invoke(
        FunctionName=called_function,
        InvocationType='Event',
        Payload=bytes(json.dumps(event), 'utf-8')
    )
