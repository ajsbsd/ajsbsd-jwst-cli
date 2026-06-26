"""Unit tests for simulation.figures."""
from pathlib import Path

import pytest

from simulation.figures import Figure, FigureRegistry

FIGURES_DIR = Path(__file__).parent.parent / "simulation" / "data" / "figures"

REQUIRED_FIELDS = {"id", "name", "role", "faction", "active_years", "traits", "stats", "decision_logic"}
REQUIRED_STATS = {"aggression", "pragmatism", "political_skill", "public_influence"}
VALID_FACTIONS = {"military", "political", "civilian", "media"}
VALID_DECISION_LOGIC = {"hawk", "dove", "pragmatist", "opportunist", "demagogue"}


class TestFigureRegistry:
    def test_loads_all_yaml_files(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        # Expect the 7 figures defined in the plan
        expected_ids = {"lemay", "mcnamara", "mccarthy", "truman", "eisenhower", "johnson", "reagan"}
        loaded_ids = set(registry.ids())
        assert expected_ids == loaded_ids, f"Missing: {expected_ids - loaded_ids}"

    def test_all_figures_have_required_fields(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        for figure in registry.all():
            assert figure.id, "id missing"
            assert figure.name, f"{figure.id}: name missing"
            assert figure.role, f"{figure.id}: role missing"
            assert figure.faction in VALID_FACTIONS, f"{figure.id}: invalid faction {figure.faction!r}"
            assert figure.decision_logic in VALID_DECISION_LOGIC, (
                f"{figure.id}: invalid decision_logic {figure.decision_logic!r}"
            )

    def test_all_figures_have_required_stats(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        for figure in registry.all():
            for stat in REQUIRED_STATS:
                assert stat in figure.stats, f"{figure.id}: missing stat {stat!r}"
                assert 0 <= figure.stats[stat] <= 100, (
                    f"{figure.id}.{stat} = {figure.stats[stat]} out of [0,100]"
                )

    def test_active_years_are_valid_range(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        for figure in registry.all():
            start, end = figure.active_years
            assert 1940 <= start <= 2000, f"{figure.id}: start year {start} out of expected range"
            assert start <= end, f"{figure.id}: active_years start > end"


class TestFigureActiveYears:
    def test_lemay_active_in_1950(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        lemay = registry.get("lemay")
        assert lemay.is_active(1950) is True

    def test_mccarthy_not_active_in_1947(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        mccarthy = registry.get("mccarthy")
        assert mccarthy.is_active(1947) is False

    def test_reagan_not_active_in_1960(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        reagan = registry.get("reagan")
        assert reagan.is_active(1960) is False

    def test_reagan_active_in_1985(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        reagan = registry.get("reagan")
        assert reagan.is_active(1985) is True

    def test_active_in_returns_correct_subset(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        active_1948 = {f.id for f in registry.active_in(1948)}
        # Only Truman and LeMay are active in 1948 (McCarthy starts 1950)
        assert "lemay" in active_1948
        assert "truman" in active_1948
        assert "mccarthy" not in active_1948
        assert "reagan" not in active_1948


class TestFigureRelationships:
    def test_lemay_hostile_to_mcnamara(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        lemay = registry.get("lemay")
        assert lemay.relationship_to("mcnamara") < 0

    def test_unknown_relationship_defaults_to_zero(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        lemay = registry.get("lemay")
        assert lemay.relationship_to("nobody") == 0


class TestFigureModifyStat:
    def test_modify_stat_positive(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        lemay = registry.get("lemay")
        original = lemay.current_stats["aggression"]
        lemay.modify_stat("aggression", 5)
        assert lemay.current_stats["aggression"] == min(100, original + 5)

    def test_modify_stat_clamp_upper(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        lemay = registry.get("lemay")
        lemay.modify_stat("aggression", 1000)
        assert lemay.current_stats["aggression"] == 100

    def test_modify_stat_clamp_lower(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        truman = registry.get("truman")
        truman.modify_stat("aggression", -1000)
        assert truman.current_stats["aggression"] == 0

    def test_modify_unknown_stat_raises(self):
        registry = FigureRegistry.load_all(FIGURES_DIR)
        lemay = registry.get("lemay")
        with pytest.raises(KeyError):
            lemay.modify_stat("nonexistent_stat", 5)
