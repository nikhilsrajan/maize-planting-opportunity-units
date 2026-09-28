# Recommended bins for the MPOU zones

Can `zones_nbins=8.tif` have "recommended bins", and do bins make sense for downstream work?
Numbers below come from the committed maps, restricted to the 32,488 pixels inside the Sub-Saharan
Africa outline. Opportunity is shown **per year** (`planting_opportunity_days / 30`, the 30 years before
the cutoff).

## 1. Short answer

- **Yes, for stratifying or mapping.** Use bins to choose trial sites, stratify samples, report by
  domain, or draw a readable map. This is what the GYGA and GLI zone schemes are for.
- **No, for statistics.** For regression, correlation with yields or ML, use the two raw layers. Binning a
  continuous predictor throws away information and puts false steps at the bin edges (Royston et al.,
  2006).
- **The current equal-width 8 × 8 grid is not a good default** (§ 2). The recommended scheme is in § 4.

## 2. What is wrong with the current bins

| Finding | Number |
|---|---|
| Opportunity bin 1 (0–456 days = 0–15.2 d/yr) also holds never-viable pixels | 17,612 of 32,488 px (54 %); 9,569 of them never viable |
| Zone 101 alone | 12,258 px (38 %) |
| Opportunity is right-skewed (d/yr, viable pixels) | p10 1.0, median 27.4, p90 81.8, p99 182 |
| Season length vs `2400 / (T_mean − 8)` from the mean-temperature map | r = 0.955 |
| Opportunity vs season length (Spearman) | 0.17 |

What this means:
1. **"Never viable" is not its own class.** It shares a class with "viable a few days a year". That is the
   biggest distinction on the map.
2. **Season length is mostly a temperature map.** For one variety with a fixed 2400 GDD target, days to
   maturity is roughly 2400 / (T − 8). Its bins are therefore thermal zones (lowland / mid-altitude /
   highland), and they should be labelled that way. The two axes are nearly independent, so a 2-D
   matrix is justified.
3. **Equal-width edges ignore the skew.** Most of the map ends up in the bottom rows.

## 3. How other zone schemes chose their edges

| Scheme | Edges | Source |
|---|---|---|
| GYGA-ED (the scheme MPOU was compared against) | Only cells where major food crops cover > 0.5 % of the cell; GDD and aridity index each split into 10 intervals, **each holding 10 % of those cropland cells**; × 3 temperature-seasonality classes = 300 zones | van Wart et al. 2013, § 2.3.5 (**verified**, read) |
| GLI (revised SAGE) | GDD × precipitation, 10 × 10. Edges set so that **each zone holds 1 % of the crop's global harvested area** (the "equal-area approach") | van Wart et al. 2013, § 2.3.3, after Licker et al. 2010 and Mueller et al. 2012 (**verified**, read in van Wart) |
| Matrix vs cluster | Matrix edges come from "expert opinion or frequency distributions"; clusters (ISODATA, k-means) set edges from the data, but the zone count is still the researcher's choice | van Wart et al. 2013, §§ 2.1–2.2 (**verified**) |
| Survey stratification | Cumulative-√f rule: boundaries at equal steps of the cumulative square root of the frequencies, close to optimal for Neyman allocation | Dalenius & Hodges 1959 (**secondary**, via the Statistics Canada and CRAN `stratification` docs) |
| Choropleth maps | Readers did best with quantile classes; Jenks natural breaks scored under 70 % as accurate | Brewer & Pickle 2002 (**secondary**, abstract only) |
| Maize mega-environments, SSA | Six classes: highland, dry/wet lowland, dry mid-altitude, wet lower/upper mid-altitude, set by maximum temperature, season rainfall (and soil pH in SADC) | Cairns et al. 2013; Setimela et al. (**secondary**: class names confirmed, numeric thresholds not found) |

Lessons for MPOU:
- **Weight by where maize grows, not by land pixels.** Both yield-gap schemes set their edges only on
  cropland. MPOU's edges are currently set by the Sahara, the Kalahari and the Congo forest.
- **Tie the edges to the purpose.** Equal-share classes suit sampling. Agronomic breakpoints suit maps
  people read.

## 4. Recommended approach

1. **Split out "never viable" as zone 0.** Pixels with opportunity = 0 have no season length. Today they
   become 101.
2. **Express opportunity in days per year.** People can read those numbers, and the edges no longer
   depend on the length of the record.
3. **Default map: fixed agronomic edges, 5 × 5 + zone 0.**
   - Opportunity (d/yr): `0 | (0, 5] | (5, 20] | (20, 45] | (45, 90] | > 90`, read as rare, short
     window, about one month, one long season, long or two seasons. These breakpoints are Claude's
     heuristic; no paper sets them.
   - Season length (days): `≤ 135 | 135–160 | 160–200 | 200–260 | > 260`. Through
     `T = 8 + 2400 / season` these match mean temperatures of about 25.8 / 23.0 / 20.0 / 17.2 °C, so the
     classes read as hot lowland → highland. Snap the edges to the mega-environment temperature thresholds
     once those numbers are sourced.
   - The top class of each axis has no upper limit.
   - Checked on the committed maps: all 25 cells are filled (smallest cell 83 px). Share of variance kept:
     opportunity 0.88, season 0.91 (1 − within-bin SS / total SS).
4. **Sampling and stratification: equal-area edges on maize land (the GYGA/GLI method).**
   - Mask to maize area (MapSPAM maize physical area > 0, or a cropland mask).
   - Set edges at maize-area-weighted quantiles on each axis.
   - Use 4–6 classes per axis. On the committed maps, natural-break GVF reaches 0.93 at k = 5 and 0.97 at
     k = 8, so more than 5 classes adds little. Cochran's classic advice (little gain beyond about 6
     strata) points the same way. The cumulative-√f rule is the alternative if the zones will drive
     Neyman-allocated sampling.
   - Round the edges and freeze them in the GeoTIFF tags. Edges re-derived on every run would make zone
     codes incomparable across runs and regions.
5. **Choose k by support and stability, not by eye.**
   - Every zone must hold enough maize area to be used: for example, at least N admin-1 units or trial
     sites for the planned analysis.
   - Zones must be stable across the record. Recompute opportunity for two 15-year halves, or bootstrap
     over years, and report how many pixels change zone. This needs per-year viable counts, which exist
     only on the cluster.
6. **Test the zones against something they should predict.** Yield spread is the wrong target (see
   `limitations.md` § 4). Use **observed planting dates / crop calendars**: zones should differ in when and
   how widely farmers plant. The GYGA-style check (within-zone spread of mean temperature and
   rainfall, van Wart § 3.2) is a cheap first test that needs no new data.

## 5. What this would change

- **The raw layers are untouched.** Only the zone map would change.
- **A v1.1.0 change is small.** `mpou.zones` would take explicit edge lists instead of `n_bins` /
  `opportunity_max` / `season_min` / `season_max`, and `_binify` would get a zone 0. Maize-area weighting stays in `examples/` or `report/`, because the core imports only numpy +
  numba.
- **Better layer, later.** A per-year reliability layer (the share of years with ≥ 1 viable day) would
  separate "how often" from "how long". The 30-year sum mixes the two, and it cannot be built from the
  committed rasters.

## References

- Brewer, C. A., & Pickle, L. (2002). Evaluation of methods for classifying epidemiological data on
  choropleth maps in series. *Annals of the Association of American Geographers*, 92(4), 662–681.
- Cairns, J. E., et al. (2013). Adapting maize production to climate change in sub-Saharan Africa.
  *Food Security*, 5, 345–360. https://doi.org/10.1007/s12571-013-0256-x
- Cochran, W. G. (1977). *Sampling Techniques* (3rd ed.). Wiley.
- Dalenius, T., & Hodges, J. L. (1959). Minimum variance stratification. *JASA*, 54(285), 88–101.
- Licker, R., et al. (2010). Mind the gap. *Global Ecology and Biogeography*, 19, 769–782.
- Mueller, N. D., et al. (2012). Closing yield gaps through nutrient and water management. *Nature*, 490,
  254–257.
- Royston, P., Altman, D. G., & Sauerbrei, W. (2006). Dichotomizing continuous predictors in multiple
  regression: a bad idea. *Statistics in Medicine*, 25(1), 127–141.
- van Wart, J., et al. (2013). Use of agro-climatic zones to upscale simulated crop yield potential.
  *Field Crops Research*, 143, 44–55.
