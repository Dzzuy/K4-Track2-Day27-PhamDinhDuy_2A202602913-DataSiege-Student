"""
Your defense. Implement register(ctx) and a handler per event type.
See ../README.md for the full interface + toolkit reference, and
../RULES.md before you start.
"""
from api import Verdict


def register(ctx):
    ctx.on("data_batch", check_data_batch)
    ctx.on("contract_checkpoint", check_contract_checkpoint)
    ctx.on("lineage_run", check_lineage_run)
    ctx.on("feature_materialization", check_feature_materialization)
    ctx.on("embedding_batch", check_embedding_batch)


def check_data_batch(payload, ctx):
    # Completed requirement: inspect each batch against the published baseline.
    profile = ctx.tools.batch_profile(payload["batch_id"])
    if "error" in profile:
        return Verdict(alert=False, pillar="checks", reason=profile["error"])
    bounds = ctx.baseline
    checks = (
        (profile["row_count"] < bounds["row_count_min"] or profile["row_count"] > bounds["row_count_max"], "row count"),
        (profile["null_rate"]["customer_id"] > bounds["null_rate_max"], "customer ID null rate"),
        (profile["mean_amount"] < bounds["mean_amount_min"] or profile["mean_amount"] > bounds["mean_amount_max"], "mean amount"),
        (profile["staleness_min"] > bounds["staleness_min_max"], "staleness"),
    )
    for failed, reason in checks:
        if failed:
            return Verdict(alert=True, pillar="checks", reason=reason)
    return Verdict(alert=False, pillar="checks")


def check_contract_checkpoint(payload, ctx):
    # Completed requirement: check declared contract and freshness.
    diff = ctx.tools.contract_diff(payload["contract_id"], payload["checkpoint_batch_id"])
    if "error" in diff:
        return Verdict(alert=False, pillar="contracts", reason=diff["error"])
    if diff["violations"]:
        return Verdict(alert=True, pillar="contracts", reason=", ".join(diff["violations"]))
    sla = payload.get("declared_sla", {}).get("freshness_min", ctx.baseline["freshness_delay_max_min"])
    if diff["freshness_delay_min"] > max(sla, ctx.baseline["freshness_delay_max_min"]):
        return Verdict(alert=True, pillar="contracts", reason="freshness delay")
    return Verdict(alert=False, pillar="contracts")


def check_lineage_run(payload, ctx):
    # Completed requirement: detect broken dependencies, unused output and slow runs.
    graph = ctx.tools.lineage_graph_slice(payload["run_id"])
    if "error" in graph:
        return Verdict(alert=False, pillar="lineage", reason=graph["error"])
    if graph["actual_downstream_count"] == 0:
        return Verdict(alert=True, pillar="lineage", reason="orphan output")
    if not {"raw.orders", "raw.customers"}.issubset(graph["actual_upstream"]):
        return Verdict(alert=True, pillar="lineage", reason="missing upstream")
    if graph["duration_ms"] > ctx.baseline["lineage_duration_ms_max"]:
        return Verdict(alert=True, pillar="lineage", reason="slow run")
    return Verdict(alert=False, pillar="lineage")


def check_feature_materialization(payload, ctx):
    # Completed requirement: compare serving and training feature distributions.
    drift = ctx.tools.feature_drift(payload["feature_view"], payload["batch_id"])
    if "error" in drift:
        return Verdict(alert=False, pillar="ai_infra", reason=drift["error"])
    if drift["mean_shift_sigma"] > 0.65:
        return Verdict(alert=True, pillar="ai_infra", reason="feature drift")
    return Verdict(alert=False, pillar="ai_infra")


def check_embedding_batch(payload, ctx):
    # Completed requirement: check vector drift and corpus age.
    drift = ctx.tools.embedding_drift(payload["corpus"], payload["chunk_batch_id"])
    if "error" in drift:
        return Verdict(alert=False, pillar="ai_infra", reason=drift["error"])
    if drift["centroid_shift"] > ctx.baseline["embedding_centroid_shift_max"]:
        return Verdict(alert=True, pillar="ai_infra", reason="embedding drift")
    if drift["avg_doc_age_days"] > ctx.baseline["corpus_avg_doc_age_days_max"]:
        return Verdict(alert=True, pillar="ai_infra", reason="stale corpus")
    return Verdict(alert=False, pillar="ai_infra")
