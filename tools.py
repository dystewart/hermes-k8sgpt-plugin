from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any

from .schemas import EXPLANATION_SCHEMA

K8SGPT_BIN = os.getenv("K8SGPT_BIN", "/opt/data/.local/bin/k8sgpt")
K8SGPT_TIMEOUT = int(os.getenv("K8SGPT_TIMEOUT", "180"))
K8SGPT_MAX_OUTPUT_BYTES = int(os.getenv("K8SGPT_MAX_OUTPUT_BYTES", "2097152"))

_NAMESPACE_RE = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")
_FILTER_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _dump(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _namespace(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("namespace must be a string")
    value = value.strip()
    if not value:
        return None
    if len(value) > 63 or not _NAMESPACE_RE.fullmatch(value):
        raise ValueError(f"invalid Kubernetes namespace: {value!r}")
    return value


def _filters(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("filters must be an array")
    cleaned = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError("every filter must be a string")
        item = item.strip()
        if item:
            if not _FILTER_RE.fullmatch(item):
                raise ValueError(f"invalid K8sGPT filter: {item!r}")
            cleaned.append(item)
    return cleaned


def _run(arguments: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(
            [K8SGPT_BIN, *arguments],
            capture_output=True,
            text=True,
            timeout=K8SGPT_TIMEOUT,
            check=False,
            env=os.environ.copy(),
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "error": f"K8sGPT binary not found at {K8SGPT_BIN}"
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"K8sGPT timed out after {K8SGPT_TIMEOUT} seconds"
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    stdout = result.stdout or ""
    if len(stdout.encode("utf-8", errors="replace")) > K8SGPT_MAX_OUTPUT_BYTES:
        return {"ok": False, "error": "K8sGPT output exceeded safety limit"}

    output: Any = None
    if stdout.strip():
        try:
            output = json.loads(stdout)
        except json.JSONDecodeError:
            output = stdout.strip()

    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "command": arguments,
        "output": output,
        "stderr": (result.stderr or "").strip() or None
    }


def _explain(ctx, raw: Any, namespace: str | None) -> dict[str, Any]:
    scope = f"namespace {namespace}" if namespace else "the cluster"
    result = ctx.llm.complete_structured(
        instructions=(
            f"Explain these deterministic K8sGPT findings for {scope}. "
            "Do not invent resources or evidence. Separate observations from "
            "inference, rank severity conservatively, and provide safe "
            "verification steps. Do not claim changes were applied."
        ),
        input=[{
            "type": "text",
            "text": json.dumps(raw, ensure_ascii=False)
        }],
        json_schema=EXPLANATION_SCHEMA,
        schema_name="k8sgpt.analysis",
        purpose="k8sgpt.explain",
        temperature=0.0,
        max_tokens=1800,
        timeout=180,
    )

    return {
        "ok": result.parsed is not None,
        "provider": result.provider,
        "model": result.model,
        "explanation": result.parsed,
        "raw_model_output": None if result.parsed is not None else result.text,
        "audit": result.audit,
    }


def k8sgpt_analyze(ctx, args: dict, **kwargs) -> str:
    try:
        namespace = _namespace(args.get("namespace"))
        filters = _filters(args.get("filters"))
        explain = bool(args.get("explain", True))
        include_raw = bool(args.get("include_raw", True))
        include_docs = bool(args.get("include_kubernetes_docs", False))

        command = ["analyze", "--output=json"]
        if namespace:
            command.append(f"--namespace={namespace}")
        if filters:
            command.append(f"--filter={','.join(filters)}")
        if include_docs:
            command.append("--with-doc")

        raw = _run(command)
        if not raw.get("ok"):
            return _dump({"ok": False, "raw_analysis": raw})

        response: dict[str, Any] = {
            "ok": True,
            "scope": {"namespace": namespace, "filters": filters}
        }
        if include_raw:
            response["raw_analysis"] = raw
        if explain:
            response["hermes_explanation"] = _explain(
                ctx, raw.get("output"), namespace
            )
        return _dump(response)
    except Exception as exc:
        return _dump({"ok": False, "error": str(exc)})


def k8sgpt_filters(args: dict, **kwargs) -> str:
    return _dump(_run(["filters", "list"]))


def k8sgpt_status(args: dict, **kwargs) -> str:
    version = _run(["version"])
    return _dump({
        "ok": bool(version.get("ok")),
        "binary": K8SGPT_BIN,
        "k8sgpt_ai_backend_required": False,
        "explanation_backend": "Hermes ctx.llm active provider/model",
        "version": version
    })
