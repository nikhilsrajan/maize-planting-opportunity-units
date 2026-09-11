"""Maize Planting Opportunity Units (MPOU) from daily temperature and precipitation."""
import numba
import numpy as np


@numba.njit
def _days_to_gdd(temp, t_base, required_gdd, max_tolerable_temp, min_tolerable_temp):
    """Return for each start day the days, start day included, until GDD exceeds required_gdd, else -1."""
    n = temp.shape[0]
    days = np.zeros(n, dtype=np.int64)
    for start in range(n):
        gdd = 0.0
        for i in range(start, n):
            if temp[i] >= max_tolerable_temp or temp[i] <= min_tolerable_temp:
                days[start] = -1
                break
            if temp[i] - t_base > 0:
                gdd += temp[i] - t_base
            days[start] += 1
            if gdd > required_gdd:
                break
        if gdd < required_gdd:
            days[start] = -1
    return days


@numba.njit
def _dry_run(prec, dryspell_threshold):
    """Return for each day the length of the run of dry days starting on it."""
    n = prec.shape[0]
    run = np.zeros(n + 1, dtype=np.int64)
    for i in range(n - 1, -1, -1):
        if prec[i] < dryspell_threshold:
            run[i] = run[i + 1] + 1
    return run[:n]


@numba.njit(parallel=True)
def _viable_planting_days(
    temp, prec, cumsum_prec, t_base, required_gdd_for_pollination, required_gdd_for_maturity,
    max_tolerable_temp, min_tolerable_temp, max_duration, min_total_prec_till_maturity,
    max_consecutive_dry_days, dryspell_threshold, days_to_germination, min_total_prec_for_germination,
):
    """Return the viable planting days and days to maturity, pixel by pixel."""
    n, height, width = temp.shape
    viable = np.zeros((n, height, width), dtype=np.bool_)
    days_to_maturity = np.empty((n, height, width), dtype=np.int64)
    for y in numba.prange(height):
        for x in range(width):
            d2p = _days_to_gdd(
                temp[:, y, x], t_base, required_gdd_for_pollination, max_tolerable_temp, min_tolerable_temp,
            )
            d2m = _days_to_gdd(
                temp[:, y, x], t_base, required_gdd_for_maturity, max_tolerable_temp, min_tolerable_temp,
            )
            dry = _dry_run(prec[:, y, x], dryspell_threshold)
            c = cumsum_prec[:, y, x]
            suitable = np.zeros(n, dtype=np.bool_)
            for t in range(n):
                p = t + d2p[t]
                m = t + d2m[t]
                suitable[t] = (
                    d2m[t] <= max_duration and d2m[t] != -1
                    and d2p[t] != -1 and p < n and dry[p] < max_consecutive_dry_days
                    and m < n and c[m] - c[t] >= min_total_prec_till_maturity
                )
            g = days_to_germination
            for t in range(n - g):
                viable[t, y, x] = suitable[t + g] and c[t + g] - c[t] > min_total_prec_for_germination
            days_to_maturity[:, y, x] = d2m
    return viable, days_to_maturity


def viable_planting_days(
    temp,
    prec,
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
):
    """Return which days of (time, y, x) daily mean temperature (°C) and precipitation (mm) are viable for planting, and the days to maturity from each day (-1 if never reached)."""
    return _viable_planting_days(
        temp, prec, prec.cumsum(axis=0), t_base, required_gdd_for_pollination, required_gdd_for_maturity,
        max_tolerable_temp, min_tolerable_temp, max_duration, min_total_prec_till_maturity,
        max_consecutive_dry_days, dryspell_threshold, days_to_germination, min_total_prec_for_germination,
    )


def summarize(viable, days_to_maturity, cutoff_index):
    """Return the count of viable days before cutoff_index and the mean days to maturity over all viable days, per pixel."""
    opportunity_days = viable[:cutoff_index].sum(axis=0).astype(np.uint16)
    season_length = days_to_maturity.astype(float)
    season_length[viable != 1] = np.nan
    return opportunity_days, np.nanmean(season_length, axis=0)


def _binify(x, edges):
    """Return bin i where edges[i] < x <= edges[i + 1], else 0."""
    binned = np.zeros(x.shape, dtype=np.uint8)
    for i in range(edges.shape[0] - 1):
        binned[(x > edges[i]) & (x <= edges[i + 1])] = i
    return binned


def zones(opportunity_days, season_length, n_bins=8, opportunity_max=3652, season_min=100, season_max=360):
    """Return uint16 zone codes season_bin * 100 + opportunity_bin, with bins numbered from 1."""
    opportunity_bin = _binify(opportunity_days, np.linspace(0, opportunity_max, n_bins + 1)) + 1
    season_bin = _binify(season_length, np.linspace(season_min, season_max, n_bins + 1)) + 1
    return season_bin.astype(np.uint16) * 100 + opportunity_bin
