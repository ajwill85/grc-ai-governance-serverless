"""
Lambda handler for scheduled scans
Triggered by EventBridge on a schedule
"""
import json
import boto3
from datetime import datetime

sqs = boto3.client('sqs')

def lambda_handler(event, context):
    """Trigger daily governance scans"""
    
    queue_url = os.environ.get('SQS_QUEUE_URL')
    
    # Queue scan jobs
    scan_types = ['s3', 'sagemaker', 'iam']
    regions = ['us-east-1']  # Add more regions as needed
    
    for scan_type in scan_types:
        for region in regions:
            message = {
                'scan_type': scan_type,
                'region': region,
                'scheduled': True,
                'timestamp': datetime.now().isoformat()
            }
            
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message)
            )
            
            print(f"Queued {scan_type} scan for {region}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Scans queued successfully',
            'scans_queued': len(scan_types) * len(regions)
        })
    }
