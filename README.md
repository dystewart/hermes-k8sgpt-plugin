# Hermes K8sGPT Plugin

Native Hermes plugin repository for:

```text
https://github.com/dystewart/hermes-k8sgpt-plugin.git
```

The plugin runs K8sGPT deterministic analyzers and uses Hermes `ctx.llm` for
explanations. K8sGPT does not need a separate API key or AI backend.

## Install on OpenShift

```bash
oc apply -f openshift/01-rbac.yaml

oc patch deployment hermes-agent   -n hermes   --type=strategic   --patch-file openshift/02-deployment-plugin-install.yaml

oc rollout restart deployment/hermes-agent -n hermes
oc rollout status deployment/hermes-agent -n hermes
```

The Deployment patch adds two init containers:

1. `install-k8sgpt` copies the K8sGPT binary into a shared volume.
2. `install-k8sgpt-plugin` runs:

```bash
hermes plugins install   https://github.com/dystewart/hermes-k8sgpt-plugin.git   --enable
```

The plugin is installed into the shared `HERMES_HOME=/opt/data` PVC before
the main Hermes process starts.

## Verify

```bash
oc exec -n hermes deployment/hermes-agent -c hermes --   hermes plugins list

oc exec -n hermes deployment/hermes-agent -c hermes --   /opt/data/.local/bin/k8sgpt version
```

Inspect initialization:

```bash
POD=$(oc get pod -n hermes   -l app=hermes-agent,component=agent   -o jsonpath='{.items[0].metadata.name}')

oc logs -n hermes "${POD}" -c install-k8sgpt
oc logs -n hermes "${POD}" -c install-k8sgpt-plugin
```

## Registered tools

- `k8sgpt_analyze`
- `k8sgpt_filters`
- `k8sgpt_status`
