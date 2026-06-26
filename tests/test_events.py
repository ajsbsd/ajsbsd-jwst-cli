"""Unit tests for simulation.events."""
from pathlib import Path

import pytest

from simulation.events import (
    Event,
    EventEngine,
    Condition,
    evaluate_conditions,
    apply_outcomes,
)
from simulation.meters import GlobalMeters
from simulation.figures import FigureRegistry

EVENTS_DIR = Path(__file__).parent.parent / "simulation" / "data" / "events"
FIGURES_DIR = Path(__file__).parent.parent / "simulation" / "data" / "figures"


def make_registry() -> FigureRegistry:
    return FigureRegistry.load_all(FIGURES_DIR)


def make_meters() -> GlobalMeters:
    return GlobalMeters()


class TestEventEngineLoad:
    def test_loads_all_era_files(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        events = engine.all_events()
        assert len(events) >= 25, f"Expected >=25 events, got {len(events)}"

    def test_all_events_have_ids(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        ids = [e.id for e in engine.all_events()]
        assert len(ids) == len(set(ids)), "Duplicate event IDs detected"

    def test_all_events_have_valid_years(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        for event in engine.all_events():
            assert 1947 <= event.year <= 1991, (
                f"{event.id}: year {event.year} out of expected range"
            )

    def test_known_events_present(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        ids = {e.id for e in engine.all_events()}
        for expected_id in [
            "usaf_independence_1947",
            "sac_takeover_1948",
            "soviet_atomic_test_1949",
            "cuba_airstrikes_1962",  # wait — this is a divergence id, not an event
            "cuban_missile_crisis_1962",
            "rolling_thunder_begins_1965",
            "cold_war_ends_1991",
        ]:
            if expected_id == "cuba_airstrikes_1962":
                continue  # divergence id, not in event list
            assert expected_id in ids, f"Event {expected_id!r} not found"


class TestEvaluateConditions:
    def test_no_conditions_always_true(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        # usaf_independence_1947 has no conditions
        event = next(e for e in engine.all_events() if e.id == "usaf_independence_1947")
        meters = make_meters()
        registry = make_registry()
        assert evaluate_conditions(event, meters, registry, 1947) is True

    def test_figure_active_condition_passes(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        event = next(e for e in engine.all_events() if e.id == "sac_takeover_1948")
        meters = make_meters()
        registry = make_registry()
        # LeMay is active in 1948 and sac_readiness starts at 20 < 40
        assert evaluate_conditions(event, meters, registry, 1948) is True

    def test_figure_active_condition_fails_when_not_active(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        # reagan_buildup_1981 requires reagan active
        event = next(e for e in engine.all_events() if e.id == "reagan_buildup_1981")
        meters = make_meters()
        registry = make_registry()
        # Reagan is not active in 1947
        assert evaluate_conditions(event, meters, registry, 1947) is False

    def test_meter_condition_fails_when_not_met(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        event = next(e for e in engine.all_events() if e.id == "sac_takeover_1948")
        meters = make_meters()
        # Set sac_readiness above 40 so the lt condition fails
        meters.update("sac_readiness", 30)  # now 50
        registry = make_registry()
        assert evaluate_conditions(event, meters, registry, 1948) is False


class TestApplyOutcomes:
    def test_meter_outcomes_applied(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        event = next(e for e in engine.all_events() if e.id == "sac_takeover_1948")
        meters = make_meters()
        registry = make_registry()
        before_sac = meters.get("sac_readiness")
        apply_outcomes(event, meters, registry)
        assert meters.get("sac_readiness") == before_sac + 20

    def test_figure_stat_changes_applied(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        event = next(e for e in engine.all_events() if e.id == "sac_takeover_1948")
        meters = make_meters()
        registry = make_registry()
        lemay = registry.get("lemay")
        before_influence = lemay.current_stats["public_influence"]
        apply_outcomes(event, meters, registry)
        assert lemay.current_stats["public_influence"] == min(100, before_influence + 10)


class TestGetEligibleEvents:
    def test_returns_events_for_year(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        meters = make_meters()
        registry = make_registry()
        eligible = engine.get_eligible_events(1947, meters, registry)
        ids = {e.id for e in eligible}
        assert "usaf_independence_1947" in ids

    def test_does_not_return_wrong_year(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        meters = make_meters()
        registry = make_registry()
        eligible_1947 = engine.get_eligible_events(1947, meters, registry)
        ids = {e.id for e in eligible_1947}
        assert "sac_takeover_1948" not in ids

    def test_once_event_not_returned_after_firing(self):
        engine = EventEngine.load_eras(EVENTS_DIR)
        meters = make_meters()
        registry = make_registry()
        eligible = engine.get_eligible_events(1947, meters, registry)
        usaf_event = next(e for e in eligible if e.id == "usaf_independence_1947")
        engine.fire_event(usaf_event, meters, registry)
        # After firing, it should not appear again
        eligible_again = engine.get_eligible_events(1947, meters, registry)
        assert "usaf_independence_1947" not in {e.id for e in eligible_again}
