"""Tests for src/d_extend.py (paper D, post hoc extension, plan section 11).

Pure helpers are tested on synthetic values; the full run is tested against
the WHO files when they are present beside this repository.
Usage: python -I -m pytest tests/test_d_extend.py -q
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import d_extend as e                      # noqa: E402
import d_regimen as d                     # noqa: E402

HAVE_DATA = d.NOTIF.exists() and d.EXPEN.exists() and d.PROC.exists()


def test_summary_quartiles_and_share():
    s = e.summary([-0.5, -0.2, 0.1, -0.4, 0.3])
    assert s["n"] == 5 and s["median"] == -0.2
    assert s["q1"] == pytest.approx(-0.4) and s["q3"] == pytest.approx(0.1)
    assert s["share_falling"] == pytest.approx(3 / 5)
    assert e.summary([])["median"] is None


def test_by_group_flags_small_groups_and_unclassified():
    rows = [{"g": "A", "v": -0.1}] * 5 + [{"g": None, "v": 0.2}]
    out = e.by_group(rows, "g", "v")
    assert out["A"]["interpreted"] and not out["unclassified"]["interpreted"]


def test_quadrants_count_every_pair_once():
    pairs = [(-0.1, 0.2), (-0.1, -0.2), (0.1, 0.2), (0.1, -0.2), (-0.3, 0.0)]
    q = e.quadrants(pairs)
    assert sum(q.values()) == len(pairs)
    assert q == {"cost_down_patients_up": 1, "cost_down_patients_down": 2,
                 "cost_up_patients_up": 1, "cost_up_patients_down": 1}


@pytest.mark.parametrize("spend,patients,word", [
    (-0.4, -0.1, "savings not visibly reinvested"),
    (-0.4, 0.0, "savings not visibly reinvested"),
    (-0.4, 0.1, "numbers treated rose while total spending fell"),
    (0.2, -0.1, "total spending rose")])
def test_verdict_wording_is_the_pre_stated_one(spend, patients, word):
    assert e.verdict(spend, patients) == word


def test_decomposition_shares_add_up():
    r = e.decomposition((2000.0, 1200.0), (1000.0, 900.0))
    assert r["change_total"] == pytest.approx(-900.0)
    assert r["drug_share_of_change"] == pytest.approx(800 / 900)
    assert r["mostly_drugs"] is True
    assert r["relative_programme"] == pytest.approx(-0.1)
    assert e.decomposition((1000.0, 900.0), (1000.0, 800.0))["mostly_drugs"] is False


def test_zero_reads_as_missing(monkeypatch):
    monkeypatch.setattr(d, "table", lambda p: {("XXX", 2019): {"exp_mdrmgt": "0"}})
    assert e.amount("XXX", 2019, "exp_mdrmgt") is None


@pytest.mark.skipif(not HAVE_DATA, reason="WHO files not beside this repository")
class TestOnTheData:
    R, rows = e.results() if HAVE_DATA else ({}, [])

    def test_same_panel_and_deflator_as_section_9(self):
        for which in ("sld", "cpp"):
            dist = self.R[which]["distribution"]
            assert dist["check_median_matches_section_9"]
            assert dist["all_real"]["n"] == d.balanced(which)["n"]
            assert self.R[which]["timing"]["figure_panel_equals_balanced_panel"]

    def test_subgroups_partition_the_panel(self):
        for which in ("sld", "cpp"):
            dist = self.R[which]["distribution"]
            n = dist["all_real"]["n"]
            assert sum(g["n"] for g in dist["by_region"].values()) == n
            assert sum(g["n"] for g in dist["by_income"].values()) == n

    def test_timing_matches_d_regimen(self):
        for which in ("sld", "cpp"):
            assert self.R[which]["timing"]["share_by_2021"] == pytest.approx(d.fall_before_guideline(which))

    def test_totals_are_internally_consistent(self):
        T = self.R["sld"]["treated"]
        st, tot = T["started"], T["total_real_sld"]
        assert T["change_pooled_per_patient"] == pytest.approx((tot[2024] / st[2024]) / (tot[2019] / st[2019]) - 1)
        assert sum(T["quadrants"].values()) == T["n"]

    def test_composition_panel_is_inside_the_drug_panel(self):
        comp = {r["iso3"] for r in self.rows if r["programme_change_real"] != ""}
        drug = {r["iso3"] for r in self.rows if r["sld_change_real"] != ""}
        assert comp <= drug and len(comp) == self.R["composition"]["n"]

    def test_committed_outputs_equal_a_fresh_run(self):
        saved = json.loads((e.OUT / "results.json").read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(e.jsonable(self.R), sort_keys=True))
        assert saved == fresh
        with (e.OUT / "country_changes.csv").open(encoding="utf-8") as f:
            assert len(list(csv.DictReader(f))) == len(self.rows)

    def test_no_nan(self):
        bad = []

        def walk(x, path=""):
            if isinstance(x, dict):
                for k, v in x.items():
                    walk(v, f"{path}/{k}")
            elif isinstance(x, (list, tuple)):
                for i, v in enumerate(x):
                    walk(v, f"{path}/{i}")
            elif isinstance(x, float) and math.isnan(x):
                bad.append(path)
        walk(self.R)
        assert not bad, bad
