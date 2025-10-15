# SageMaker Encryption Policy
# Enforces encryption requirements for SageMaker resources
# ISO 27001 A.8.24, ISO 27701 6.6.1, ISO 42001 6.3.1

package sagemaker.encryption

import future.keywords.if
import future.keywords.in

# Default deny
default allow = false

# Deny SageMaker notebooks without encryption at rest
deny[msg] if {
    input.resource_type == "AWS::SageMaker::NotebookInstance"
    not input.kms_key_id
    msg := sprintf(
        "VIOLATION: SageMaker notebook '%s' must have KMS encryption enabled. Control: ISO 27001 A.8.24, ISO 27701 6.6.1",
        [input.notebook_name]
    )
}

# Deny SageMaker notebooks with root access enabled
deny[msg] if {
    input.resource_type == "AWS::SageMaker::NotebookInstance"
    input.root_access == "Enabled"
    msg := sprintf(
        "VIOLATION: SageMaker notebook '%s' must disable root access. Control: ISO 27001 A.5.18",
        [input.notebook_name]
    )
}

# Deny SageMaker endpoints without encryption
deny[msg] if {
    input.resource_type == "AWS::SageMaker::EndpointConfig"
    not input.kms_key_id
    msg := sprintf(
        "VIOLATION: SageMaker endpoint config '%s' must encrypt data at rest. Control: ISO 27001 A.8.24",
        [input.endpoint_config_name]
    )
}

# Deny SageMaker training jobs without encryption
deny[msg] if {
    input.resource_type == "AWS::SageMaker::TrainingJob"
    not input.output_data_config.kms_key_id
    msg := sprintf(
        "VIOLATION: SageMaker training job '%s' must encrypt output data. Control: ISO 27001 A.8.24, ISO 42001 6.3.1",
        [input.training_job_name]
    )
}

# Deny SageMaker training jobs without volume encryption
deny[msg] if {
    input.resource_type == "AWS::SageMaker::TrainingJob"
    not input.resource_config.volume_kms_key_id
    msg := sprintf(
        "VIOLATION: SageMaker training job '%s' must encrypt training volumes. Control: ISO 27001 A.8.24",
        [input.training_job_name]
    )
}

# Deny unencrypted inter-container traffic
deny[msg] if {
    input.resource_type == "AWS::SageMaker::TrainingJob"
    input.enable_inter_container_traffic_encryption == false
    msg := sprintf(
        "VIOLATION: SageMaker training job '%s' must encrypt inter-container traffic. Control: ISO 27001 A.8.24",
        [input.training_job_name]
    )
}

# Deny SageMaker models without encryption
deny[msg] if {
    input.resource_type == "AWS::SageMaker::Model"
    not input.vpc_config
    input.data_classification in ["PII", "SENSITIVE"]
    msg := sprintf(
        "VIOLATION: SageMaker model '%s' handling %s data must use VPC configuration. Control: ISO 27701 6.6.2, ISO 42001 6.3.2",
        [input.model_name, input.data_classification]
    )
}

# Allow if no violations
allow if {
    count(deny) == 0
}

# Helper function to check if encryption is properly configured
is_encrypted(resource) if {
    resource.kms_key_id
}

# Helper function to validate KMS key
valid_kms_key(key_id) if {
    startswith(key_id, "arn:aws:kms:")
}

# Severity classification
severity[result] if {
    count(deny) > 0
    result := {
        "level": "HIGH",
        "violations": count(deny),
        "controls_affected": [
            "ISO 27001 A.8.24",
            "ISO 27701 6.6.1",
            "ISO 42001 6.3.1"
        ]
    }
}
