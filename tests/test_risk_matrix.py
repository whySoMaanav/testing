import pytest
from app.utils.risk_matrix import (
    calculate_risk,
    parse_level_value,
    RISK_SCORING_TABLE,
    LIKELIHOOD_OPTIONS,
    IMPACT_OPTIONS
)

def test_risk_scoring_matrix_all_cells():
    # Verify all 25 cells match expected formulas and levels
    for (l_val, i_val), (score, level) in RISK_SCORING_TABLE.items():
        res = calculate_risk(l_val, i_val)
        assert res["score"] == score
        assert res["level"] == level
        assert res["label"] == f"{level} ({score})"

def test_parse_level_value():
    assert parse_level_value("Remote (1)") == 1
    assert parse_level_value("Unlikely (2)") == 2
    assert parse_level_value("Possible (3)") == 3
    assert parse_level_value("Likely (4)") == 4
    assert parse_level_value("Virtually Certain (5)") == 5

    assert parse_level_value("Insignificant (1)") == 1
    assert parse_level_value("Minor (2)") == 2
    assert parse_level_value("Moderate (3)") == 3
    assert parse_level_value("High (4)") == 4
    assert parse_level_value("Very High (5)") == 5

    assert parse_level_value(4) == 4
    assert parse_level_value("3") == 3

def test_calculate_risk_with_strings():
    # Test specific cells from user prompt
    # Virtually Certain (5) x Very High (5) -> Very High (25)
    r1 = calculate_risk("Virtually Certain (5)", "Very High (5)")
    assert r1["score"] == 25
    assert r1["level"] == "Very High"

    # Likely (4) x Moderate (3) -> High (12)
    r2 = calculate_risk("Likely (4)", "Moderate (3)")
    assert r2["score"] == 12
    assert r2["level"] == "High"

    # Possible (3) x Insignificant (1) -> Very Low (3)
    r3 = calculate_risk("Possible (3)", "Insignificant (1)")
    assert r3["score"] == 3
    assert r3["level"] == "Very Low"

    # Unlikely (2) x Very High (5) -> Medium (10)
    r4 = calculate_risk("Unlikely (2)", "Very High (5)")
    assert r4["score"] == 10
    assert r4["level"] == "Medium"

    # Remote (1) x High (4) -> Low (4)
    r5 = calculate_risk("Remote (1)", "High (4)")
    assert r5["score"] == 4
    assert r5["level"] == "Low"

def test_unassessed_risk():
    res = calculate_risk(None, None)
    assert res["score"] is None
    assert res["level"] == "Unassessed"
