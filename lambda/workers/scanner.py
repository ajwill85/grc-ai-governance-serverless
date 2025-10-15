"""
Lambda handler for processing scan jobs from SQS
"""
import sys
import os
import json
import boto3
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scanners.s3_scanner import S3Scanner
from scanners.sagemaker_scanner import SageMakerScanner
from scanners.iam_scanner import IAMScanner

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """Process scan jobs from SQS"""
    
    results = []
    
    for record in event['Records']:
        try:
            # Parse message
            message = json.loads(record['body'])
            scan_type = message.get('scan_type', 's3')
            region = message.get('region', 'us-east-1')
            
            print(f"Processing {scan_type} scan for region {region}")
            
            # Run appropriate scanner
            if scan_type == 's3':
                scanner = S3Scanner(region=region)
                scan_results = scanner.scan_all_buckets()
            elif scan_type == 'sagemaker':
                scanner = SageMakerScanner(region=region)
                scan_results = scanner.scan()
            elif scan_type == 'iam':
                scanner = IAMScanner(region=region)
                scan_results = scanner.scan()
            else:
                raise ValueError(f"Unknown scan type: {scan_type}")
            
            # Store results in S3
            bucket_name = os.environ.get('RESULTS_BUCKET')
            timestamp = datetime.now().isoformat()
            key = f"scans/{scan_type}/{timestamp}.json"
            
            s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=json.dumps(scan_results, indent=2),
                ContentType='application/json'
            )
            
            results.append({
                'scan_type': scan_type,
                'status': 'success',
                'results_location': f"s3://{bucket_name}/{key}",
                'findings_count': len(scan_results.get('findings', []))
            })
            
            print(f"Scan complete: {len(scan_results.get('findings', []))} findings")
            
        except Exception as e:
            print(f"Error processing scan: {str(e)}")
            results.append({
                'scan_type': message.get('scan_type', 'unknown'),
                'status': 'error',
                'error': str(e)
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
