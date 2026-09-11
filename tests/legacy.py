"""Frozen copy of the legacy CSU code (nh_crop_calendar) that mpou must reproduce: verbatim except rsutils prefixes and raster I/O."""
import sys

import numba
import numpy as np

csu = sys.modules[__name__]


@numba.njit()
def get_continuous_sum_1d(arr:np.ndarray, stop_value = 0, spot_fill:bool=True)->np.ndarray:
    continous_sum = np.zeros(arr.shape, dtype=arr.dtype)

    N = arr.shape[0]

    cur_sum = 0
    for i in numba.prange(1, N+1):
        inv_i = N - i
        if arr[inv_i] != stop_value:
            cur_sum += arr[inv_i]
            if inv_i > 0:
                if spot_fill:
                    if arr[inv_i - 1] == stop_value:
                        continous_sum[inv_i] = cur_sum
                else:
                    continous_sum[inv_i] = cur_sum
            else:
                continous_sum[inv_i] = cur_sum
        else:
            cur_sum = 0

    return continous_sum


@numba.njit()
def get_continuous_sum_2d(arr:np.ndarray, spot_fill:bool=True)->np.ndarray:
    n_samples, n_timestamps = arr.shape
    continuous_sums = np.zeros((n_samples, n_timestamps), dtype=arr.dtype)
    for i in numba.prange(n_samples):
        continuous_sums[i] = \
            get_continuous_sum_1d(arr=arr[i], spot_fill=spot_fill)
    return continuous_sums


def _flatten_2D(arr):
    """
    Flattens an N-D array to 2D array by keeping the
    last dimension untouched.

    Input dimension: (n_1, n_2, ..., n_n, n_t)
    Output dimenstion: (n_1 * n_2 * ... * n_n, n_t)
    """
    *n_rem, n_ts = arr.shape
    return arr.reshape((np.prod(n_rem), n_ts))


def get_continuous_sum(arr:np.ndarray, spot_fill:bool=True)->np.ndarray:
    """
    Expected arr.shape: (n0, n1, n2, ..., n_timestamps)
    Output shape: (n0, n1, n2, ..., n_timestamps)
    """
    org_shape = arr.shape
    arr_2D = _flatten_2D(arr=arr)
    continuous_sums = get_continuous_sum_2d(arr=arr_2D, spot_fill=spot_fill)
    return continuous_sums.reshape(org_shape)


@numba.njit(parallel=True)
def calculate_days_to_maturity_1d(
    temp_ts:np.ndarray,
    t_base:float,
    required_gdd:float,
    max_tolerable_temp:float,
    min_tolerable_temp:float,
):
    N = temp_ts.shape[0]
    days_to_maturity = np.zeros(shape=temp_ts.shape)
    gdd_at_maturity = np.zeros(shape=temp_ts.shape, dtype=float)

    for start_index in range(N):
        GDD_i = 0
        for iter_index in range(start_index, N):
            cur_temp = temp_ts[iter_index]
            if cur_temp >= max_tolerable_temp or cur_temp <= min_tolerable_temp:
                days_to_maturity[start_index] = -1
                gdd_at_maturity[start_index] = np.inf
                break
            if cur_temp - t_base > 0:
                GDD_i += cur_temp - t_base
            days_to_maturity[start_index] += 1
            gdd_at_maturity[start_index] = GDD_i
            if GDD_i > required_gdd:
                break
        if GDD_i < required_gdd:
            days_to_maturity[start_index] = -1

    return days_to_maturity, gdd_at_maturity


@numba.njit(parallel=True)
def calculate_days_to_maturity(
    temp_ts:np.ndarray,
    t_base:float,
    required_gdd:float,
    max_tolerable_temp:float,
    min_tolerable_temp:float,
):
    """
    temp_ts is a 3d array - (timestamps, height, width)
    """
    n_ts, height, width = temp_ts.shape

    temp_ts_2d = temp_ts.reshape(n_ts, height*width)
    N = height * width

    days_to_maturity_2d = np.zeros(shape = temp_ts_2d.shape)
    gdd_at_maturity_2d = np.zeros(shape = temp_ts_2d.shape, dtype=float)

    for i in numba.prange(N):
        days_to_maturity_2d[:, i], gdd_at_maturity_2d[:, i] = \
        calculate_days_to_maturity_1d(
            temp_ts = temp_ts_2d[:, i],
            t_base = t_base,
            required_gdd = required_gdd,
            max_tolerable_temp = max_tolerable_temp,
            min_tolerable_temp = min_tolerable_temp,
        )

    days_to_maturity = days_to_maturity_2d.reshape(n_ts, height, width)
    gdd_at_maturity = gdd_at_maturity_2d.reshape(n_ts, height, width)

    return days_to_maturity, gdd_at_maturity


@numba.njit(parallel=True)
def total_prec_in_days_to_maturity_1d(
    cumsum_prec_ts:np.ndarray,
    days_to_maturity_ts:np.ndarray,
):
    total_prec_in_d2m = np.full(shape=cumsum_prec_ts.shape, fill_value=np.nan)
    N = cumsum_prec_ts.shape[0]
    for start_index in numba.prange(N):
        d2m = days_to_maturity_ts[start_index]
        upto_index = d2m + start_index
        if upto_index < N and d2m != -1:
            total_prec_in_d2m[start_index] = cumsum_prec_ts[upto_index] - cumsum_prec_ts[start_index]
    return total_prec_in_d2m


@numba.njit(parallel=True)
def total_prec_in_days_to_maturity(cumsum_prec_ts:np.ndarray, days_to_maturity:np.ndarray):
    n_ts, height, width = cumsum_prec_ts.shape

    N = height * width

    cumsum_prec_ts_2d = cumsum_prec_ts.reshape(n_ts, N)
    days_to_maturity_2d = days_to_maturity.reshape(n_ts, N)
    total_prec_in_d2m_2d = np.full(shape=(n_ts, N), fill_value=np.nan)

    for i in numba.prange(N):
        total_prec_in_d2m_2d[:, i] = \
        total_prec_in_days_to_maturity_1d(
            cumsum_prec_ts = cumsum_prec_ts_2d[:, i],
            days_to_maturity_ts = days_to_maturity_2d[:, i]
        )

    total_prec_in_d2m = total_prec_in_d2m_2d.reshape(n_ts, height, width)

    return total_prec_in_d2m


@numba.njit(parallel=True)
def lookup_1d(
    value_arr:np.ndarray,
    shift_arr:np.ndarray,
):
    value_at_index_arr = np.full(shape=shift_arr.shape, fill_value=np.nan)
    N = shift_arr.shape[0]
    for start_index in numba.prange(N):
        shift = shift_arr[start_index]
        lookup_index = start_index + shift
        if lookup_index < N and shift != -1:
            value_at_index_arr[start_index] = value_arr[lookup_index]
    return value_at_index_arr


def lookup(
    value_arr:np.ndarray,
    shift_arr:np.ndarray,
):
    n_ts, height, width = shift_arr.shape

    N = height * width

    value_arr_2d = value_arr.reshape(n_ts, N)
    shift_arr_2d = shift_arr.reshape(n_ts, N)
    value_at_index_arr_2d = np.full(shape=(n_ts, N), fill_value=np.nan)

    for i in numba.prange(N):
        value_at_index_arr_2d[:, i] = \
        lookup_1d(
            value_arr = value_arr_2d[:, i],
            shift_arr = shift_arr_2d[:, i]
        )

    value_at_index_arr = value_at_index_arr_2d.reshape(n_ts, height, width)

    return value_at_index_arr


def shift_right(arr, n, fill_value=0):
    n_ts, height, width = arr.shape
    return np.concatenate([arr[n:], np.full(shape=(n, height, width), fill_value=fill_value)])


def updated_compute_csu(
    region_temp_data,
    region_prec_data,
    t_base,
    required_gdd_for_pollination,
    required_gdd_for_maturity,
    max_tolerable_temp,
    min_tolerable_temp,
    max_duration,
    min_total_prec_till_maturity,
    max_consecutive_dry_days,
    dryspell_threshold,
    days_to_germination,
    min_total_prec_for_germination,
):
    days_to_pollination, _ = \
    csu.calculate_days_to_maturity(
        temp_ts = region_temp_data.values,
        t_base = t_base,
        required_gdd = required_gdd_for_pollination,
        max_tolerable_temp = max_tolerable_temp,
        min_tolerable_temp = min_tolerable_temp,
    )

    days_to_maturity, _ = \
    csu.calculate_days_to_maturity(
        temp_ts = region_temp_data.values,
        t_base = t_base,
        required_gdd = required_gdd_for_maturity,
        max_tolerable_temp = max_tolerable_temp,
        min_tolerable_temp = min_tolerable_temp,
    )

    days_to_maturity[days_to_maturity == np.inf] = -1
    days_to_maturity = days_to_maturity.astype(int)

    days_to_pollination[days_to_pollination == np.inf] = -1
    days_to_pollination = days_to_pollination.astype(int)

    consecutive_dry_days = get_continuous_sum(
        (region_prec_data.values < dryspell_threshold).astype(int).swapaxes(0, -1), spot_fill = False,
    ).swapaxes(0, -1)

    consecutive_dry_days_at_pollination = \
    csu.lookup(
        value_arr = consecutive_dry_days.astype(float),
        shift_arr = days_to_pollination,
    )

    total_prec_in_days_to_maturity = \
    csu.total_prec_in_days_to_maturity(
        cumsum_prec_ts = region_prec_data.values.cumsum(axis=0),
        days_to_maturity = days_to_maturity,
    )

    suitable_days = np.zeros(shape=days_to_maturity.shape, dtype=np.uint8)
    suitable_days[np.where(
        (days_to_maturity <= max_duration)
        & (days_to_maturity != -1)
        & (consecutive_dry_days_at_pollination < max_consecutive_dry_days)
        & (total_prec_in_days_to_maturity >= min_total_prec_till_maturity)
    )] = 1

    total_prec_in_days_to_germination = \
    csu.total_prec_in_days_to_maturity(
        cumsum_prec_ts = region_prec_data.values.cumsum(axis=0),
        days_to_maturity = np.full(shape=days_to_maturity.shape, fill_value=days_to_germination, dtype=int),
    )

    final_suitability_days = shift_right(suitable_days, days_to_germination, 0) & (total_prec_in_days_to_germination > min_total_prec_for_germination)

    return final_suitability_days, \
        suitable_days, \
        days_to_maturity, \
        days_to_pollination, \
        total_prec_in_days_to_maturity, \
        total_prec_in_days_to_germination, \
        consecutive_dry_days


def summaries(final_suitability_days, days_to_maturity, cutoffindex):
    """Return the sum-suitable-days and mean-days-to-maturity rasters as running_sum_prec.py computed them."""
    sum_suitable_days = final_suitability_days[:cutoffindex].sum(axis=(0)).astype(np.uint16)

    days_to_maturity = days_to_maturity.astype(float)
    days_to_maturity[final_suitability_days != 1] = np.nan
    mean_days_to_maturity = np.nanmean(days_to_maturity, axis=0)

    return sum_suitable_days, mean_days_to_maturity


def binify(array, bin_checkpoints):
    binned_array = np.zeros(shape=array.shape, dtype=np.uint8)
    for i in range(bin_checkpoints.shape[0] - 1):
        binned_array[np.where((array > bin_checkpoints[i]) & (array <= bin_checkpoints[i+1]))] = i
    return binned_array


def csu_zones(ssd_data, mdm_data, NUM_BINS, N_DAYS_1994_2024_BY_3, MULTIPLIER=100):
    """Return the CSU raster as csu_validation.ipynb computed it and wrote it (uint16)."""
    binned_ssd_data = binify(
        array = ssd_data,
        bin_checkpoints = np.linspace(0, N_DAYS_1994_2024_BY_3, NUM_BINS + 1),
    ) + 1

    binned_mdm_data = binify(
        array = mdm_data,
        bin_checkpoints = np.linspace(100, 360, NUM_BINS + 1),
    ) + 1

    csu_data = binned_mdm_data.astype(float) * MULTIPLIER + binned_ssd_data.astype(float)

    return csu_data.astype(np.uint16)
