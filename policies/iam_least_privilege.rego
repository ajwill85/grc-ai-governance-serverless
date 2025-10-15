# IAM Least Privilege Policy
# Enforces least privilege access for SageMaker and AI/ML resources
# ISO 27001 A.5.15-A.5.18, ISO 27701 6.2.1-6.2.3, ISO 42001 6.1.3-6.1.4

package iam.least_privilege

import future.keywords.if
import future.keywords.in

default allow = false

# Deny wildcard actions in IAM policies
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    input.role_name
    statement := input.policy_document.Statement[_]
    action := statement.Action[_]
    action == "*"
    msg := sprintf(
        "VIOLATION: IAM role '%s' has wildcard action (*). Use specific actions. Control: ISO 27001 A.5.15, ISO 27701 6.2.1",
        [input.role_name]
    )
}

# Deny wildcard resources in IAM policies
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    input.role_name
    statement := input.policy_document.Statement[_]
    resource := statement.Resource[_]
    resource == "*"
    statement.Effect == "Allow"
    not is_read_only_action(statement.Action)
    msg := sprintf(
        "VIOLATION: IAM role '%s' has wildcard resource (*) for write actions. Scope to specific resources. Control: ISO 27001 A.5.16",
        [input.role_name]
    )
}

# Deny overly permissive SageMaker execution roles
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    is_sagemaker_role(input)
    statement := input.policy_document.Statement[_]
    has_dangerous_sagemaker_permissions(statement)
    msg := sprintf(
        "VIOLATION: SageMaker role '%s' has dangerous permissions: %s. Control: ISO 42001 6.1.3",
        [input.role_name, concat(", ", statement.Action)]
    )
}

# Deny roles without MFA for privileged actions
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    statement := input.policy_document.Statement[_]
    has_privileged_actions(statement)
    not requires_mfa(statement)
    msg := sprintf(
        "VIOLATION: IAM role '%s' allows privileged actions without MFA. Control: ISO 27001 A.5.18",
        [input.role_name]
    )
}

# Deny cross-account access without conditions
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    statement := input.assume_role_policy.Statement[_]
    principal := statement.Principal.AWS[_]
    not startswith(principal, sprintf("arn:aws:iam::%s:", [input.account_id]))
    not statement.Condition
    msg := sprintf(
        "VIOLATION: IAM role '%s' allows cross-account access without conditions. Control: ISO 27001 A.5.19",
        [input.role_name]
    )
}

# Deny roles with admin access to AI/ML resources
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    statement := input.policy_document.Statement[_]
    action := statement.Action[_]
    contains(action, "sagemaker:*")
    statement.Effect == "Allow"
    msg := sprintf(
        "VIOLATION: IAM role '%s' has admin access to SageMaker (sagemaker:*). Use specific permissions. Control: ISO 27001 A.5.15",
        [input.role_name]
    )
}

# Deny roles that can modify encryption settings
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    not is_security_admin_role(input)
    statement := input.policy_document.Statement[_]
    action := statement.Action[_]
    action in [
        "kms:DisableKey",
        "kms:ScheduleKeyDeletion",
        "kms:DeleteAlias"
    ]
    msg := sprintf(
        "VIOLATION: Non-security role '%s' can modify KMS keys. Control: ISO 27001 A.5.18, ISO 27701 6.2.2",
        [input.role_name]
    )
}

# Deny roles with data deletion permissions without approval workflow
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    statement := input.policy_document.Statement[_]
    has_data_deletion_permissions(statement)
    not has_approval_workflow(input)
    msg := sprintf(
        "VIOLATION: IAM role '%s' can delete data without approval workflow. Control: ISO 27701 6.4.3",
        [input.role_name]
    )
}

# Deny stale IAM roles (not used in 90 days)
deny[msg] if {
    input.resource_type == "AWS::IAM::Role"
    input.last_used_date
    days_since_use := time.now_ns() - time.parse_rfc3339_ns(input.last_used_date)
    days_since_use > 90 * 24 * 60 * 60 * 1000000000  # 90 days in nanoseconds
    msg := sprintf(
        "VIOLATION: IAM role '%s' has not been used in 90+ days. Review and remove if unnecessary. Control: ISO 27001 A.5.18, ISO 27701 6.2.3",
        [input.role_name]
    )
}

# Helper functions
is_sagemaker_role(role) if {
    statement := role.assume_role_policy.Statement[_]
    principal := statement.Principal.Service[_]
    principal == "sagemaker.amazonaws.com"
}

is_read_only_action(actions) if {
    action := actions[_]
    startswith(action, "Describe")
}

is_read_only_action(actions) if {
    action := actions[_]
    startswith(action, "List")
}

is_read_only_action(actions) if {
    action := actions[_]
    startswith(action, "Get")
}

has_dangerous_sagemaker_permissions(statement) if {
    action := statement.Action[_]
    action in [
        "sagemaker:CreatePresignedNotebookInstanceUrl",
        "sagemaker:UpdateNotebookInstance",
        "sagemaker:DeleteNotebookInstance"
    ]
    statement.Effect == "Allow"
}

has_privileged_actions(statement) if {
    action := statement.Action[_]
    action in [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:PutRolePolicy",
        "iam:AttachRolePolicy"
    ]
}

requires_mfa(statement) if {
    statement.Condition["Bool"]["aws:MultiFactorAuthPresent"]
}

is_security_admin_role(role) if {
    contains(role.role_name, "SecurityAdmin")
}

is_security_admin_role(role) if {
    contains(role.role_name, "InfoSec")
}

has_data_deletion_permissions(statement) if {
    action := statement.Action[_]
    action in [
        "s3:DeleteObject",
        "s3:DeleteBucket",
        "dynamodb:DeleteItem",
        "dynamodb:DeleteTable"
    ]
}

has_approval_workflow(role) if {
    role.tags[_].Key == "ApprovalWorkflow"
    role.tags[_].Value == "Enabled"
}

allow if {
    count(deny) == 0
}

severity[result] if {
    count(deny) > 0
    high_severity_count := count([v | v := deny[_]; contains(v, "wildcard")])
    level := "CRITICAL" if high_severity_count > 0 else "HIGH"
    result := {
        "level": level,
        "violations": count(deny),
        "controls_affected": [
            "ISO 27001 A.5.15",
            "ISO 27001 A.5.16",
            "ISO 27001 A.5.18",
            "ISO 27701 6.2.1",
            "ISO 27701 6.2.2",
            "ISO 27701 6.2.3",
            "ISO 42001 6.1.3",
            "ISO 42001 6.1.4"
        ]
    }
}
