# Data Classification and Governance Policy
# Enforces data classification, minimization, and retention requirements
# ISO 27001 A.5.12, A.5.34, ISO 27701 6.4.1-6.4.4, ISO 42001 6.2.1-6.2.4

package data.classification

import future.keywords.if
import future.keywords.in

default allow = false

# Deny S3 buckets without classification tags
deny[msg] if {
    input.resource_type == "AWS::S3::Bucket"
    input.sagemaker_usage == true
    not has_classification_tag(input.tags)
    msg := sprintf(
        "VIOLATION: S3 bucket '%s' used by SageMaker must have DataClassification tag. Control: ISO 27001 A.5.12, ISO 27701 6.4.1",
        [input.bucket_name]
    )
}

# Deny PII data without encryption
deny[msg] if {
    input.resource_type == "AWS::S3::Bucket"
    get_classification(input.tags) in ["PII", "SENSITIVE"]
    not input.encryption_enabled
    msg := sprintf(
        "VIOLATION: S3 bucket '%s' containing %s data must have encryption enabled. Control: ISO 27701 6.4.1",
        [input.bucket_name, get_classification(input.tags)]
    )
}

# Deny PII data without versioning
deny[msg] if {
    input.resource_type == "AWS::S3::Bucket"
    get_classification(input.tags) == "PII"
    not input.versioning_enabled
    msg := sprintf(
        "VIOLATION: S3 bucket '%s' containing PII must have versioning enabled. Control: ISO 27701 6.4.3",
        [input.bucket_name]
    )
}

# Deny buckets without lifecycle policies
deny[msg] if {
    input.resource_type == "AWS::S3::Bucket"
    input.sagemaker_usage == true
    not has_lifecycle_policy(input)
    msg := sprintf(
        "VIOLATION: S3 bucket '%s' must have lifecycle policy for data retention. Control: ISO 27001 A.5.34, ISO 27701 6.4.3",
        [input.bucket_name]
    )
}

# Deny excessive data retention
deny[msg] if {
    input.resource_type == "AWS::S3::Bucket"
    classification := get_classification(input.tags)
    max_retention := get_max_retention_days(classification)
    lifecycle := input.lifecycle_rules[_]
    lifecycle.expiration_days > max_retention
    msg := sprintf(
        "VIOLATION: S3 bucket '%s' retention (%d days) exceeds maximum for %s data (%d days). Control: ISO 27701 6.4.3",
        [input.bucket_name, lifecycle.expiration_days, classification, max_retention]
    )
}

# Deny training datasets without data quality checks
deny[msg] if {
    input.resource_type == "AWS::SageMaker::TrainingJob"
    not has_data_quality_check(input)
    msg := sprintf(
        "VIOLATION: SageMaker training job '%s' must include data quality validation. Control: ISO 42001 6.2.4, ISO 27001 A.8.24",
        [input.training_job_name]
    )
}

# Deny excessive data collection (data minimization)
deny[msg] if {
    input.resource_type == "AWS::Glue::Crawler"
    input.sagemaker_pipeline == true
    column_count := count(input.schema.columns)
    column_count > input.required_columns * 1.5  # 50% tolerance
    msg := sprintf(
        "VIOLATION: Glue crawler '%s' collects %d columns but only %d required. Apply data minimization. Control: ISO 27701 6.4.2, ISO 42001 6.2.2",
        [input.crawler_name, column_count, input.required_columns]
    )
}

# Deny PII in model artifacts without anonymization
deny[msg] if {
    input.resource_type == "AWS::SageMaker::Model"
    input.contains_pii == true
    not input.anonymization_applied
    msg := sprintf(
        "VIOLATION: SageMaker model '%s' contains PII without anonymization. Control: ISO 27701 6.4.2",
        [input.model_name]
    )
}

# Deny cross-region data transfer for PII without approval
deny[msg] if {
    input.resource_type == "AWS::S3::Bucket"
    get_classification(input.tags) == "PII"
    input.replication_configuration
    dest_region := input.replication_configuration.rules[_].destination.region
    dest_region != input.region
    not has_cross_region_approval(input)
    msg := sprintf(
        "VIOLATION: S3 bucket '%s' replicates PII to %s without approval. Control: ISO 27701 6.16.1",
        [input.bucket_name, dest_region]
    )
}

# Deny public access to classified data
deny[msg] if {
    input.resource_type == "AWS::S3::Bucket"
    classification := get_classification(input.tags)
    classification in ["PII", "SENSITIVE", "CONFIDENTIAL"]
    input.public_access_block.block_public_acls == false
    msg := sprintf(
        "VIOLATION: S3 bucket '%s' containing %s data must block all public access. Control: ISO 27701 6.6.1",
        [input.bucket_name, classification]
    )
}

# Deny untagged SageMaker resources
deny[msg] if {
    input.resource_type in [
        "AWS::SageMaker::NotebookInstance",
        "AWS::SageMaker::TrainingJob",
        "AWS::SageMaker::Model",
        "AWS::SageMaker::Endpoint"
    ]
    not has_required_tags(input.tags)
    msg := sprintf(
        "VIOLATION: SageMaker resource '%s' missing required tags (DataClassification, Owner, Purpose). Control: ISO 27001 A.5.12",
        [get_resource_name(input)]
    )
}

# Helper functions
has_classification_tag(tags) if {
    tag := tags[_]
    tag.Key == "DataClassification"
    tag.Value in ["PUBLIC", "INTERNAL", "SENSITIVE", "PII", "CONFIDENTIAL"]
}

get_classification(tags) := classification if {
    tag := tags[_]
    tag.Key == "DataClassification"
    classification := tag.Value
}

get_classification(tags) := "UNKNOWN" if {
    not has_classification_tag(tags)
}

get_max_retention_days(classification) := days if {
    retention_map := {
        "PII": 365,
        "SENSITIVE": 730,
        "CONFIDENTIAL": 1095,
        "INTERNAL": 1825,
        "PUBLIC": 3650
    }
    days := retention_map[classification]
}

get_max_retention_days(classification) := 365 if {
    not classification in ["PII", "SENSITIVE", "CONFIDENTIAL", "INTERNAL", "PUBLIC"]
}

has_lifecycle_policy(bucket) if {
    count(bucket.lifecycle_rules) > 0
}

has_data_quality_check(training_job) if {
    training_job.tags[_].Key == "DataQualityCheck"
    training_job.tags[_].Value == "Completed"
}

has_cross_region_approval(bucket) if {
    bucket.tags[_].Key == "CrossRegionApproval"
    bucket.tags[_].Value == "Approved"
}

has_required_tags(tags) if {
    required := {"DataClassification", "Owner", "Purpose"}
    tag_keys := {tag.Key | tag := tags[_]}
    required_present := required & tag_keys
    count(required_present) == count(required)
}

get_resource_name(resource) := name if {
    name := resource.notebook_name
}

get_resource_name(resource) := name if {
    name := resource.training_job_name
}

get_resource_name(resource) := name if {
    name := resource.model_name
}

get_resource_name(resource) := name if {
    name := resource.endpoint_name
}

get_resource_name(resource) := "unknown" if {
    not resource.notebook_name
    not resource.training_job_name
    not resource.model_name
    not resource.endpoint_name
}

allow if {
    count(deny) == 0
}

severity[result] if {
    count(deny) > 0
    pii_violations := count([v | v := deny[_]; contains(v, "PII")])
    level := "CRITICAL" if pii_violations > 0 else "HIGH"
    result := {
        "level": level,
        "violations": count(deny),
        "pii_related": pii_violations,
        "controls_affected": [
            "ISO 27001 A.5.12",
            "ISO 27001 A.5.34",
            "ISO 27701 6.4.1",
            "ISO 27701 6.4.2",
            "ISO 27701 6.4.3",
            "ISO 27701 6.4.4",
            "ISO 42001 6.2.1",
            "ISO 42001 6.2.2",
            "ISO 42001 6.2.4"
        ]
    }
}
