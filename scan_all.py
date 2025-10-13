#!/usr/bin/env python3
"""
Unified Scanner for AWS AI Governance
Runs all scanners and generates consolidated report
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from scanners import SageMakerScanner, IAMScanner, S3Scanner


class UnifiedScanner:
    """Runs all scanners and consolidates results"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.all_findings = []
    
    def run_all_scans(self) -> Dict:
        """Run all scanners"""
        print("\n" + "="*70)
        print("AWS AI GOVERNANCE FRAMEWORK - UNIFIED SECURITY SCAN")
        print("="*70)
        print(f"Region: {self.region}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        print("="*70 + "\n")
        
        results = {
            'scan_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'region': self.region,
                'scanners_run': []
            },
            'findings_by_scanner': {},
            'consolidated_findings': [],
            'summary': {}
        }
        
        # Run SageMaker scanner
        print("\n[1/3] Running SageMaker Scanner...")
        sagemaker_scanner = SageMakerScanner(region=self.region)
        sagemaker_findings = sagemaker_scanner.scan_all()
        results['findings_by_scanner']['sagemaker'] = [
            self._finding_to_dict(f) for f in sagemaker_findings
        ]
        results['scan_metadata']['scanners_run'].append('SageMaker')
        
        # Run IAM scanner
        print("\n[2/3] Running IAM Scanner...")
        iam_scanner = IAMScanner()
        iam_findings = iam_scanner.scan_all()
        results['findings_by_scanner']['iam'] = [
            self._finding_to_dict(f) for f in iam_findings
        ]
        results['scan_metadata']['scanners_run'].append('IAM')
        
        # Run S3 scanner
        print("\n[3/3] Running S3 Scanner...")
        s3_scanner = S3Scanner(region=self.region)
        s3_findings = s3_scanner.scan_all()
        results['findings_by_scanner']['s3'] = [
            self._finding_to_dict(f) for f in s3_findings
        ]
        results['scan_metadata']['scanners_run'].append('S3')
        
        # Consolidate findings
        self.all_findings = sagemaker_findings + iam_findings + s3_findings
        results['consolidated_findings'] = [
            self._finding_to_dict(f) for f in self.all_findings
        ]
        
        # Generate summary
        results['summary'] = self._generate_summary()
        
        return results
    
    def _finding_to_dict(self, finding) -> Dict:
        """Convert finding dataclass to dict"""
        if hasattr(finding, '__dict__'):
            return finding.__dict__
        return finding
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        control_counts = {}
        
        for finding in self.all_findings:
            # Count by severity
            severity = getattr(finding, 'severity', 'UNKNOWN')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by control
            control = getattr(finding, 'control', 'UNKNOWN')
            for ctrl in control.split(','):
                ctrl = ctrl.strip()
                control_counts[ctrl] = control_counts.get(ctrl, 0) + 1
        
        # Get top violated controls
        top_controls = sorted(
            control_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_findings': len(self.all_findings),
            'severity_breakdown': severity_counts,
            'top_violated_controls': dict(top_controls),
            'risk_score': self._calculate_risk_score(severity_counts)
        }
    
    def _calculate_risk_score(self, severity_counts: Dict) -> int:
        """Calculate overall risk score (0-100)"""
        weights = {'CRITICAL': 10, 'HIGH': 5, 'MEDIUM': 2, 'LOW': 1}
        total_score = sum(
            severity_counts.get(sev, 0) * weight
            for sev, weight in weights.items()
        )
        # Normalize to 0-100 scale
        return min(100, total_score)
    
    def print_summary(self, results: Dict) -> None:
        """Print consolidated summary"""
        summary = results['summary']
        
        print("\n" + "="*70)
        print("CONSOLIDATED SCAN SUMMARY")
        print("="*70)
        print(f"Total Findings: {summary['total_findings']}")
        print(f"Risk Score: {summary['risk_score']}/100")
        
        print(f"\nSeverity Breakdown:")
        for severity, count in summary['severity_breakdown'].items():
            print(f"  {severity:10s}: {count}")
        
        print(f"\nTop Violated Controls:")
        for i, (control, count) in enumerate(
            list(summary['top_violated_controls'].items())[:5], 1
        ):
            print(f"  {i}. {control}: {count} violations")
        
        print("\nFindings by Scanner:")
        for scanner, findings in results['findings_by_scanner'].items():
            print(f"  {scanner.upper():12s}: {len(findings)} findings")
        
        print("="*70 + "\n")
    
    def export_results(self, results: Dict, output_file: str) -> None:
        """Export results to JSON"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"[+] Results exported to {output_file}")
    
    def generate_html_report(self, results: Dict, output_file: str) -> None:
        """Generate HTML report"""
        html = self._create_html_report(results)
        with open(output_file, 'w') as f:
            f.write(html)
        print(f"[+] HTML report generated: {output_file}")
    
    def _create_html_report(self, results: Dict) -> str:
        """Create HTML report content"""
        summary = results['summary']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AWS AI Governance Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #232f3e; }}
        h2 {{ color: #ff9900; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .critical {{ color: #d13212; font-weight: bold; }}
        .high {{ color: #ff9900; font-weight: bold; }}
        .medium {{ color: #1d8102; }}
        .low {{ color: #879596; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #232f3e; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .risk-score {{ font-size: 48px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>AWS AI Governance Framework - Security Scan Report</h1>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p><strong>Scan Date:</strong> {results['scan_metadata']['timestamp']}</p>
        <p><strong>Region:</strong> {results['scan_metadata']['region']}</p>
        <p><strong>Total Findings:</strong> {summary['total_findings']}</p>
        <p><strong>Risk Score:</strong> <span class="risk-score">{summary['risk_score']}/100</span></p>
    </div>
    
    <h2>Severity Breakdown</h2>
    <table>
        <tr>
            <th>Severity</th>
            <th>Count</th>
        </tr>
        <tr>
            <td class="critical">CRITICAL</td>
            <td>{summary['severity_breakdown'].get('CRITICAL', 0)}</td>
        </tr>
        <tr>
            <td class="high">HIGH</td>
            <td>{summary['severity_breakdown'].get('HIGH', 0)}</td>
        </tr>
        <tr>
            <td class="medium">MEDIUM</td>
            <td>{summary['severity_breakdown'].get('MEDIUM', 0)}</td>
        </tr>
        <tr>
            <td class="low">LOW</td>
            <td>{summary['severity_breakdown'].get('LOW', 0)}</td>
        </tr>
    </table>
    
    <h2>Top Violated Controls</h2>
    <table>
        <tr>
            <th>Control</th>
            <th>Violations</th>
        </tr>
"""
        
        for control, count in list(summary['top_violated_controls'].items())[:10]:
            html += f"        <tr><td>{control}</td><td>{count}</td></tr>\n"
        
        html += """
    </table>
    
    <h2>Detailed Findings</h2>
"""
        
        for scanner, findings in results['findings_by_scanner'].items():
            html += f"    <h3>{scanner.upper()} Scanner ({len(findings)} findings)</h3>\n"
            if findings:
                html += """    <table>
        <tr>
            <th>Severity</th>
            <th>Resource</th>
            <th>Issue</th>
            <th>Control</th>
        </tr>
"""
                for finding in findings[:20]:  # Limit to first 20
                    severity_class = finding.get('severity', 'LOW').lower()
                    resource_name = finding.get('resource_name') or finding.get('role_name') or finding.get('bucket_name', 'N/A')
                    html += f"""        <tr>
            <td class="{severity_class}">{finding.get('severity', 'UNKNOWN')}</td>
            <td>{resource_name}</td>
            <td>{finding.get('issue', 'N/A')}</td>
            <td>{finding.get('control', 'N/A')}</td>
        </tr>
"""
                html += "    </table>\n"
        
        html += """
</body>
</html>
"""
        return html


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run unified AWS AI governance security scan'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region to scan (default: us-east-1)'
    )
    parser.add_argument(
        '--output',
        default='governance_scan_results.json',
        help='Output JSON file (default: governance_scan_results.json)'
    )
    parser.add_argument(
        '--html',
        default='governance_scan_report.html',
        help='Output HTML report (default: governance_scan_report.html)'
    )
    
    args = parser.parse_args()
    
    # Run unified scan
    scanner = UnifiedScanner(region=args.region)
    results = scanner.run_all_scans()
    
    # Print summary
    scanner.print_summary(results)
    
    # Export results
    scanner.export_results(results, args.output)
    scanner.generate_html_report(results, args.html)
    
    print("\n[+] Scan complete!")
    print(f"[+] View detailed results: {args.output}")
    print(f"[+] View HTML report: {args.html}")


if __name__ == '__main__':
    main()
