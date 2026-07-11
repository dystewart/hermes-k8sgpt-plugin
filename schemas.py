K8SGPT_ANALYZE = {
    "name": "k8sgpt_analyze",
    "description": (
        "Run K8sGPT deterministic Kubernetes/OpenShift analyzers and optionally "
        "explain the findings with Hermes' active model and credentials."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "description": "Optional namespace; prefer scoped analysis."
            },
            "filters": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional filters such as Pod, Service, Deployment."
            },
            "explain": {
                "type": "boolean",
                "default": True,
                "description": "Use Hermes ctx.llm to explain raw findings."
            },
            "include_raw": {
                "type": "boolean",
                "default": True
            },
            "include_kubernetes_docs": {
                "type": "boolean",
                "default": False
            }
        },
        "additionalProperties": False
    }
}

K8SGPT_FILTERS = {
    "name": "k8sgpt_filters",
    "description": "List available K8sGPT analyzers/filters.",
    "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
}

K8SGPT_STATUS = {
    "name": "k8sgpt_status",
    "description": "Report K8sGPT binary and version status.",
    "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
}

EXPLANATION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "severity": {
            "type": "string",
            "enum": ["none", "low", "medium", "high", "critical"]
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "resource": {"type": "string"},
                    "problem": {"type": "string"},
                    "evidence": {"type": "string"},
                    "likely_cause": {"type": "string"},
                    "recommended_action": {"type": "string"},
                    "verification": {"type": "string"}
                },
                "required": [
                    "resource", "problem", "evidence", "likely_cause",
                    "recommended_action", "verification"
                ],
                "additionalProperties": False
            }
        },
        "next_checks": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["summary", "severity", "findings", "next_checks"],
    "additionalProperties": False
}
