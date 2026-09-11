# Maize Planting Opportunity Units (MPOU)

MPOU zones land by how often daily weather let maize planted on a given day reach maturity, and by the
typical season length. It works with any daily temperature and precipitation data. The published maps
cover Sub-Saharan Africa with ERA5 from 1994 to 2024.

## What MPOU measures

For every pixel and every day *t*, MPOU asks: would maize planted on day *t* have germinated and reached
maturity? Day *t* is a **viable planting day** when:

1. **Germination:** rain on days *t*+1 … *t*+3 totals more than 20 mm.
2. **Maturity**, counted from *s* = *t*+3 (the end of germination):
   - growing degree days, the sum of max(*T* − 8 °C, 0), exceed 2400 within 500 days;
   - no day before that reaches 45 °C or drops to 0 °C;
   - rain on days *s*+1 … *s*+(days to maturity) totals at least 450 mm.
3. **Pollination:** the run of dry days (< 1 mm) that starts the day after 842 GDD are exceeded is
   shorter than 5 days. A dry spell at pollination is what makes maize fail.

From the viable days MPOU builds three layers:

- **Planting opportunity days**: the number of viable days before a cutoff date.
- **Season length**: the mean days to maturity over all viable days.
- **Zones**: both layers split into equal bins, combined as `season_bin * 100 + opportunity_bin`.
  With 8 bins, zone 305 has season bin 3 and opportunity bin 5.

## Inputs and outputs

Inputs are numpy arrays of shape (time, y, x): daily mean temperature in °C and daily total
precipitation in mm, on the same grid and days.

| Output | Shape, dtype | Meaning |
|---|---|---|
| `viable` | (time, y, x), bool | viable planting days |
| `days_to_maturity` | (time, y, x), int64 | days from each day until 2400 GDD are exceeded; −1 if never |
| `opportunity_days` | (y, x), uint16 | viable days before `cutoff_index` |
| `season_length` | (y, x), float64 | mean `days_to_maturity` over viable days; NaN if none |
| `zones` | (y, x), uint16 | zone codes, bins numbered from 1 |

## Install

Python 3.11. `mpou.py` is one file that needs only numpy and numba, so you can also copy it into a
project.

```
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Tests compare `mpou` against a frozen copy of the legacy code: `.venv/bin/pip install pytest && .venv/bin/pytest`.

## Usage

```python
import mpou

# temp: daily mean temperature (°C), prec: daily total precipitation (mm), both (time, y, x)
viable, days_to_maturity = mpou.viable_planting_days(temp, prec)
opportunity_days, season_length = mpou.summarize(viable, days_to_maturity, cutoff_index=10957)
zones = mpou.zones(opportunity_days, season_length, n_bins=8)
```

`cutoff_index` is the index of the first day not counted in `opportunity_days`. `mpou.zones` also takes
`opportunity_max=3652`, `season_min=100` and `season_max=360`, the bin ranges of the published map.
3652 is a third of the 10,957 days from 1994-01-01 to 2024-01-01.

## Parameters

Keyword arguments of `mpou.viable_planting_days`. The defaults are the published values for a medium
maturity maize.

| Parameter | Default | Unit | Meaning |
|---|---|---|---|
| `t_base` | 8 | °C | base temperature for growing degree days |
| `required_gdd_for_pollination` | 842 | °C·day | GDD to pollination ([CIMMYT CAH219](https://maizecatalog.cimmyt.org/tech/CAH219)) |
| `required_gdd_for_maturity` | 2400 | °C·day | GDD to maturity |
| `max_tolerable_temp` | 45 | °C | a day at or above this before maturity fails the season |
| `min_tolerable_temp` | 0 | °C | a day at or below this before maturity fails the season |
| `max_duration` | 500 | days | longest allowed time to maturity |
| `min_total_prec_till_maturity` | 450 | mm | least rain from the day after sowing to maturity |
| `max_consecutive_dry_days` | 5 | days | the dry run at pollination must be shorter than this |
| `dryspell_threshold` | 1 | mm | a day with less rain than this is dry |
| `days_to_germination` | 3 | days | length of the germination window |
| `min_total_prec_for_germination` | 20 | mm | rain in the germination window must exceed this |

## Reproduce the published maps

Run on the NASA Harvest cluster, with ERA5 already downloaded by
[download_era5](https://github.com/nikhilsrajan/download_era5). The example loads 31 years of daily data
(1994-01-01 to 2024-12-31, 11,323 days) over the bounding box of Sub-Saharan Africa, 249 × 333 pixels at
0.25°. It needs roughly 32 GB of RAM at peak and starts one loader process per core, so run it inside a
job allocation, not on a login node.

1. Set the paths:
   ```
   CATALOG=/gpfs/data1/cmongp1/sasirajann/download_era5/data/era5/catalog.csv
   REGION=/gpfs/data1/cmongp2/sasirajann/nh_crop_calendar/crop_calendar/data/shapefiles/AfSP012Qry_ISRIC/GIS_Shape/AfSP012Qry_SubSaharanAfrica.shp
   PUBLISHED=/gpfs/data1/cmongp2/sasirajann/nh_crop_calendar/crop_calendar/data/era5_csu/sub-saharan-africa/maize_pollination
   ```
2. Install:
   ```
   git clone https://github.com/nikhilsrajan/maize-planting-opportunity-units.git
   cd maize-planting-opportunity-units
   python3.11 -m venv .venv
   .venv/bin/pip install -r requirements.txt -r examples/requirements.txt
   ```
3. Copy the published zones raster `CSU_nbins=8.tif` into `$PUBLISHED`, once. It was made on a laptop
   and is not on the cluster.
4. Compute the three rasters, from the repository root:
   ```
   .venv/bin/python -m examples.era5_sub_saharan_africa "$CATALOG" "$REGION" outputs
   ```
5. Compare them with the published rasters:
   ```
   .venv/bin/python examples/compare_with_published.py outputs "$PUBLISHED"
   ```
   Expected output:
   ```
   PASS planting_opportunity_days.tif
   PASS season_length.tif
   PASS zones_nbins=8.tif
   ```

Every output GeoTIFF carries the parameters and dates as tags (`gdalinfo outputs/season_length.tif`).

## Renamed from CSU

MPOU was first called Crop Suitability Units (CSU). It was renamed because "suitability" has a specific
FAO meaning that this method does not follow. Only the names changed: the method, the zone codes and
every pixel value are the same.

| CSU (before) | MPOU (now) |
|---|---|
| Crop Suitability Units (CSU) | Maize Planting Opportunity Units (MPOU) |
| suitable day | viable planting day |
| sum of suitable days, `sum-suitable-days_tbase=8_…_minreqprecgerm=20.tif` | planting opportunity days, `planting_opportunity_days.tif` |
| mean days to maturity, `mean_days_to_maturity.tif` | season length, `season_length.tif` |
| CSU zones, `CSU_nbins=8.tif` | zones, `zones_nbins=8.tif` |
| `updated_compute_csu` → `final_suitability_days` | `mpou.viable_planting_days` → `viable` |
| sum and mean in `running_sum_prec.py` | `mpou.summarize` |
| `binify` and the zone code in `csu_validation.ipynb` | `mpou.zones` |

## Known quirks

v1.0.0 reproduces the published rasters pixel for pixel, so it keeps these behaviours of the original
code. Fixes are planned for v1.1.0.

1. **Out-of-range values land in bin 1.** A value above the top bin edge, or at or below the bottom edge,
   gets bin 1. In the published map this affects 1,087 pixels with more than 3652 opportunity days and
   187 pixels with a season longer than 360 days. Never-viable pixels (0 days, NaN season) get zone 101.
2. **The dry spell is counted forward.** It is the run of dry days starting at the pollination lookup day,
   not the run ending on it.
3. **The pollination lookup day is one day late.** It is the day after 842 GDD are exceeded.
4. **Rain windows exclude the start day.** They cover days *t*+1 … *t*+*d*.
5. **Season length and viability use different start days.** Season length averages days to maturity
   counted from the planting day *t*, while viability is judged from *t*+3. When *t* itself never reaches
   maturity, −1 enters the mean.
6. **Season length spans the whole series.** It includes days after the cutoff (2024 in the published
   run), while opportunity days stop at the cutoff.
7. **The CSU method note was wrong in two places.** It gives a maximum temperature of 38 °C and a failing
   dry spell of "more than 5 days". The published run used 45 °C and fails dry runs of 5 days or more.
   The defaults here match the published run.

## Validation

The zones (then called CSU) were evaluated against maize yields from HarvestStat Africa
([doi:10.5061/dryad.vq83bk42w](https://doi.org/10.5061/dryad.vq83bk42w)). They were compared with the
[GYGA climate zones](https://yieldgap-test.containers.wur.nl/web/guest/climate-zones). 8 bins were used
because they give a number of zones close to GYGA's in the region. The comparison used 187 admin-1 regions
in DR Congo, Kenya, Malawi, Mozambique, Rwanda, Zambia and Zimbabwe: the countries with 2016–2024 yields
and an assigned zone. Each region got its majority zone, and 578 region-years of yield were grouped by zone
and by GYGA climate zone. The two schemes group yields comparably. MPOU does worse than GYGA in low-yield
regions and better in medium-yield regions. Unlike GYGA, MPOU is crop-specific and its parameters can be
tuned.

## Data

The published maps use ERA5 from the Copernicus Climate Data Store dataset
[derived-era5-single-levels-daily-statistics](https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics)
(reanalysis, 1-hourly input, UTC):

- `2m_temperature`, daily mean, converted from K to °C.
- `total_precipitation`, daily sum, converted from m to mm.

## How to cite

A DOI will be added here when v1.0.0 is released on Zenodo. Until then, use GitHub's "Cite this
repository" button, which reads `CITATION.cff`.

## License

MIT, see `LICENSE`.
