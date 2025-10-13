# SageMaker Network Security Policy
# Enforces network isolation and security group requirements
# ISO 27001 A.8.20-A.8.21, ISO 27701 6.6.2, ISO 42001 6.3.2

package sagemaker.network

import future.keywords.if
import future.keywords.in

default allow = false

# Deny SageMaker notebooks with direct internet access
deny[msg] if {
    input.resource_type == "AWS::SageMaker::NotebookInstance"
    input.direct_internet_access == "Enabled"
    not input.subnet_id
    msg := sprintf(
        "VIOLATION: SageMaker notebook '%s' must not have direct internet access without VPC. Control: ISO 27001 A.8.20",
        [input.notebook_name]
    )
}

# Deny SageMaker notebooks without VPC for sensitive data
deny[msg] if {
    input.resource_type == "AWS::SageMaker::NotebookInstance"
    input.data_classification in ["PII", "SENSITIVE", "CONFIDENTIAL"]
    not input.subnet_id
    msg := sprintf(
        "VIOLATION: SageMaker notebook '%s' handling %s data must be deployed in VPC. Control: ISO 27701 6.6.2, ISO 42001 6.3.2",
        [input.notebook_name, input.data_classification]
    )
}

# Deny SageMaker endpoints without VPC configuration
deny[msg] if {
    input.resource_type == "AWS::SageMaker::EndpointConfig"
    input.production_variants[_].instance_type
    not input.vpc_config
    input.public_facing == true
    msg := sprintf(
        "VIOLATION: Public-facing SageMaker endpoint '%s' must use VPC configuration. Control: ISO 27001 A.8.21, ISO 42001 6.3.2",
        [input.endpoint_config_name]
    )
}

# Deny overly permissive security groups
deny[msg] if {
    input.resource_type == "AWS::EC2::SecurityGroup"
    input.sagemaker_resource == true
    rule := input.ingress_rules[_]
    rule.cidr == "0.0.0.0/0"
    rule.port != 443
    msg := sprintf(
        "VIOLATION: Security group '%s' for SageMaker has overly permissive ingress (0.0.0.0/0 on port %d). Control: ISO 27001 A.8.20",
        [input.security_group_id, rule.port]
    )
}

# Deny SageMaker training jobs without network isolation
deny[msg] if {
    input.resource_type == "AWS::SageMaker::TrainingJob"
    input.enable_network_isolation == false
    input.data_classification in ["PII", "SENSITIVE"]
    msg := sprintf(
        "VIOLATION: SageMaker training job '%s' handling %s data must enable network isolation. Control: ISO 27701 6.6.2",
        [input.training_job_name, input.data_classification]
    )
}

# Deny SageMaker processing jobs without VPC
deny[msg] if {
    input.resource_type == "AWS::SageMaker::ProcessingJob"
    not input.network_config.vpc_config
    input.data_classification in ["PII", "SENSITIVE"]
    msg := sprintf(
        "VIOLATION: SageMaker processing job '%s' handling %s data must use VPC. Control: ISO 27701 6.6.2",
        [input.processing_job_name, input.data_classification]
    )
}

# Require VPC endpoints for S3 access
deny[msg] if {
    input.resource_type == "AWS::SageMaker::NotebookInstance"
    input.subnet_id
    not has_vpc_endpoint_for_s3(input.vpc_id)
    msg := sprintf(
        "VIOLATION: VPC '%s' for SageMaker notebook must have S3 VPC endpoint. Control: ISO 27001 A.8.21",
        [input.vpc_id]
    )
}

# Helper functions
has_vpc_endpoint_for_s3(vpc_id) if {
    input.vpc_endpoints[_].service_name == "com.amazonaws.region.s3"
    input.vpc_endpoints[_].vpc_id == vpc_id
}

is_private_subnet(subnet_id) if {
    subnet := input.subnets[_]
    subnet.subnet_id == subnet_id
    not subnet.map_public_ip_on_launch
}

allow if {
    count(deny) == 0
}

severity[result] if {
    count(deny) > 0
    result := {
        "level": "HIGH",
        "violations": count(deny),
        "controls_affected": [
            "ISO 27001 A.8.20",
            "ISO 27001 A.8.21",
            "ISO 27701 6.6.2",
            "ISO 42001 6.3.2"
        ]
    }
}
