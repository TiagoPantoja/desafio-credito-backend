import boto3
import json
from app.core.config import settings

def get_sqs_client():
    return boto3.client(
        "sqs",
        endpoint_url="http://localhost:4566",
        region_name=settings.AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

def send_to_queue(message_body: dict):
    client = get_sqs_client()
    return client.send_message(
        QueueUrl=settings.SQS_QUEUE_URL,
        MessageBody=json.dumps(message_body)
    )