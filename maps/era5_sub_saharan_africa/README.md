# MPOU maps: Sub-Saharan Africa, ERA5 1994–2024

These are the published Maize Planting Opportunity Units (MPOU) maps. They were made with MPOU v1.0.0 and
`examples/era5_sub_saharan_africa.py`, using the default maize parameters. The top-level README explains
how to reproduce them.

| File | dtype | Meaning |
|---|---|---|
| `planting_opportunity_days.tif` | uint16 | viable planting days from 1994-01-01 to 2023-12-31 |
| `season_length.tif` | float64 | mean days to maturity over all viable days from 1994-01-01 to 2024-12-31; NaN if none |
| `zones_nbins=8.tif` | uint16 | zones `season_bin * 100 + opportunity_bin` with 8 bins; nodata 0 |

- **Grid:** 249 × 333 pixels at 0.25°, EPSG:4326, from 25.375° W to 57.875° E and from 34.875° S to
  27.375° N. This is the bounding box of the ISRIC Sub-Saharan Africa outline
  (`AfSP012Qry_SubSaharanAfrica.shp`).
- **Weather:** ERA5 daily statistics from the Copernicus Climate Data Store
  ([derived-era5-single-levels-daily-statistics](https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics)).
  The inputs are `2m_temperature` (daily mean, °C) and `total_precipitation` (daily sum, mm), from
  1994-01-01 to 2024-12-31.
- **Parameters:** every file stores the MPOU parameters and dates as GeoTIFF tags. Run `gdalinfo` on a
  file to see them. The zones file also stores its bin settings. The `enddate` tag, 2024-12-01, is the
  date of the last monthly ERA5 file, so the data run to 2024-12-31.
- **Renamed from CSU:** these maps have the same pixels as the earlier Crop Suitability Units (CSU) maps,
  which were never published. The top-level README has a table of the renamed files.

## Licence

The maps are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The MPOU code is
MIT. When you use the maps, cite MPOU (see "How to cite" in the top-level README) and include:

> Contains modified Copernicus Climate Change Service information [1994–2024]. Neither the European
> Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data
> it contains.
