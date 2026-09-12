"""Draw the report figures from the repo maps, report/data and the HarvestStat Africa and GYGA files."""
import argparse
import os

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import rasterio.features
import rasterio.mask

MAPS = 'maps/era5_sub_saharan_africa'
DATA = 'report/data'
FIGURES = 'report/figures'
COUNTRIES = [
    'Uganda', 'Burundi', 'Ethiopia', 'Kenya', 'Sudan', 'Rwanda', 'DRC', 'Malawi', 'Mozambique', 'Tanzania', 'Zambia',
    'Zimbabwe',
]
START_YEAR = 2016
ZONE_RANGE = dict(cmap='turbo', vmin=101, vmax=808)


def save(fig, name):
    """Save a figure into FIGURES and close it."""
    fig.savefig(os.path.join(FIGURES, name), dpi=150)
    plt.close(fig)


def map_panel(ax, path, region, title, label, **imshow):
    """Draw band 1 of a raster inside the region outline, with a colorbar spanning the 1st to 99th percentile."""
    with rasterio.open(path) as src:
        data = src.read(1).astype(float)
        data[rasterio.features.geometry_mask(region.geometry, data.shape, src.transform)] = np.nan
        extent = (src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top)
    vmin, vmax = np.nanpercentile(data, [1, 99])
    imshow = dict(dict(vmin=vmin, vmax=vmax), **imshow)
    image = ax.imshow(data, extent=extent, interpolation='nearest', **imshow)
    region.boundary.plot(ax=ax, color='black', linewidth=0.3)
    ax.set_title(title)
    ax.set_axis_off()
    fig = ax.get_figure()
    fig.colorbar(image, ax=ax, orientation='horizontal', shrink=0.8, pad=0.02, label=label, extend='both')


def majority(path, geometry, nodata):
    """Return the most common raster value inside geometry (the smallest on ties), or None if no pixel centre is inside."""
    with rasterio.open(path) as src:
        values, _ = rasterio.mask.mask(src, [geometry], crop=True, nodata=nodata)
    values = values[values != nodata]
    if values.size == 0:
        return None
    uniques, counts = np.unique(values, return_counts=True)
    return uniques[counts.argmax()]


def evaluation(hvstat_csv, hvstat_gpkg, gyga):
    """Return maize yields per admin-1 region and year with the region's majority zone and GYGA climate zone, and the regions."""
    regions = gpd.read_file(hvstat_gpkg).dissolve(by=['ADMIN0', 'ADMIN1']).reset_index()
    regions['zone'] = [majority(os.path.join(MAPS, 'zones_nbins=8.tif'), g, 65535) for g in regions.geometry]
    regions['gyga'] = [majority(gyga, g, 2147483647) for g in regions.geometry]
    regions = regions.dropna(subset=['zone', 'gyga']).astype({'zone': int, 'gyga': int})

    yields = pd.read_csv(hvstat_csv, low_memory=False)
    yields = yields.groupby(['country', 'admin_1', 'product', 'planting_year'])[['area', 'production']].sum().reset_index()
    yields = yields[
        yields['country'].isin(COUNTRIES) & (yields['product'] == 'Maize') & (yields['area'] > 0)
        & (yields['planting_year'] >= START_YEAR)
    ]
    yields['yield'] = yields['production'] / yields['area']
    table = yields.merge(
        regions[['ADMIN0', 'ADMIN1', 'zone', 'gyga']], left_on=['country', 'admin_1'], right_on=['ADMIN0', 'ADMIN1'],
    ).dropna()
    return table, regions


def climate(region):
    """Map the ERA5 mean temperature and mean annual precipitation."""
    fig, axs = plt.subplots(1, 2, figsize=(12, 6.1), constrained_layout=True)
    map_panel(axs[0], os.path.join(DATA, 'mean_temperature.tif'), region, 'Mean temperature, 1994–2024', '°C', cmap='magma')
    map_panel(
        axs[1], os.path.join(DATA, 'mean_annual_precipitation.tif'), region, 'Mean annual precipitation, 1994–2024',
        'mm per year', cmap='YlGnBu',
    )
    save(fig, 'climate.png')


def layers(region):
    """Map planting opportunity days and season length."""
    fig, axs = plt.subplots(1, 2, figsize=(12, 6.1), constrained_layout=True)
    map_panel(
        axs[0], os.path.join(MAPS, 'planting_opportunity_days.tif'), region, 'Planting opportunity days, 1994–2023',
        'days', cmap='viridis',
    )
    map_panel(axs[1], os.path.join(MAPS, 'season_length.tif'), region, 'Season length, 1994–2024', 'days', cmap='viridis')
    save(fig, 'layers.png')


def zones(region, regions):
    """Map the pixel zones and the majority zone of each selected admin-1 region."""
    fig, axs = plt.subplots(1, 2, figsize=(12, 6.1), constrained_layout=True)
    map_panel(axs[0], os.path.join(MAPS, 'zones_nbins=8.tif'), region, 'Zones, 8 bins', 'zone code', **ZONE_RANGE)
    regions.plot(ax=axs[1], column='zone', edgecolor='white', linewidth=0.2, **ZONE_RANGE)
    region.boundary.plot(ax=axs[1], color='black', linewidth=0.3)
    axs[1].set_title(f'Majority zone of {len(regions)} admin-1 regions')
    axs[1].set_axis_off()
    save(fig, 'zones.png')


def malawi_pixel():
    """Plot the Malawi pixel's weather, days to maturity and rain to maturity, shading viable planting days."""
    df = pd.read_csv(os.path.join(DATA, 'malawi_pixel.csv'), parse_dates=['date'])
    fig, axs = plt.subplots(2, 1, figsize=(9, 7), sharex=True, constrained_layout=True)
    panels = [
        (axs[0], 'temperature', 'daily mean temperature (°C)', 'precipitation', 'daily precipitation (mm)'),
        (axs[1], 'days_to_maturity', 'days to maturity', 'rain_to_maturity', 'rain to maturity (mm)'),
    ]
    for ax, left, left_label, right, right_label in panels:
        ax.fill_between(
            df['date'], 0, 1, where=df['viable'] == 1, step='mid', color='tab:green', alpha=0.15,
            transform=ax.get_xaxis_transform(), label='viable planting day',
        )
        ax.plot(df['date'], df[left], color='tab:blue')
        ax.set_ylabel(left_label, color='tab:blue')
        twin = ax.twinx()
        twin.plot(df['date'], df[right], color='tab:red')
        twin.set_ylabel(right_label, color='tab:red')
    axs[0].legend(loc='upper left')
    axs[0].set_title('ERA5 pixel at 33.75° E, 11.75° S (Malawi)')
    save(fig, 'malawi_pixel.png')


def malawi_day_of_year(malawi):
    """Plot, for each Malawi pixel, the share of years in which each day of year was a viable planting day."""
    with rasterio.open(os.path.join(DATA, 'malawi_viable_share_by_day_of_year.tif')) as src:
        share = src.read()
        outside = rasterio.features.geometry_mask(malawi.geometry, share.shape[1:], src.transform)
    curves = share[:, ~outside]
    days = np.arange(1, share.shape[0] + 1)
    fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
    ax.plot(days, curves, color='tab:green', alpha=0.1, linewidth=0.8)
    ax.plot(days, np.median(curves, axis=1), color='black', label='median over pixels')
    ax.set(
        xlabel='day of year', ylabel='share of years viable', ylim=(0, 1),
        title=f'Viable planting days by day of year, Malawi, 1994–2023 ({curves.shape[1]} pixels)',
    )
    ax.legend(loc='upper center')
    save(fig, 'malawi_day_of_year.png')


def validation(table):
    """Box-plot maize yields by majority zone and by GYGA climate zone, each ordered by median yield."""
    fig, axs = plt.subplots(1, 2, figsize=(14, 6.5), constrained_layout=True)
    for ax, column, name in [(axs[0], 'zone', 'MPOU zone'), (axs[1], 'gyga', 'GYGA climate zone')]:
        groups = table.groupby(column)['yield']
        order = groups.median().sort_values().index
        ax.boxplot([groups.get_group(z) for z in order], tick_labels=[str(int(z)) for z in order], showfliers=False)
        for i, z in enumerate(order, start=1):
            ax.text(i, 0, str(groups.size()[z]), ha='center', va='bottom', fontsize=8)
        ax.set(title=f'{name}, {len(order)} zones', xlabel=name, ylabel='maize yield (t/ha)')
        ax.tick_params(axis='x', rotation=90)
    fig.suptitle(f'Maize yields by zone, HarvestStat Africa {START_YEAR}–2024 ({len(table)} region-years)')
    save(fig, 'validation.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('region', help='Sub-Saharan Africa outline, AfSP012Qry_SubSaharanAfrica.shp')
    parser.add_argument('hvstat_csv', help='HarvestStat Africa hvstat_africa_data_v1.0.csv')
    parser.add_argument('hvstat_gpkg', help='HarvestStat Africa hvstat_africa_boundary_v1.0.gpkg')
    parser.add_argument('gyga', help='GYGA climate zones raster GYGA_ED.tif')
    args = parser.parse_args()

    os.makedirs(FIGURES, exist_ok=True)
    region = gpd.read_file(args.region)
    table, regions = evaluation(args.hvstat_csv, args.hvstat_gpkg, args.gyga)
    selected = regions[regions['ADMIN0'].isin(COUNTRIES)]
    evaluated = table[['ADMIN0', 'ADMIN1']].drop_duplicates()
    print(
        f'{len(selected)} admin-1 regions with a zone in the selected countries; {len(evaluated)} of them, in '
        f'{evaluated["ADMIN0"].nunique()} countries, have yields: {len(table)} region-years, '
        f'{table["zone"].nunique()} MPOU zones, {table["gyga"].nunique()} GYGA zones'
    )
    layers(region)
    zones(region, selected)
    validation(table)
    climate(region)
    malawi_pixel()
    malawi_day_of_year(regions[regions['ADMIN0'] == 'Malawi'])


if __name__ == '__main__':
    main()
