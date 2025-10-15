"""
SageMaker Security Scanner
Scans AWS SageMaker resources for security and compliance violations
ISO 27001, ISO 27701, ISO 42001 controls
"""

import boto3
import json
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class SecurityFinding:
    """Represents a security finding from the scan"""
    resource_type: str
    resource_name: str
    resource_arn: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    issue: str
    control: str
    remediation: str
    timestamp: str
    region: str


class SageMakerScanner:
    """Scanner for SageMaker resources"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.sagemaker = boto3.client('sagemaker', region_name=region)
        self.findings: List[SecurityFinding] = []
    
    def scan_all(self) -> List[SecurityFinding]:
        """Run all scans and return findings"""
        print(f"[*] Starting SageMaker security scan in {self.region}")
        
        self.scan_notebooks()
        self.scan_training_jobs()
        self.scan_models()
        self.scan_endpoints()
        
        print(f"[+] Scan complete. Found {len(self.findings)} violations.")
        return self.findings
    
    def scan_notebooks(self) -> None:
        """Scan SageMaker notebook instances"""
        print("[*] Scanning notebook instances...")
        
        try:
            paginator = self.sagemaker.get_paginator('list_notebook_instances')
            for page in paginator.paginate():
                for notebook in page['NotebookInstances']:
                    self._check_notebook(notebook['NotebookInstanceName'])
        except Exception as e:
            print(f"[!] Error scanning notebooks: {e}")
    
    def _check_notebook(self, notebook_name: str) -> None:
        """Check individual notebook for violations"""
        try:
            response = self.sagemaker.describe_notebook_instance(
                NotebookInstanceName=notebook_name
            )
            
            # Check encryption
            if not response.get('KmsKeyId'):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::NotebookInstance',
                    resource_name=notebook_name,
                    resource_arn=response['NotebookInstanceArn'],
                    severity='HIGH',
                    issue='Notebook instance does not have KMS encryption enabled',
                    control='ISO 27001 A.8.24, ISO 27701 6.6.1',
                    remediation='Enable KMS encryption for the notebook instance',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
            
            # Check root access
            if response.get('RootAccess') == 'Enabled':
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::NotebookInstance',
                    resource_name=notebook_name,
                    resource_arn=response['NotebookInstanceArn'],
                    severity='MEDIUM',
                    issue='Root access is enabled on notebook instance',
                    control='ISO 27001 A.5.18',
                    remediation='Disable root access on the notebook instance',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
            
            # Check direct internet access
            if response.get('DirectInternetAccess') == 'Enabled' and not response.get('SubnetId'):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::NotebookInstance',
                    resource_name=notebook_name,
                    resource_arn=response['NotebookInstanceArn'],
                    severity='HIGH',
                    issue='Notebook has direct internet access without VPC',
                    control='ISO 27001 A.8.20, ISO 42001 6.3.2',
                    remediation='Deploy notebook in VPC or disable direct internet access',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
            
            # Check tags
            if not self._has_required_tags(response.get('Tags', [])):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::NotebookInstance',
                    resource_name=notebook_name,
                    resource_arn=response['NotebookInstanceArn'],
                    severity='LOW',
                    issue='Missing required tags (DataClassification, Owner, Purpose)',
                    control='ISO 27001 A.5.12',
                    remediation='Add required tags to the notebook instance',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
                
        except Exception as e:
            print(f"[!] Error checking notebook {notebook_name}: {e}")
    
    def scan_training_jobs(self) -> None:
        """Scan SageMaker training jobs"""
        print("[*] Scanning training jobs...")
        
        try:
            paginator = self.sagemaker.get_paginator('list_training_jobs')
            for page in paginator.paginate(MaxResults=100):
                for job in page['TrainingJobSummaries']:
                    self._check_training_job(job['TrainingJobName'])
        except Exception as e:
            print(f"[!] Error scanning training jobs: {e}")
    
    def _check_training_job(self, job_name: str) -> None:
        """Check individual training job for violations"""
        try:
            response = self.sagemaker.describe_training_job(
                TrainingJobName=job_name
            )
            
            # Check output encryption
            if not response.get('OutputDataConfig', {}).get('KmsKeyId'):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::TrainingJob',
                    resource_name=job_name,
                    resource_arn=response['TrainingJobArn'],
                    severity='HIGH',
                    issue='Training job output is not encrypted',
                    control='ISO 27001 A.8.24, ISO 42001 6.3.1',
                    remediation='Enable KMS encryption for training job output',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
            
            # Check volume encryption
            if not response.get('ResourceConfig', {}).get('VolumeKmsKeyId'):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::TrainingJob',
                    resource_name=job_name,
                    resource_arn=response['TrainingJobArn'],
                    severity='HIGH',
                    issue='Training job volumes are not encrypted',
                    control='ISO 27001 A.8.24',
                    remediation='Enable KMS encryption for training volumes',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
            
            # Check inter-container encryption
            if not response.get('EnableInterContainerTrafficEncryption', False):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::TrainingJob',
                    resource_name=job_name,
                    resource_arn=response['TrainingJobArn'],
                    severity='MEDIUM',
                    issue='Inter-container traffic encryption is not enabled',
                    control='ISO 27001 A.8.24',
                    remediation='Enable inter-container traffic encryption',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
            
            # Check network isolation
            if not response.get('EnableNetworkIsolation', False):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::TrainingJob',
                    resource_name=job_name,
                    resource_arn=response['TrainingJobArn'],
                    severity='MEDIUM',
                    issue='Network isolation is not enabled',
                    control='ISO 27701 6.6.2',
                    remediation='Enable network isolation for training jobs',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
                
        except Exception as e:
            print(f"[!] Error checking training job {job_name}: {e}")
    
    def scan_models(self) -> None:
        """Scan SageMaker models"""
        print("[*] Scanning models...")
        
        try:
            paginator = self.sagemaker.get_paginator('list_models')
            for page in paginator.paginate():
                for model in page['Models']:
                    self._check_model(model['ModelName'])
        except Exception as e:
            print(f"[!] Error scanning models: {e}")
    
    def _check_model(self, model_name: str) -> None:
        """Check individual model for violations"""
        try:
            response = self.sagemaker.describe_model(ModelName=model_name)
            
            # Check VPC configuration for sensitive models
            if not response.get('VpcConfig'):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::Model',
                    resource_name=model_name,
                    resource_arn=response['ModelArn'],
                    severity='MEDIUM',
                    issue='Model does not have VPC configuration',
                    control='ISO 27701 6.6.2, ISO 42001 6.3.2',
                    remediation='Configure VPC for model deployment',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
            
            # Check tags
            if not self._has_required_tags(response.get('Tags', [])):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::Model',
                    resource_name=model_name,
                    resource_arn=response['ModelArn'],
                    severity='LOW',
                    issue='Missing required tags',
                    control='ISO 27001 A.5.12',
                    remediation='Add required tags to the model',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
                
        except Exception as e:
            print(f"[!] Error checking model {model_name}: {e}")
    
    def scan_endpoints(self) -> None:
        """Scan SageMaker endpoints"""
        print("[*] Scanning endpoints...")
        
        try:
            paginator = self.sagemaker.get_paginator('list_endpoints')
            for page in paginator.paginate():
                for endpoint in page['Endpoints']:
                    self._check_endpoint(endpoint['EndpointName'])
        except Exception as e:
            print(f"[!] Error scanning endpoints: {e}")
    
    def _check_endpoint(self, endpoint_name: str) -> None:
        """Check individual endpoint for violations"""
        try:
            response = self.sagemaker.describe_endpoint(
                EndpointName=endpoint_name
            )
            
            # Get endpoint config
            config_name = response['EndpointConfigName']
            config = self.sagemaker.describe_endpoint_config(
                EndpointConfigName=config_name
            )
            
            # Check encryption
            if not config.get('KmsKeyId'):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::Endpoint',
                    resource_name=endpoint_name,
                    resource_arn=response['EndpointArn'],
                    severity='HIGH',
                    issue='Endpoint does not have KMS encryption',
                    control='ISO 27001 A.8.24',
                    remediation='Enable KMS encryption for endpoint',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
            
            # Check data capture (for monitoring)
            if not config.get('DataCaptureConfig'):
                self.findings.append(SecurityFinding(
                    resource_type='AWS::SageMaker::Endpoint',
                    resource_name=endpoint_name,
                    resource_arn=response['EndpointArn'],
                    severity='LOW',
                    issue='Data capture not configured for monitoring',
                    control='ISO 42001 9.2.2',
                    remediation='Enable data capture for model monitoring',
                    timestamp=datetime.utcnow().isoformat(),
                    region=self.region
                ))
                
        except Exception as e:
            print(f"[!] Error checking endpoint {endpoint_name}: {e}")
    
    def _has_required_tags(self, tags: List[Dict]) -> bool:
        """Check if resource has required tags"""
        required_tags = {'DataClassification', 'Owner', 'Purpose'}
        tag_keys = {tag['Key'] for tag in tags}
        return required_tags.issubset(tag_keys)
    
    def export_findings(self, output_file: str = 'sagemaker_findings.json') -> None:
        """Export findings to JSON file"""
        findings_dict = [asdict(f) for f in self.findings]
        
        with open(output_file, 'w') as f:
            json.dump({
                'scan_timestamp': datetime.utcnow().isoformat(),
                'region': self.region,
                'total_findings': len(self.findings),
                'severity_breakdown': self._get_severity_breakdown(),
                'findings': findings_dict
            }, f, indent=2)
        
        print(f"[+] Findings exported to {output_file}")
    
    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get count of findings by severity"""
        breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in self.findings:
            breakdown[finding.severity] += 1
        return breakdown
    
    def print_summary(self) -> None:
        """Print summary of findings"""
        breakdown = self._get_severity_breakdown()
        
        print("\n" + "="*60)
        print("SAGEMAKER SECURITY SCAN SUMMARY")
        print("="*60)
        print(f"Region: {self.region}")
        print(f"Total Findings: {len(self.findings)}")
        print(f"\nSeverity Breakdown:")
        print(f"  CRITICAL: {breakdown['CRITICAL']}")
        print(f"  HIGH:     {breakdown['HIGH']}")
        print(f"  MEDIUM:   {breakdown['MEDIUM']}")
        print(f"  LOW:      {breakdown['LOW']}")
        print("="*60 + "\n")
        
        if self.findings:
            print("Top 5 Findings:")
            for i, finding in enumerate(self.findings[:5], 1):
                print(f"\n{i}. [{finding.severity}] {finding.resource_type}")
                print(f"   Resource: {finding.resource_name}")
                print(f"   Issue: {finding.issue}")
                print(f"   Control: {finding.control}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scan AWS SageMaker resources for security violations'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region to scan (default: us-east-1)'
    )
    parser.add_argument(
        '--output',
        default='sagemaker_findings.json',
        help='Output file for findings (default: sagemaker_findings.json)'
    )
    
    args = parser.parse_args()
    
    # Run scan
    scanner = SageMakerScanner(region=args.region)
    scanner.scan_all()
    scanner.print_summary()
    scanner.export_findings(args.output)


if __name__ == '__main__':
    main()
