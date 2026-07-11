---
name: cluster-triage
description: Diagnose Kubernetes and OpenShift failures using K8sGPT analyzers and Hermes-native explanations.
---

# K8sGPT cluster triage

Use `k8sgpt_analyze` for first-pass diagnosis of failing pods, controllers,
services, events, storage, scheduling, and namespace or cluster health.

- Scope to a namespace whenever possible.
- Use `explain=true` by default.
- K8sGPT performs deterministic analysis only.
- Hermes explains findings through its active model and credentials.
- Verify important conclusions against current resources, events, and logs.
- Never modify the cluster without explicit approval.
