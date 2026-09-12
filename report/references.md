# Citation audit: what needs a source, and what the source is

Every hard-set value and every rule in `mpou.viable_planting_days` is listed here with the reference that
supports it. **Status** says how far the check got:

- **verified** — the number or wording was read from the source.
- **secondary** — the number is quoted consistently by several sources, but the primary document was not
  opened from here (paywall, dead link, TLS failure).
- **open** — no adequate source yet; the value needs a decision before it can be defended in print.

## 1. Parameters

| Value | Rule it sets | Reference | Status |
|---|---|---|---|
| `t_base` = 8 °C | base for growing degree days | Sánchez et al. (2014), Table 2: maize Tmin is 7.7 °C (SE 0.5) for anthesis and 8.0 °C (SE 2.0) for grain filling. CERES-Maize/DSSAT likewise defines P5 on an 8 °C base | verified |
| `required_gdd_for_pollination` = 842 °C·day | when the pollination test is applied | CIMMYT Maize Product Catalog, entry CAH219: "50% anthesis — 55 days — 842 GDD (°C)". Corroborated by Soler et al. (2005): emergence to silking ≈ 800–900 °C·day on a 10 °C base | verified — the catalog gives no base temperature (§ 4.1) |
| `required_gdd_for_maturity` = 2400 °C·day | season ends when GDD exceed this | Popescu et al. (2021) give 2400–2500 °C for semi-early/semi-late and 2600–2700 °C for late hybrids | open, and hard to reconcile with 842 (§ 4.2) |
| `max_tolerable_temp` = 45 °C | a day at or above this kills the season | Sánchez et al. (2014): maize lethal maximum 46.0 °C (SE 2.9), and they cite Sinsawat et al. (2004) that temperatures over 45 °C cause irreversible damage to maize tissue | verified (but see § 4.3) |
| `min_tolerable_temp` = 0 °C | a day at or below this kills the season | Sánchez et al. (2014): maize lethal minimum −1.8 °C (SE 1.9), citing Carter & Hesterman (1990) that lethal damage to stem, leaf and ear occurs below −2.2 °C for a few minutes or below 0 °C for more than 4 h | verified (but see § 4.3) |
| `max_duration` = 500 days | longest allowed season | none — a computational guard, not an agronomic claim | n/a |
| `min_total_prec_till_maturity` = 450 mm | rain needed from sowing to maturity | FAO: "for maximum production a medium maturity grain crop requires between 500 and 800 mm of water depending on climate" (FAO Crop Information: Maize; FAO 1986, Table 5) | verified (see § 4.4) |
| `max_consecutive_dry_days` = 5 | dry run at pollination that fails the season | Barron et al. (2003): an agricultural dry spell for grain cultivation in semi-arid tropical SSA "generally range[s] between 5 and 15 days", and they report dry-spell probabilities at exactly the > 5, > 10 and > 15 day thresholds; Mengistu et al. (2021) define a dry spell as a 5-day pentad | verified as the lower bound of the agronomic range (see § 4.5) |
| `dryspell_threshold` = 1 mm | a day below this is dry | ETCCDI convention: a dry day has precipitation < 1 mm (Zhang et al. 2011). Mengistu et al. (2021) list 1.0 mm as a standard threshold (Douguedroit 1987; Frei et al. 2003; Usman & Reason 2004); Barron et al. (2003) use < 0.85 mm after Stern et al. (1982) | verified |
| `days_to_germination` = 3 | germination window | Sivakumar (1988): onset of rains = 20 mm over 3 consecutive days | verified |
| `min_total_prec_for_germination` = 20 mm | rain the window must exceed | Sivakumar (1988), as above; Rezaei et al. (2020) test 10–30 mm accumulation rules for maize sowing dates | verified |
| `n_bins` = 8, `opportunity_max` = 3652, `season_min/max` = 100/360 | zone binning | none needed — chosen to match the GYGA zone count in the evaluation region (report § 3.5) | n/a |

## 2. The logic that maize fails from a dry spell at pollination

This is the method's central agronomic claim and it is the best-supported one.

1. **Flowering is the most sensitive stage.** FAO's yield response factors for maize are ky = 0.4
   (vegetative), **1.5 (flowering)**, 0.5 (yield formation), 0.2 (ripening) and 1.25 for the whole season —
   flowering is the only stage where a relative water deficit costs *more* than proportional yield
   (Doorenbos & Kassam 1979, FAO Irrigation and Drainage Paper 33). FAO-56 (Allen et al. 1998, Table 24)
   carries the seasonal value 1.25 and credits Paper 33.
2. **Why the grain fails.** FAO Crop Information: Maize — "Severe water deficits during the flowering
   period, particularly at the time of silking and pollination, may result in little or no grain yield due
   to silk drying", and "the greatest decrease in grain yields is caused by water deficits during the
   flowering period including tasselling and silking and pollination, due mainly to a reduction in grain
   number per cob."
3. **Experimental basis.** Denmead & Shaw (1960) first dated the sensitivity: stress at flowering cut yield
   about 50 %, against 21 % during grain filling. NeSmith & Ritchie (1992) showed deficits at tassel
   emergence cut yield by more than 90 % when they ran into grain fill. Grant et al. (1989) resolved the
   window: kernel number is sensitive from about 2–7 days after silking to 16–22 days after silking.
   Schussler & Westgate (1991) showed the loss is developmental failure after fertilisation, not pollen
   failure.
4. **Dry spells, not seasonal totals, are what rainfed African maize actually faces.** Barron et al. (2003)
   found maize met a dry spell longer than 10 days during flowering in more than 80 % of seasons on sandy
   soil and at least 60 % on clay, at two semi-arid East African sites. Marcos-Garcia et al. (2024) found
   the intra-season dry–wet spell pattern explains 50–60 % of interannual maize yield variation across
   sub-Saharan Africa, against 30–35 % for seasonal mean rainfall and temperature. Mengistu et al. (2021)
   make the operational point MPOU encodes: "planting dates should be chosen to ensure that this stage
   coincides with normally favourable growing conditions and does not coincide with midsummer drought
   periods."

## 3. Framing claims in the report

| Claim | Reference |
|---|---|
| MPOU as a crop-specific alternative to technology extrapolation domains (report § 1) | Rattalino Edreira et al. (2018) |
| GYGA climate zones as the comparison scheme (report § 5) | van Wart et al. (2013) |
| Maize-based systems and their constraints in sub-Saharan Africa | Snapp et al. (2010); Droppelmann, Snapp & Waddington (2017) |
| Field-scale yield-gap mapping as the use case for zoning | Schulthess et al. (2013) |
| Operational agricultural monitoring this feeds into | Becker-Reshef et al. (2020, 2023) |

## 4. Open items

### 4.1 The 842 GDD figure — sourced, with one caveat
The catalog entry was read on 2026-09-12 (saved as `docs/cah219.pdf`; the live site fails TLS verification
from this laptop). It confirms the number exactly: under Agronomic Characteristics, **"50% anthesis — 55
days — 842 GDD (°C)"**, with the abbreviation list giving "GDD = growing degree-days (°C)". So 842 is the
thermal time to 50 % anthesis, which is precisely the event MPOU's pollination test is meant to locate. The
entry is CAH219, an intermediate-maturing (maturity group: Medium) single-cross yellow semi-dent hybrid,
adapted to **tropical lowland South Asia**, announced 2024, from CIMMYT South Asia 2021/22 Stage 4 and
2022/23 Stage 5 trials. Anthesis-silking interval 2.1 days.

Two things the entry does **not** settle:

1. **No base temperature.** The page gives "842 GDD (°C)" and never says what base the sum uses. MPOU applies
   it on an 8 °C base. Maize GDD is most often computed on a 10 °C base (8–10 °C across the literature), and
   the entry's own arithmetic leans that way: 842 GDD over 55 days is 15.3 °C·day per day, which implies a
   mean air temperature of 25.3 °C on a 10 °C base or 23.3 °C on an 8 °C base — the former is the better fit
   for tropical-lowland South Asia. That is an indication, not proof. If the catalog is on a 10 °C base, then
   feeding 842 into an 8 °C-base accumulation reaches the pollination test *earlier in the season* than the
   hybrid would actually flower. Worth one email to the catalog contact (P.Nagesh@cgiar.org) or a look at the
   entry's "Full Product Announcement" link.
2. **It is a South Asian hybrid.** Using its anthesis GDD for a Sub-Saharan Africa map is defensible — anthesis
   thermal time is fairly conservative across tropical maize — but it is an assumption, and the report should
   say so rather than let the reader assume an African variety.

### 4.2 The 2400 GDD figure — and a units trap

Do not cite US hybrid ratings for this. American "2400 GDU" figures are computed on a 50 °F base with an
86 °F cap; converted, they are about 1330 °C·day on a 10 °C base — roughly half of MPOU's 2400 °C·day. The
figures that *are* on the same scale are European: 2400–2500 °C for semi-early to semi-late hybrids and
2600–2700 °C for late ones (Popescu et al. 2021 — statement found through search, the paper itself returned
403 and was not read). On that scale 2400 °C·day is a **medium-late to late** variety, not the "medium
maturity" the README and report § 3.1 claim. Either soften that wording, or cite a tropical-maize thermal
requirement and say which maturity class it is.

**842 and 2400 do not sit on the same crop.** Now that 842 is confirmed as anthesis thermal time, the two
GDD parameters can be checked against each other, and they disagree:

- CAH219 is an *intermediate*-maturing hybrid reaching 50 % anthesis at 842 GDD. Adding the DSSAT/CERES-Maize
  P5 coefficient — silking to physiological maturity, defined on an 8 °C base, reported in the 790–900
  °C·day range — puts that hybrid's whole season at roughly **1650–1750 °C·day**, not 2400.
- As a ratio: Soler et al. (2005) give emergence to silking ≈ 800–900 °C·day against emergence to maturity
  ≈ 1400–1500 °C·day, so anthesis falls at about **0.55–0.60** of the season. MPOU's 842/2400 is **0.35**.

So MPOU applies its dry-spell test about a third of the way through the season rather than just past halfway:
either 842 belongs to a shorter-season crop than 2400 does, or the two numbers use different base
temperatures, or both. This does not affect v1.0.0 — the published rasters must reproduce as they are — but
it is the substantive parameter question for v1.1.0, and the report should not present the two values as a
matched pair describing one variety.

### 4.3 45 °C and 0 °C are sourced, but are applied to a daily *mean*
Both numbers now have a source (Sánchez et al. 2014, Table 2 and text: maize lethal limits −1.8 °C and
46.0 °C; over 45 °C causes irreversible tissue damage; lethal damage below 0 °C for more than 4 h). What
remains is that MPOU tests them against **ERA5 daily mean** temperature, not a daily maximum or an hourly
value, while the sources are about tissue temperature over hours. A daily mean of 45 °C essentially never
occurs, so `max_tolerable_temp` is close to inert in the published run; a daily mean at or below 0 °C does
occur in the highlands, so `min_tolerable_temp` bites. Worth one sentence in the report, and it is also the
honest answer to the docx's "38 °C" discrepancy (README quirk 7).

Sánchez et al. also make a point MPOU does **not** capture: maize pollination is damaged by heat as well as
by drought — pollen exposed to 38 °C failed to germinate (Herrero & Johnson 1980) and temperatures over
32 °C cut pollen germination sharply (Schoper et al. 1987). MPOU's pollination test is water-only. Since the
model already locates anthesis (842 GDD), a heat test at the same point is the obvious v1.1.0 extension.

### 4.4 450 mm sits just under the FAO range
FAO gives 500–800 mm for a medium-maturity grain crop, so 450 mm is a deliberately permissive floor rather
than a cited requirement. Say so, or raise it in v1.1.0 — do not present 450 mm as the FAO number.

### 4.5 Five days is the lower bound of the agronomic range — defensible, and strict
Barron et al. (2003) supply what was missing: for grain cultivation in semi-arid tropical sub-Saharan Africa,
an agricultural dry spell — a run of days where the crop takes up less than half its water requirement —
"generally range[s] between **5 and 15 days**", and the paper reports dry-spell probabilities at exactly the
**> 5, > 10 and > 15 day** thresholds. Mengistu et al. (2021) independently take the 5-day pentad as the unit
of dry-spell analysis over the South African maize belt. So 5 days is the short end of the range agronomists
treat as damaging, not an arbitrary pick, and it can be cited as such.

One caveat to state plainly: at Barron's two sites a dry spell of more than five consecutive days is very
likely at any time of year (P = 90 % and 78 % at Machakos for the long and short rains, 75 % and 86 % at
Same), whereas > 10-day spells run at 20–30 % minimum. A 5-day trigger is therefore a **strict** test — in
semi-arid areas it will reject most candidate planting dates, which is consistent with MPOU's low opportunity
counts there. Raising it to 10 days would be the natural sensitivity test for v1.1.0; the parameter is
already exposed for exactly that.

### 4.6 Not read directly
Popescu et al. (2021) returned 403; its 2400–2500 °C figure is quoted from search results only, so § 4.2
should not lean on it alone. The FAO Crop Information: Maize page is indexed and quotable but its `/en/` and
`/es/` URLs currently return 404 — check whether FAO has moved it before the page is cited by URL. Doorenbos
& Kassam (1979) was not opened either: the maize ky values (0.4 / 1.5 / 0.5 / 0.2 / 1.25) are consistent
across secondary sources and FAO-56 confirms the seasonal 1.25 and credits Paper 33, but if the report prints
the stage-by-stage figures, read them off the paper first.

Sánchez et al. (2014), Barron et al. (2003) and Mengistu et al. (2021) **were** read in full (2026-09-12,
PDFs in `docs/`), which is what moved `t_base`, `max_tolerable_temp`, `min_tolerable_temp`,
`max_consecutive_dry_days` and `dryspell_threshold` to verified.

## References

Allen, R.G., Pereira, L.S., Raes, D. & Smith, M. (1998). *Crop evapotranspiration: guidelines for computing
crop water requirements.* FAO Irrigation and Drainage Paper 56. FAO, Rome.
https://www.fao.org/4/x0490e/x0490e0e.htm

Barron, J., Rockström, J., Gichuki, F. & Hatibu, N. (2003). Dry spell analysis and maize yields for two
semi-arid locations in East Africa. *Agricultural and Forest Meteorology* 117, 23–37.
https://doi.org/10.1016/S0168-1923(03)00037-6 — a dry day is < 0.85 mm (after Stern et al. 1982); an
agricultural dry spell is a run of days where crop uptake meets < 50 % of the requirement, and for grain
cultivation in semi-arid tropical SSA such spells "generally range between 5 and 15 days"; probabilities are
reported at > 5, > 10 and > 15 days. Maize met at least one spell of ≥ 10 days in 74–80 % of seasons, and
> 10-day spells during flowering and early grain filling in over 80 % of seasons on sandy soil.

Becker-Reshef, I., Justice, C., Barker, B., Humber, M., Rembold, F., Bonifacio, R., et al. (2020).
Strengthening agricultural decisions in countries at risk of food insecurity: the GEOGLAM Crop Monitor for
Early Warning. *Remote Sensing of Environment* 237, 111553. https://doi.org/10.1016/j.rse.2019.111553

Becker-Reshef, I., Barker, B., Whitcraft, A., Oliva, P., Mobley, K., Justice, C. & Sahajpal, R. (2023). Crop
type maps for operational global agricultural monitoring. *Scientific Data* 10, 172.
https://doi.org/10.1038/s41597-023-02047-9

Black, E., Asfaw, D.T., Sananka, A., Aston, S., Boult, V.L. & Maidment, R.I. (2023). Application of
TAMSAT-ALERT soil moisture forecasts for planting date decision support in Africa. *Frontiers in Climate* 4,
993511. https://doi.org/10.3389/fclim.2022.993511 — validated against more than 30,000 observed planting
dates and yields in Kenya, Rwanda, Uganda, Zambia and Malawi; farmers planting near the recommendation
obtained 7–10 % higher yields.

CIMMYT (2024). CAH219. *CIMMYT Maize Product Catalog*, web published 2 June 2024.
https://maizecatalog.cimmyt.org/tech/CAH219 — intermediate-maturing single-cross hybrid for the tropical
lowlands of South Asia; 50 % anthesis at 55 days / 842 GDD (°C); base temperature not stated. Product
information from CIMMYT South Asia 2021/22 Stage 4 and 2022/23 Stage 5 trials.

Denmead, O.T. & Shaw, R.H. (1960). The effects of soil moisture stress at different stages of growth on the
development and yield of corn. *Agronomy Journal* 52, 272–274.

Doorenbos, J. & Kassam, A.H. (1979). *Yield response to water.* FAO Irrigation and Drainage Paper 33. FAO,
Rome. — source of the maize yield response factors ky = 0.4 vegetative, 1.5 flowering, 0.5 yield formation,
0.2 ripening, 1.25 total.

Droppelmann, K.J., Snapp, S.S. & Waddington, S.R. (2017). Sustainable intensification options for smallholder
maize-based farming systems in sub-Saharan Africa. *Food Security* 9, 133–150.
https://doi.org/10.1007/s12571-016-0636-0

FAO (1986). *Irrigation water management: irrigation water needs.* Training Manual 3, Chapter 2: Crop water
needs. FAO, Rome. https://www.fao.org/4/s2022e/s2022e02.htm — maize 500–800 mm per growing period; grain
maize 125–180 days.

FAO. *Crop Information: Maize.* Land & Water Division, FAO, Rome.
https://www.fao.org/land-water/databases-and-software/crop-information/maize/en/ (URL currently returns 404;
see § 4.6)

Grant, R.F., Jackson, B.S., Kiniry, J.R. & Arkin, G.F. (1989). Water deficit timing effects on yield
components in maize. *Agronomy Journal* 81, 61–65.

Ichami, S.M., Shepherd, K.D., Sila, A.M., Stoorvogel, J.J. & Hoffland, E. (2018). Fertilizer response and
nitrogen use efficiency in African smallholder maize farms. *Nutrient Cycling in Agroecosystems* 113, 1–19.
https://doi.org/10.1007/s10705-018-9958-y — median fertilizer response 1.7 in sub-Saharan Africa; 18 % of
plots non-responsive (FR < 1); available soil, climate and management data explained < 33 % of the variation
in fertilizer response and nitrogen use efficiency.

Kim, Y.U., Webber, H., Adiku, S.G., Nóbrega Júnior, R.D.S., Deswarte, J.C., Asseng, S. & Ewert, F. (2024).
Mechanisms and modelling approaches for excessive rainfall stress on cereals: waterlogging, submergence,
lodging, pests and diseases. *Agricultural and Forest Meteorology* 344, 109819.
https://doi.org/10.1016/j.agrformet.2023.109819

Lobell, D.B., Bänziger, M., Magorokosho, C. & Vivek, B. (2011). Nonlinear heat effects on African maize as
evidenced by historical yield trials. *Nature Climate Change* 1, 42–45. https://doi.org/10.1038/nclimate1043
— from over 20,000 African maize trials: each degree day above 30 °C reduced yield by 1 % under optimal
rainfed conditions and by 1.7 % under drought.

Marcos-Garcia, P., Carmona-Moreno, C. & Pastori, M. (2024). Intra-growing season dry–wet spell pattern is a
pivotal driver of maize yield variability in sub-Saharan Africa. *Nature Food* 5, 775–786.
https://doi.org/10.1038/s43016-024-01040-8

Mengistu, M.G., Olivier, C., Botai, J.O., Adeola, A.M. & Daniel, S. (2021). Spatial and temporal analysis of
the mid-summer dry spells for the summer rainfall region of South Africa. *Water SA* 47(1), 76–87.
https://doi.org/10.17159/wsa/2021.v47.i1.9447 — "a dry spell is defined as a period of 5 days (a pentad)
during which rainfall totals are less than predefined thresholds" (5, 10 and 15 mm per pentad; the Markov
analysis uses 3 mm/day = 15 mm/pentad). Reviews the dry-day thresholds in use (0.1, 1.0, 2.0, 3.0, 10 mm)
and states that the flowering stage of maize is the most sensitive to water stress, so planting dates should
be chosen so it misses the mid-summer dry period.

NeSmith, D.S. & Ritchie, J.T. (1992). Effects of soil water-deficits during tassel emergence on development
and yield components of maize (*Zea mays*). *Field Crops Research* 28, 251–256.

Popescu, S. et al. (2021). Agrometeorological requirements of maize crop phenology for sustainable
cropping — a historical review for Romania. *Sustainability* 13(14), 7719.
https://doi.org/10.3390/su13147719 (not read directly; see § 4.2)

Rattalino Edreira, J.I., Cassman, K.G., Hochman, Z., van Ittersum, M.K., van Bussel, L., Claessens, L. &
Grassini, P. (2018). Beyond the plot: technology extrapolation domains for scaling out agronomic science.
*Environmental Research Letters* 13, 054027. https://doi.org/10.1088/1748-9326/aac092

Rezaei, E.E., Ghazaryan, G., González, J., Cornish, N., Dubovyk, O. & Siebert, S. (2020). The use of remote
sensing to derive maize sowing dates for large-scale crop yield simulations. *International Journal of
Biometeorology* 65, 565–576. https://doi.org/10.1007/s00484-020-02050-4

Sacks, W.J., Deryng, D., Foley, J.A. & Ramankutty, N. (2010). Crop planting dates: an analysis of global
patterns. *Global Ecology and Biogeography* 19, 607–620. https://doi.org/10.1111/j.1466-8238.2010.00551.x

Sánchez, B., Rasmussen, A. & Porter, J.R. (2014). Temperatures and the growth and development of maize and
rice: a review. *Global Change Biology* 20, 408–417. https://doi.org/10.1111/gcb.12389 — Table 2, maize
(mean ± SE, n literature sources): lethal limits −1.8 °C (1.9) and 46.0 °C (2.9); anthesis Tmin 7.7 (0.5),
Topt 30.5 (2.5), Tmax 37.3 (1.3); grain filling Tmin 8.0 (2.0), Topt 26.4 (2.1), Tmax 36.0 (1.4); whole
plant Tmin 6.2 (1.1), Topt 30.8 (1.6), Tmax 42.0 (3.3); sowing to emergence Tmin 10.0 (2.2).

Schulthess, U., Timsina, J., Herrera, J.M. & McDonald, A. (2013). Mapping field-scale yield gaps for maize:
an example from Bangladesh. *Field Crops Research* 143, 151–156.
https://doi.org/10.1016/j.fcr.2012.11.004

Schussler, J.R. & Westgate, M.E. (1991). Maize kernel set at low water potential: II. Sensitivity to reduced
assimilates at pollination. *Crop Science* 31, 1196–1203.

Sivakumar, M.V.K. (1988). Predicting rainy season potential from the onset of rains in southern Sahelian and
Sudanian climatic zones of West Africa. *Agricultural and Forest Meteorology* 42, 295–305. — onset = 20 mm
over 3 consecutive days, with no dry spell longer than 7 days in the following 30 days.

Snapp, S.S., Blackie, M.J., Gilbert, R.A., Bezner-Kerr, R. & Kanyama-Phiri, G.Y. (2010). Biodiversity can
support a greener revolution in Africa. *PNAS* 107(48), 20840–20845.
https://doi.org/10.1073/pnas.1007199107

Soler, C.M.T., Sentelhas, P.C. & Hoogenboom, G. (2005). Thermal time for phenological development of four
maize hybrids grown off-season in a subtropical environment. *Journal of Agricultural Science* 143, 169–182.

Steinkopf, J. & Engelbrecht, F. (2022). Verification of ERA5 and ERA-Interim precipitation over Africa at
intra-annual and interannual timescales. *Atmospheric Research* 280, 106427.
https://doi.org/10.1016/j.atmosres.2022.106427 — reanalyses over-produce wet days ("drizzle") and
underestimate heavy rainfall over Africa.

van Wart, J., van Bussel, L.G.J., Wolf, J., Licker, R., Grassini, P., Nelson, A., Boogaard, H., Gerber, J.,
Mueller, N.D., Claessens, L., van Ittersum, M.K. & Cassman, K.G. (2013). Use of agro-climatic zones to
upscale simulated crop yield potential. *Field Crops Research* 143, 44–55.
https://doi.org/10.1016/j.fcr.2012.11.023

Zhang, X., Alexander, L., Hegerl, G.C., Jones, P., Klein Tank, A., Peterson, T.C., Trewin, B. & Zwiers, F.W.
(2011). Indices for monitoring changes in extremes based on daily temperature and precipitation data. *WIREs
Climate Change* 2, 851–870. https://doi.org/10.1002/wcc.147 — ETCCDI convention: a dry day is a day with
precipitation below 1 mm.
