from pathlib import Path
from . import schemas, tools

def register(ctx):
    ctx.register_tool(
        name="k8sgpt_analyze",
        toolset="k8sgpt",
        schema=schemas.K8SGPT_ANALYZE,
        handler=lambda args, **kwargs: tools.k8sgpt_analyze(ctx, args, **kwargs),
    )
    ctx.register_tool(
        name="k8sgpt_filters",
        toolset="k8sgpt",
        schema=schemas.K8SGPT_FILTERS,
        handler=lambda args, **kwargs: tools.k8sgpt_filters(args, **kwargs),
    )
    ctx.register_tool(
        name="k8sgpt_status",
        toolset="k8sgpt",
        schema=schemas.K8SGPT_STATUS,
        handler=lambda args, **kwargs: tools.k8sgpt_status(args, **kwargs),
    )

    skill = Path(__file__).parent / "skills" / "cluster-triage" / "SKILL.md"
    if skill.is_file():
        ctx.register_skill("cluster-triage", skill)
