from types import SimpleNamespace

import numpy as np
import pytest

import legacy
import mpou

PUBLISHED = dict(
    t_base=8,
    required_gdd_for_pollination=842,
    required_gdd_for_maturity=2400,
    max_tolerable_temp=45,
    min_tolerable_temp=0,
    max_duration=500,
    min_total_prec_till_maturity=450,
    max_consecutive_dry_days=5,
    dryspell_threshold=1,
    days_to_germination=3,
    min_total_prec_for_germination=20,
)


def weather(n, seed, dtype=np.float32):
    """Return seasonal random daily temperature (°C) and precipitation (mm) cubes of shape (n, 3, 4)."""
    rng = np.random.default_rng(seed)
    season = np.sin(2 * np.pi * np.arange(n) / 365)[:, None, None]
    temp = 22 + 8 * season + rng.normal(0, 3, (n, 3, 4))
    prec = (rng.random((n, 3, 4)) < 0.5 + 0.3 * season) * rng.exponential(10, (n, 3, 4))
    return temp.astype(dtype), prec.astype(dtype)


def assert_matches_legacy(temp, prec, cutoff_index, **params):
    """Assert every mpou output equals the legacy result on the same cubes, and return mpou's outputs."""
    viable, days_to_maturity = mpou.viable_planting_days(temp, prec, **params)
    opportunity_days, season_length = mpou.summarize(viable, days_to_maturity, cutoff_index)
    zones = mpou.zones(opportunity_days, season_length, opportunity_max=cutoff_index // 3)

    final, _, legacy_days_to_maturity, *_ = legacy.updated_compute_csu(
        SimpleNamespace(values=temp), SimpleNamespace(values=prec), **{**PUBLISHED, **params},
    )
    legacy_sum, legacy_mean = legacy.summaries(final, legacy_days_to_maturity, cutoff_index)
    legacy_zones = legacy.csu_zones(legacy_sum, legacy_mean, NUM_BINS=8, N_DAYS_1994_2024_BY_3=cutoff_index // 3)

    assert viable.dtype == bool
    np.testing.assert_array_equal(viable, final)
    np.testing.assert_array_equal(days_to_maturity, legacy_days_to_maturity, strict=True)
    np.testing.assert_array_equal(opportunity_days, legacy_sum, strict=True)
    np.testing.assert_array_equal(season_length, legacy_mean, strict=True)
    np.testing.assert_array_equal(zones, legacy_zones, strict=True)
    return viable, days_to_maturity, zones


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_normal(dtype):
    viable, _, _ = assert_matches_legacy(*weather(730, seed=0, dtype=dtype), cutoff_index=365)
    assert 0 < viable.mean() < 1


def test_temperature_out_of_range():
    temp, prec = weather(730, seed=1)
    temp[200] = 45
    temp[400, :, :2] = 0
    temp[500] = 50
    temp[600, 1] = -5
    _, days_to_maturity, _ = assert_matches_legacy(temp, prec, cutoff_index=365)
    assert (days_to_maturity[199] == -1).all()
    assert (days_to_maturity[399, :, :2] == -1).all()


def test_all_dry():
    temp, prec = weather(730, seed=2)
    viable, _, zones = assert_matches_legacy(temp, np.zeros_like(prec), cutoff_index=365)
    assert not viable.any()
    assert (zones == 101).all()


def test_maturity_past_series_end():
    temp = np.full((200, 2, 2), 28, dtype=np.float32)
    prec = np.full((200, 2, 2), 10, dtype=np.float32)
    viable, days_to_maturity, _ = assert_matches_legacy(temp, prec, cutoff_index=150)
    assert (days_to_maturity[:80] == 121).all()
    assert (days_to_maturity[80] == 120).all()
    assert (days_to_maturity[81:] == -1).all()
    assert viable[:76].all() and not viable[76:].any()


def test_bin_overflow():
    opportunity_days = np.array([[0, 1, 456, 457, 2000, 3652, 3653, 9000]], dtype=np.uint16)
    season_length = np.array([[np.nan, 100, 100.5, 132.5, 200, 360, 360.5, -1]])
    zones = mpou.zones(opportunity_days, season_length)
    legacy_zones = legacy.csu_zones(opportunity_days, season_length, NUM_BINS=8, N_DAYS_1994_2024_BY_3=3652)
    np.testing.assert_array_equal(zones, legacy_zones, strict=True)
    np.testing.assert_array_equal(zones, [[101, 101, 101, 102, 405, 808, 101, 101]])
