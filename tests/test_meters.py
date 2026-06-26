"""Unit tests for simulation.meters."""
import pytest
from simulation.meters import GlobalMeters, METER_DEFINITIONS


class TestGlobalMetersInit:
    def test_all_meters_initialised(self):
        m = GlobalMeters()
        for name in METER_DEFINITIONS:
            assert name in m._values

    def test_starting_values_match_definitions(self):
        m = GlobalMeters()
        for name, (_, start) in METER_DEFINITIONS.items():
            assert m.get(name) == start, f"{name}: expected {start}, got {m.get(name)}"

    def test_previous_equals_initial_values(self):
        m = GlobalMeters()
        for name in METER_DEFINITIONS:
            assert m.trend(name) == 0


class TestUpdate:
    def test_positive_delta(self):
        m = GlobalMeters()
        m.update("sac_readiness", 10)
        assert m.get("sac_readiness") == 30  # 20 + 10

    def test_negative_delta(self):
        m = GlobalMeters()
        m.update("civilian_oversight", -5)
        assert m.get("civilian_oversight") == 80  # 85 - 5

    def test_clamp_upper(self):
        m = GlobalMeters()
        m.update("public_support", 1000)
        assert m.get("public_support") == 100

    def test_clamp_lower(self):
        m = GlobalMeters()
        m.update("escalation_risk", -1000)
        assert m.get("escalation_risk") == 0

    def test_unknown_meter_raises_key_error(self):
        m = GlobalMeters()
        with pytest.raises(KeyError):
            m.update("nonexistent_meter", 5)


class TestTrend:
    def test_trend_reflects_delta(self):
        m = GlobalMeters()
        m.update("escalation_risk", 20)
        assert m.trend("escalation_risk") == 20

    def test_snapshot_resets_trend(self):
        m = GlobalMeters()
        m.update("escalation_risk", 20)
        m.snapshot_previous()
        assert m.trend("escalation_risk") == 0

    def test_negative_trend(self):
        m = GlobalMeters()
        m.update("civilian_oversight", -15)
        assert m.trend("civilian_oversight") == -15


class TestSummary:
    def test_summary_contains_all_meters(self):
        m = GlobalMeters()
        summary = m.summary()
        for name in METER_DEFINITIONS:
            assert name in summary

    def test_summary_structure(self):
        m = GlobalMeters()
        summary = m.summary()
        for entry in summary.values():
            assert "value" in entry
            assert "trend" in entry
            assert "description" in entry


class TestCheck:
    def test_lt_true(self):
        m = GlobalMeters()
        assert m.check("escalation_risk", "lt", 50) is True

    def test_lt_false(self):
        m = GlobalMeters()
        assert m.check("civilian_oversight", "lt", 50) is False

    def test_gt_true(self):
        m = GlobalMeters()
        assert m.check("civilian_oversight", "gt", 50) is True

    def test_gte_boundary(self):
        m = GlobalMeters()
        # civilian_oversight starts at 85
        assert m.check("civilian_oversight", "gte", 85) is True

    def test_lte_boundary(self):
        m = GlobalMeters()
        assert m.check("sac_readiness", "lte", 20) is True

    def test_eq(self):
        m = GlobalMeters()
        assert m.check("sac_readiness", "eq", 20) is True

    def test_invalid_op_raises(self):
        m = GlobalMeters()
        with pytest.raises(ValueError):
            m.check("sac_readiness", "bad_op", 10)

    def test_unknown_meter_raises_key_error(self):
        m = GlobalMeters()
        with pytest.raises(KeyError):
            m.check("nonexistent", "lt", 10)
