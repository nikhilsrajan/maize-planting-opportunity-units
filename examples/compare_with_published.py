"""Check the example's rasters pixel for pixel against the published CSU rasters and print PASS or FAIL per file."""
import argparse
import os
import sys

import numpy as np
import rasterio

PUBLISHED_NAMES = {
    'planting_opportunity_days.tif': (
        'sum-suitable-days_tbase=8_reqgddpol=842_reqgddmat=2400_maxtoltemp=45_mintoltemp=0'
        '_minreqprecmat=450_maxduration=500_dryspellthreshold=1_maxconsecdryspell=5_daystogerm=3'
        '_minreqprecgerm=20.tif'
    ),
    'season_length.tif': 'mean_days_to_maturity.tif',
    'zones_nbins=8.tif': 'CSU_nbins=8.tif',
}


def read(filepath):
    """Return band 1, transform and CRS of a GeoTIFF."""
    with rasterio.open(filepath) as src:
        return src.read(1), src.transform, src.crs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outdir', help='folder written by era5_sub_saharan_africa.py')
    parser.add_argument('published_dir', help='folder holding the published rasters and CSU_nbins=8.tif')
    args = parser.parse_args()

    failed = False
    for name, published_name in PUBLISHED_NAMES.items():
        new, new_transform, new_crs = read(os.path.join(args.outdir, name))
        old, old_transform, old_crs = read(os.path.join(args.published_dir, published_name))
        if (new.shape, new.dtype, new_transform, new_crs) != (old.shape, old.dtype, old_transform, old_crs):
            print(f'FAIL {name}: grid or dtype differs: {new.shape} {new.dtype} vs {old.shape} {old.dtype}')
            failed = True
            continue
        n_diff = int(np.sum(~((new == old) | (np.isnan(new) & np.isnan(old)))))
        print(f'PASS {name}' if n_diff == 0 else f'FAIL {name}: {n_diff} of {new.size} pixels differ')
        failed |= n_diff > 0
    sys.exit(failed)


if __name__ == '__main__':
    main()
