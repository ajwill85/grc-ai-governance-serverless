"""
IAM Scanner for SageMaker Roles
Analyzes IAM roles for least privilege violations
ISO 27001 A.5.15-A.5.18, ISO 27701 6.2.1-6.2.3, ISO 42001 6.1.3-6.1.4
"""

import boto3
import json
from typing import List, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class IAMFinding:
    """IAM security finding"""
    role_name: str
    role_arn: str
    severity: str
    issue: str
    control: str
    remediation: str
    timestamp: str


class IAMScanner:
    """Scanner for IAM roles used by SageMaker"""
    
    def __init__(self):
        self.iam = boto3.client('iam')
        self.findings: List[IAMFinding] = []
    
    def scan_all(self) -> List[IAMFinding]:
        """Scan all SageMaker IAM roles"""
        print("[*] Starting IAM role scan...")
        
        roles = self._get_sagemaker_roles()
        print(f"[*] Found {len(roles)} SageMaker roles")
        
        for role in roles:
            self._check_role(role)
        
        print(f"[+] Scan complete. Found {len(self.findings)} violations.")
        return self.findings
    
    def _get_sagemaker_roles(self) -> List[Dict]:
        """Get all IAM roles with SageMaker trust relationship"""
        roles = []
        paginator = self.iam.get_paginator('list_roles')
        
        for page in paginator.paginate():
            for role in page['Roles']:
                trust_policy = role['AssumeRolePolicyDocument']
                for statement in trust_policy.get('Statement', []):
                    principal = statement.get('Principal', {})
                    service = principal.get('Service', '')
                    if isinstance(service, str):
                        service = [service]
                    if 'sagemaker.amazonaws.com' in service:
                        roles.append(role)
                        break
        
        return roles
    
    def _check_role(self, role: Dict) -> None:
        """Check individual role for violations"""
        role_name = role['RoleName']
        
        # Get inline policies
        inline_policies = self._get_inline_policies(role_name)
        
        # Get attached policies
        attached_policies = self._get_attached_policies(role_name)
        
        # Check for violations
        self._check_wildcard_actions(role, inline_policies + attached_policies)
        self._check_wildcard_resources(role, inline_policies + attached_policies)
        self._check_dangerous_permissions(role, inline_policies + attached_policies)
        self._check_stale_role(role)
    
    def _get_inline_policies(self, role_name: str) -> List[Dict]:
        """Get inline policies for role"""
        policies = []
        try:
            policy_names = self.iam.list_role_policies(RoleName=role_name)
            for policy_name in policy_names['PolicyNames']:
                policy = self.iam.get_role_policy(
                    RoleName=role_name,
                    PolicyName=policy_name
                )
                policies.append(policy['PolicyDocument'])
        except Exception as e:
            print(f"[!] Error getting inline policies for {role_name}: {e}")
        return policies
    
    def _get_attached_policies(self, role_name: str) -> List[Dict]:
        """Get attached managed policies for role"""
        policies = []
        try:
            attached = self.iam.list_attached_role_policies(RoleName=role_name)
            for policy in attached['AttachedPolicies']:
                policy_arn = policy['PolicyArn']
                policy_version = self.iam.get_policy(PolicyArn=policy_arn)
                version_id = policy_version['Policy']['DefaultVersionId']
                policy_doc = self.iam.get_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=version_id
                )
                policies.append(policy_doc['PolicyVersion']['Document'])
        except Exception as e:
            print(f"[!] Error getting attached policies for {role_name}: {e}")
        return policies
    
    def _check_wildcard_actions(self, role: Dict, policies: List[Dict]) -> None:
        """Check for wildcard actions"""
        for policy in policies:
            for statement in policy.get('Statement', []):
                if statement.get('Effect') != 'Allow':
                    continue
                
                actions = statement.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]
                
                if '*' in actions:
                    self.findings.append(IAMFinding(
                        role_name=role['RoleName'],
                        role_arn=role['Arn'],
                        severity='CRITICAL',
                        issue='Role has wildcard action (*)',
                        control='ISO 27001 A.5.15, ISO 27701 6.2.1',
                        remediation='Replace wildcard with specific actions',
                        timestamp=datetime.utcnow().isoformat()
                    ))
    
    def _check_wildcard_resources(self, role: Dict, policies: List[Dict]) -> None:
        """Check for wildcard resources"""
        for policy in policies:
            for statement in policy.get('Statement', []):
                if statement.get('Effect') != 'Allow':
                    continue
                
                resources = statement.get('Resource', [])
                if isinstance(resources, str):
                    resources = [resources]
                
                if '*' in resources:
                    self.findings.append(IAMFinding(
                        role_name=role['RoleName'],
                        role_arn=role['Arn'],
                        severity='HIGH',
                        issue='Role has wildcard resource (*)',
                        control='ISO 27001 A.5.16',
                        remediation='Scope permissions to specific resources',
                        timestamp=datetime.utcnow().isoformat()
                    ))
    
    def _check_dangerous_permissions(self, role: Dict, policies: List[Dict]) -> None:
        """Check for dangerous permissions"""
        dangerous_actions = {
            'iam:CreateRole', 'iam:DeleteRole', 'iam:PutRolePolicy',
            'kms:DisableKey', 'kms:ScheduleKeyDeletion',
            's3:DeleteBucket', 'sagemaker:DeleteNotebookInstance'
        }
        
        for policy in policies:
            for statement in policy.get('Statement', []):
                if statement.get('Effect') != 'Allow':
                    continue
                
                actions = statement.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]
                
                found_dangerous = set(actions) & dangerous_actions
                if found_dangerous:
                    self.findings.append(IAMFinding(
                        role_name=role['RoleName'],
                        role_arn=role['Arn'],
                        severity='HIGH',
                        issue=f'Role has dangerous permissions: {", ".join(found_dangerous)}',
                        control='ISO 27001 A.5.18, ISO 42001 6.1.3',
                        remediation='Remove dangerous permissions or require approval workflow',
                        timestamp=datetime.utcnow().isoformat()
                    ))
    
    def _check_stale_role(self, role: Dict) -> None:
        """Check if role hasn't been used recently"""
        try:
            role_name = role['RoleName']
            role_details = self.iam.get_role(RoleName=role_name)
            
            last_used = role_details['Role'].get('RoleLastUsed', {}).get('LastUsedDate')
            if last_used:
                days_since_use = (datetime.now(last_used.tzinfo) - last_used).days
                if days_since_use > 90:
                    self.findings.append(IAMFinding(
                        role_name=role_name,
                        role_arn=role['Arn'],
                        severity='MEDIUM',
                        issue=f'Role not used in {days_since_use} days',
                        control='ISO 27001 A.5.18, ISO 27701 6.2.3',
                        remediation='Review and remove if unnecessary',
                        timestamp=datetime.utcnow().isoformat()
                    ))
        except Exception as e:
            print(f"[!] Error checking last used for {role['RoleName']}: {e}")
    
    def export_findings(self, output_file: str = 'iam_findings.json') -> None:
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
        print("IAM ROLE SCAN SUMMARY")
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
    scanner = IAMScanner()
    scanner.scan_all()
    scanner.print_summary()
    scanner.export_findings()


if __name__ == '__main__':
    main()
