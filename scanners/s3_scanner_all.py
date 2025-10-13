"""
S3 Data Governance Scanner - All Buckets Version
Scans ALL S3 buckets for data classification and governance violations
ISO 27001 A.5.12, A.5.34, ISO 27701 6.4.1-6.4.4, ISO 42001 6.2.1-6.2.4
"""

import boto3
import json
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class S3Finding:
    """S3 security finding"""
    bucket_name: str
    severity: str
    issue: str
    control: str
    remediation: str
    timestamp: str
    region: str


class S3ScannerAll:
    """Scanner for ALL S3 buckets (not just SageMaker-related)"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.s3 = boto3.client('s3', region_name=region)
        self.findings: List[S3Finding] = []
    
    def scan_all(self) -> List[S3Finding]:
        """Scan all S3 buckets"""
        print("[*] Starting S3 bucket scan (ALL buckets)...")
        
        buckets = self._get_all_buckets()
        print(f"[*] Found {len(buckets)} total buckets")
        
        for bucket in buckets:
            self._check_bucket(bucket)
        
        print(f"[+] Scan complete. Found {len(self.findings)} violations.")
        return self.findings
    
    def _get_all_buckets(self) -> List[str]:
        """Get ALL S3 buckets"""
        buckets = []
        try:
            response = self.s3.list_buckets()
            for bucket in response['Buckets']:
                buckets.append(bucket['Name'])
        except Exception as e:
            print(f"[!] Error listing buckets: {e}")
        return buckets
    
    def _check_bucket(self, bucket_name: str) -> None:
        """Check individual bucket for violations"""
        try:
            # Get bucket location
            location = self.s3.get_bucket_location(Bucket=bucket_name)
            bucket_region = location['LocationConstraint'] or 'us-east-1'
            
            # Check tags
            self._check_classification_tags(bucket_name, bucket_region)
            
            # Check encryption
            self._check_encryption(bucket_name, bucket_region)
            
            # Check versioning
            self._check_versioning(bucket_name, bucket_region)
            
            # Check lifecycle policies
            self._check_lifecycle(bucket_name, bucket_region)
            
            # Check public access
            self._check_public_access(bucket_name, bucket_region)
            
        except Exception as e:
            print(f"[!] Error checking bucket {bucket_name}: {e}")
    
    def _check_classification_tags(self, bucket_name: str, region: str) -> None:
        """Check for data classification tags"""
        try:
            response = self.s3.get_bucket_tagging(Bucket=bucket_name)
            tags = {tag['Key']: tag['Value'] for tag in response.get('TagSet', [])}
            
            if 'DataClassification' not in tags:
                self.findings.append(S3Finding(
                    bucket_name=bucket_name,
                    severity='HIGH',
                    issue='Missing DataClassification tag',
                    control='ISO 27001 A.5.12, ISO 27701 6.4.1',
                    remediation='Add DataClassification tag (PUBLIC, INTERNAL, SENSITIVE, PII, CONFIDENTIAL)',
                    timestamp=datetime.utcnow().isoformat(),
                    region=region
                ))
            
            required_tags = {'Owner', 'Purpose'}
            missing_tags = required_tags - set(tags.keys())
            if missing_tags:
                self.findings.append(S3Finding(
                    bucket_name=bucket_name,
                    severity='LOW',
                    issue=f'Missing required tags: {", ".join(missing_tags)}',
                    control='ISO 27001 A.5.12',
                    remediation='Add missing tags',
                    timestamp=datetime.utcnow().isoformat(),
                    region=region
                ))
        except Exception as e:
            # Handle NoSuchTagSet or any tagging errors
            if 'NoSuchTagSet' in str(e) or 'TagSet' in str(e):
                self.findings.append(S3Finding(
                    bucket_name=bucket_name,
                    severity='HIGH',
                    issue='No tags configured',
                    control='ISO 27001 A.5.12, ISO 27701 6.4.1',
                    remediation='Add required tags including DataClassification',
                    timestamp=datetime.utcnow().isoformat(),
                    region=region
                ))
            else:
                print(f"[!] Error checking tags for {bucket_name}: {e}")
    
    def _check_encryption(self, bucket_name: str, region: str) -> None:
        """Check bucket encryption"""
        try:
            self.s3.get_bucket_encryption(Bucket=bucket_name)
        except Exception as e:
            # Handle ServerSideEncryptionConfigurationNotFoundError
            if 'ServerSideEncryptionConfigurationNotFoundError' in str(type(e)) or 'EncryptionConfiguration' in str(e):
                self.findings.append(S3Finding(
                    bucket_name=bucket_name,
                    severity='CRITICAL',
                    issue='Bucket encryption not enabled',
                    control='ISO 27001 A.8.24, ISO 27701 6.6.1',
                    remediation='Enable default encryption with AWS KMS',
                    timestamp=datetime.utcnow().isoformat(),
                    region=region
                ))
            else:
                print(f"[!] Error checking encryption for {bucket_name}: {e}")
    
    def _check_versioning(self, bucket_name: str, region: str) -> None:
        """Check bucket versioning"""
        try:
            response = self.s3.get_bucket_versioning(Bucket=bucket_name)
            if response.get('Status') != 'Enabled':
                self.findings.append(S3Finding(
                    bucket_name=bucket_name,
                    severity='MEDIUM',
                    issue='Versioning not enabled',
                    control='ISO 27701 6.4.3',
                    remediation='Enable versioning for data protection and audit trail',
                    timestamp=datetime.utcnow().isoformat(),
                    region=region
                ))
        except Exception as e:
            print(f"[!] Error checking versioning for {bucket_name}: {e}")
    
    def _check_lifecycle(self, bucket_name: str, region: str) -> None:
        """Check lifecycle policies"""
        try:
            self.s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        except Exception as e:
            # Handle NoSuchLifecycleConfiguration
            if 'NoSuchLifecycleConfiguration' in str(type(e)) or 'LifecycleConfiguration' in str(e):
                self.findings.append(S3Finding(
                    bucket_name=bucket_name,
                    severity='MEDIUM',
                    issue='No lifecycle policy configured',
                    control='ISO 27001 A.5.34, ISO 27701 6.4.3',
                    remediation='Configure lifecycle policy for data retention',
                    timestamp=datetime.utcnow().isoformat(),
                    region=region
                ))
            else:
                print(f"[!] Error checking lifecycle for {bucket_name}: {e}")
    
    def _check_public_access(self, bucket_name: str, region: str) -> None:
        """Check public access settings"""
        try:
            response = self.s3.get_public_access_block(Bucket=bucket_name)
            config = response['PublicAccessBlockConfiguration']
            
            if not all([
                config.get('BlockPublicAcls', False),
                config.get('IgnorePublicAcls', False),
                config.get('BlockPublicPolicy', False),
                config.get('RestrictPublicBuckets', False)
            ]):
                self.findings.append(S3Finding(
                    bucket_name=bucket_name,
                    severity='CRITICAL',
                    issue='Public access not fully blocked',
                    control='ISO 27701 6.6.1, ISO 42001 6.3.2',
                    remediation='Enable all public access block settings',
                    timestamp=datetime.utcnow().isoformat(),
                    region=region
                ))
        except Exception as e:
            # Handle NoSuchPublicAccessBlockConfiguration
            if 'NoSuchPublicAccessBlockConfiguration' in str(type(e)) or 'PublicAccessBlock' in str(e):
                self.findings.append(S3Finding(
                    bucket_name=bucket_name,
                    severity='CRITICAL',
                    issue='No public access block configured',
                    control='ISO 27701 6.6.1',
                    remediation='Configure public access block',
                    timestamp=datetime.utcnow().isoformat(),
                    region=region
                ))
            else:
                print(f"[!] Error checking public access for {bucket_name}: {e}")
    
    def export_findings(self, output_file: str = 's3_all_findings.json') -> None:
        """Export findings to JSON"""
        findings_dict = [asdict(f) for f in self.findings]
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_timestamp': datetime.utcnow().isoformat(),
                'total_findings': len(self.findings),
                'severity_breakdown': self._get_severity_breakdown(),
                'findings': findings_dict
            }, f, indent=2)
        
        print(f"[+] Findings exported to {output_file}")
    
    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get severity breakdown"""
        breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in self.findings:
            breakdown[finding.severity] += 1
        return breakdown
    
    def print_summary(self) -> None:
        """Print summary"""
        breakdown = self._get_severity_breakdown()
        
        print("\n" + "="*60)
        print("S3 BUCKET SCAN SUMMARY (ALL BUCKETS)")
        print("="*60)
        print(f"Total Findings: {len(self.findings)}")
        print(f"\nSeverity Breakdown:")
        print(f"  CRITICAL: {breakdown['CRITICAL']}")
        print(f"  HIGH:     {breakdown['HIGH']}")
        print(f"  MEDIUM:   {breakdown['MEDIUM']}")
        print(f"  LOW:      {breakdown['LOW']}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan ALL S3 buckets for governance violations')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--output', default='s3_all_findings.json', help='Output file')
    
    args = parser.parse_args()
    
    scanner = S3ScannerAll(region=args.region)
    scanner.scan_all()
    scanner.print_summary()
    scanner.export_findings(args.output)


if __name__ == '__main__':
    main()
