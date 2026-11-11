import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "config" / "competitor_ad_feature_schema_v1.json"
PLAN_PATH = ROOT / "docs" / "competitor_ad_interaction_analysis_plan.md"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_embedding_identity_integrity_binds_representation_and_derivative():
    embeddings = load_schema()["ledgers"]["embeddings"]

    assert embeddings["key"] == ["creative_sha256", "embedding_spec_id"]
    assert {
        "representation",
        "model_name",
        "model_revision",
        "preprocessing_revision",
        "masking_revision",
        "derivative_sha256",
    } <= set(embeddings["embedding_spec_identity_fields"])
    assert {"original_multimodal", "brand_masked_multimodal"} <= set(
        embeddings["representations"]
    )


def test_pairwise_keys_distinguish_occurrences_periods_and_embedding_spec():
    pairwise = load_schema()["ledgers"]["pairwise_interactions"]

    assert pairwise["key"] == [
        "pair_scope",
        "focal_occurrence_id",
        "comparison_occurrence_id",
        "embedding_spec_id",
        "information_cutoff_utc",
    ]
    required = {
        "focal_ad_id",
        "comparison_ad_id",
        "focal_period_id",
        "comparison_period_id",
        "information_cutoff_utc",
        "reference_window_start_utc",
        "reference_window_end_utc",
        "leave_one_out",
    }
    assert required <= set(pairwise["fields"])


def test_brand_period_positions_include_closed_period_and_information_cutoff():
    positions = load_schema()["ledgers"]["brand_period_positions"]

    assert "period_end" in positions["key"]
    assert "information_cutoff_utc" in positions["key"]
    assert "embedding_spec_id" in positions["key"]


def test_schema_has_typed_fields_unknown_vocabulary_and_auditable_provenance():
    schema = load_schema()

    assert schema["unknown_vocabulary"] == [
        "observed_present",
        "observed_absent",
        "unknown_not_observable",
        "unknown_not_coded",
        "not_applicable",
    ]
    assert schema["field_type_definitions"]
    for ledger in schema["ledgers"].values():
        assert ledger["schema_revision"]
        assert ledger["field_definitions"]
        assert all("type" in definition for definition in ledger["field_definitions"].values())
        assert set(ledger["key"]) | {"schema_revision"} <= set(ledger["required_fields"])
        assert ledger["additional_properties"] is False
    creative = schema["ledgers"]["creative_features"]
    assert {"evidence_links", "coder_provenance", "model_provenance"} <= set(
        creative["field_definitions"]
    )


def test_analysis_plan_forbids_focal_and_future_leakage():
    plan = PLAN_PATH.read_text().lower()

    assert "strictly prior own-brand and rival windows" in plan
    assert "leave-one-out contemporaneous benchmark" in plan
    assert "information cutoff" in plan
    assert "exclude the focal ad" in plan
    assert "future" in plan and "leakage" in plan