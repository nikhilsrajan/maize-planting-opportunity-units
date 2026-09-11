"""Compute the published ERA5 Sub-Saharan Africa MPOU rasters from monthly ERA5 daily-statistics NetCDF files."""
import argparse
import functools
import multiprocessing
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import rioxarray  # noqa: F401  (registers the .rio accessor)
import shapely
import xarray as xr

import mpou

STARTDATE = '1994-01-01'
ENDDATE = '2024-12-01'
CUTOFFDATE = '2024-01-01'
N_BINS = 8
PARAMS = dict(
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


def load_month(filepath, nc_var, envelope, crs):
    """Return one monthly ERA5 file in °C or mm, longitudes in -180..180, clipped to the envelope."""
    data = xr.open_dataset(filepath)[nc_var]
    data = data - 273.15 if nc_var == 't2m' else data * 1000
    data.coords['longitude'] = (data.coords['longitude'] + 180) % 360 - 180
    data = data.sortby('longitude').rio.set_spatial_dims('longitude', 'latitude').rio.write_crs('epsg:4326')
    return data.rio.clip([envelope], crs, drop=True, all_touched=True)


def load_series(catalog, var, nc_var, envelope, crs):
    """Return the clipped daily series of one catalog variable from STARTDATE to ENDDATE as a (time, y, x) DataArray."""
    rows = catalog[catalog['var'] == var].sort_values(by='date')
    filepaths = rows[(rows['date'] >= STARTDATE) & (rows['date'] <= ENDDATE)]['filepath'].to_list()
    with multiprocessing.Pool() as pool:
        months = pool.map(functools.partial(load_month, nc_var=nc_var, envelope=envelope, crs=crs), filepaths)
    return xr.concat(months, dim='valid_time')


def write(array, like, filepath, tags, nodata=None):
    """Write a (y, x) array as a GeoTIFF on the grid of like, with tags."""
    data = xr.DataArray(
        array, coords={'latitude': like.latitude, 'longitude': like.longitude}, dims=('latitude', 'longitude'),
    )
    data = data.rio.set_spatial_dims('longitude', 'latitude').rio.write_crs('epsg:4326')
    if nodata is not None:
        data = data.rio.write_nodata(nodata)
    data.rio.to_raster(filepath, tags=tags)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', help='catalog.csv written by download_era5 (columns var, date, filepath)')
    parser.add_argument('region', help='region shapefile; the run covers its bounding box')
    parser.add_argument('outdir', help='folder for the three output GeoTIFFs')
    args = parser.parse_args()

    catalog = pd.read_csv(args.catalog)
    region = gpd.read_file(args.region)
    envelope = shapely.unary_union(region.geometry).envelope
    temp = load_series(catalog, '2m_temperature', 't2m', envelope, region.crs)
    prec = load_series(catalog, 'total_precipitation', 'tp', envelope, region.crs)
    cutoff_index = int(np.where(prec.valid_time.values == np.datetime64(CUTOFFDATE))[0][0])

    viable, days_to_maturity = mpou.viable_planting_days(temp.values, prec.values, **PARAMS)
    opportunity_days, season_length = mpou.summarize(viable, days_to_maturity, cutoff_index)
    zone_params = dict(n_bins=N_BINS, opportunity_max=cutoff_index // 3, season_min=100, season_max=360)
    zones = mpou.zones(opportunity_days, season_length, **zone_params)

    os.makedirs(args.outdir, exist_ok=True)
    tags = dict(PARAMS, startdate=STARTDATE, enddate=ENDDATE, cutoffdate=CUTOFFDATE)
    write(opportunity_days, temp, os.path.join(args.outdir, 'planting_opportunity_days.tif'), tags)
    write(season_length, temp, os.path.join(args.outdir, 'season_length.tif'), tags)
    write(zones, temp, os.path.join(args.outdir, f'zones_nbins={N_BINS}.tif'), dict(tags, **zone_params), nodata=0)


if __name__ == '__main__':
    main()
