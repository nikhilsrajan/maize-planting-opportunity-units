"""Write the ERA5 data behind the report figures: climate maps and the Malawi planting examples."""
import argparse
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import xarray as xr

import mpou
from examples import era5_sub_saharan_africa as era5

PIXEL = dict(longitude=33.75, latitude=-11.75)
PIXEL_START, PIXEL_END = '2021-05-26', '2022-05-25'
MALAWI = dict(longitude=slice(32.75, 36.0), latitude=slice(-9.25, -17.25))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', help='catalog.csv written by download_era5 (columns var, date, filepath)')
    parser.add_argument('region', help='region shapefile; the run covers its bounding box')
    parser.add_argument('outdir', help='folder for the figure data, e.g. report/data')
    args = parser.parse_args()

    catalog = pd.read_csv(args.catalog)
    region = gpd.read_file(args.region)
    envelope = shapely.unary_union(region.geometry).envelope
    temp = era5.load_series(catalog, '2m_temperature', 't2m', envelope, region.crs)
    prec = era5.load_series(catalog, 'total_precipitation', 'tp', envelope, region.crs)

    os.makedirs(args.outdir, exist_ok=True)
    tags = dict(startdate=era5.STARTDATE, enddate=era5.ENDDATE)
    n_years = temp.sizes['valid_time'] / 365.25
    era5.write(temp.mean('valid_time').values, temp, os.path.join(args.outdir, 'mean_temperature.tif'), tags)
    era5.write(
        prec.sum('valid_time').values / n_years, temp, os.path.join(args.outdir, 'mean_annual_precipitation.tif'), tags,
    )

    temp, prec = temp.sel(**MALAWI), prec.sel(**MALAWI)
    viable, days_to_maturity = mpou.viable_planting_days(temp.values, prec.values, **era5.PARAMS)
    dates = pd.DatetimeIndex(temp.valid_time.values)
    cutoff_index = int(np.where(dates == pd.Timestamp(era5.CUTOFFDATE))[0][0])

    share = xr.DataArray(
        viable[:cutoff_index],
        coords={'valid_time': dates[:cutoff_index], 'latitude': temp.latitude.values, 'longitude': temp.longitude.values},
        dims=('valid_time', 'latitude', 'longitude'),
    ).groupby('valid_time.dayofyear').mean().astype('float32')
    share = share.rio.set_spatial_dims('longitude', 'latitude').rio.write_crs('epsg:4326')
    share.rio.to_raster(os.path.join(args.outdir, 'malawi_viable_share_by_day_of_year.tif'), tags=dict(tags, **era5.PARAMS))

    y = int(np.abs(temp.latitude.values - PIXEL['latitude']).argmin())
    x = int(np.abs(temp.longitude.values - PIXEL['longitude']).argmin())
    p = prec.values[:, y, x]
    d2m = days_to_maturity[:, y, x]
    cumsum = p.cumsum()
    start = np.arange(p.size)
    ok = (d2m != -1) & (start + d2m < p.size)
    rain_to_maturity = np.full(p.size, np.nan)
    rain_to_maturity[ok] = cumsum[start[ok] + d2m[ok]] - cumsum[start[ok]]
    pixel = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'temperature': temp.values[:, y, x],
        'precipitation': p,
        'days_to_maturity': d2m,
        'rain_to_maturity': rain_to_maturity,
        'viable': viable[:, y, x].astype(int),
    })
    pixel = pixel[(pixel['date'] >= PIXEL_START) & (pixel['date'] <= PIXEL_END)]
    pixel.to_csv(os.path.join(args.outdir, 'malawi_pixel.csv'), index=False, float_format='%.4f')
    print(pixel.head(10).to_string(index=False))


if __name__ == '__main__':
    main()
