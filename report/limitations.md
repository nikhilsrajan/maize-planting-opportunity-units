# Limitations of MPOU v1.0.0

What this version does and does not support, and what to change next. Full citations are in
`references.md`; parameter-level sourcing is in that file's table and § 4.

MPOU v1.0.0 answers one question: **on how many days, historically, would maize planted on that day have
germinated and reached maturity, and how long would the season have been?** Everything below follows from
the gap between that question and the question people will assume it answers, which is "where does maize
do well".

Limitations are grouped by how much they change conclusions: § 1 defects (cosmetic to the current users),
§ 2 missing failure modes (the substantive ones), § 3 input data, § 4 the evaluation design, § 5 what MPOU
is actually good for. § 6 ranks the fixes.

## 1. Known defects in the code

These are documented in the README's "Known quirks" and are reproduced deliberately in v1.0.0.

1. **Bin overflow lands in bin 1** (`binify`). 909 pixels with more than 3652 opportunity days and 187 with
   a season longer than 360 days are binned as if they were in the *lowest* class. Low priority, as agreed:
   the colleague used the raw layers, and the zone raster is a derived product. Fix in v1.1.0.
2. **Season length can average −1.** Viability is judged from day *t*+3 but season length averages
   `days_to_maturity[t]`, and a −1 (never matured) can enter the mean. This biases season length downward
   by an unknown amount in pixels near the viability edge — unlike the binning bug, this one silently
   corrupts a raw layer, so it deserves the higher priority of the two.
3. **The dry spell is counted forward from the lookup day, and the lookup day is one day late.** The test
   asks about the run of dry days *starting* the day after 842 GDD are passed, rather than the dry run
   *ending* at anthesis. A crop is damaged by the drying that precedes and spans flowering, not only by what
   follows it (Denmead & Shaw 1960; Grant et al. 1989 place the sensitive window from about 2–7 to 16–22
   days after silking). The current test is therefore offset from the window the literature identifies.
4. **Rain windows exclude the start day**, and **season length spans the full series while opportunity days
   stop at the cutoff** — minor, but they make the two layers non-comparable in their time base.
5. **Zone codes are equal-width, not equal-frequency.** Zone 101 holds 12,344 of 32,488 pixels (38 %),
   merging "no viable day at all" with "lowest bin of both layers". A third of the map is one class that
   also conflates two meanings.

## 2. Maize failure modes MPOU does not represent

This is the substantive list. MPOU tests three things: enough rain to germinate, enough thermal time and
total rain to reach maturity, and no long dry run at anthesis. Maize fails for at least six other reasons.

### 2.1 Heat at flowering — the biggest single omission
MPOU's only temperature ceiling is `max_tolerable_temp = 45 °C`, applied to a **daily mean**. A daily mean
of 45 °C essentially never occurs in ERA5, so in the published run the model has no effective heat test at
all. The literature is unambiguous that this is where African maize actually loses yield:

- Lobell et al. (2011), on more than 20,000 historical maize trials in Africa: **each degree day above
  30 °C cut yield by 1 % under optimal rainfed conditions and by 1.7 % under drought.**
- Sánchez et al. (2014) give maize anthesis Tmax as 37.3 °C (SE 1.3), well below 45 °C, and note that
  pollination specifically is heat-sensitive: pollen continuously exposed to 38 °C failed to germinate
  (Herrero & Johnson 1980), and temperatures over 32 °C reduced pollen germination sharply (Schoper et al.
  1987).

MPOU already locates anthesis — that is what the 842 GDD parameter is for. Adding a heat test at the same
point is the cheapest real improvement available and requires no new input data.

### 2.2 Heat and drought are not independent
Lobell et al.'s 1.0 % vs 1.7 % per degree day is an interaction: the same heat costs 70 % more when water is
short. MPOU applies its temperature and water screens as independent boolean tests and so cannot express
"hot *and* dry at flowering", which is the combination that actually destroys a crop.

### 2.3 Rainfall is not plant-available water
MPOU compares gross rainfall totals against thresholds. It has no soil, no runoff, no drainage and no
evaporative demand. Barron et al. (2003), whose dry-spell framing MPOU's pollination test borrows, are
explicit that this is inadequate on its own — "for on-farm management of dry spells, rainfall-based analyses
of dry spell occurrence have only limited value", because actual crop water stress depends on rainfall
partitioning, soil water holding capacity, crop water demand and antecedent soil water. Their own numbers
show the size of the error:

- the maize crop used only **36–64 % of seasonal rainfall** on average, the rest lost to runoff and deep
  percolation;
- **soil type changed dry-spell exposure three- to fourfold** — maize on sandy soil met > 10-day agricultural
  dry spells three to four times more often than on clay, under the same rainfall.

So two pixels with identical ERA5 rainfall can have very different water stress, and MPOU assigns them the
same opportunity count. This is the strongest argument for adding a soil layer (the report's § 6 already
proposes SoilGrids) — it is not a refinement, it is the difference between a rainfall index and a water
balance.

### 2.4 Too much water is not modelled at all
Every MPOU test is one-sided: more rain is never penalised. Maize is markedly sensitive to waterlogging,
particularly in early vegetative stages, and excessive rainfall also drives lodging, pests and disease
(Kim et al. 2024 review the mechanisms and the modelling approaches for cereals). In a method whose whole
purpose is to rank planting dates, a planting date that drowns is scored identically to an ideal one.

### 2.5 Post-flowering water distribution
`min_total_prec_till_maturity` is a **total** over the whole season, so rain that falls entirely before
flowering satisfies it. FAO's yield response factors make the yield-formation stage the second most
sensitive after flowering (ky = 0.5 against 0.2 for ripening; Doorenbos & Kassam 1979), and the worked
Malawi example in the report shows the failure mode directly: 154 of 159 dry-season planting days met the
450 mm requirement because their windows reached into the *next* rainy season. Only the germination test
excluded them. That is a coincidence of parameterisation, not a designed safeguard.

### 2.6 Nitrogen, soil fertility and management dominate actual yields
MPOU is a weather model, and in smallholder sub-Saharan Africa weather is not the binding constraint on
yield. Ichami et al. (2018), across African smallholder maize farms, found median fertilizer response of
1.7, **18 % of plots non-responsive to nitrogen altogether**, and — the crucial number for us — available
soil, climate and management data explained **less than 33 %** of the variation in fertilizer response and
nitrogen use efficiency. Snapp et al. (2010) and Droppelmann, Snapp & Waddington (2017) make the same point
from the systems side. Any expectation that a weather-only zoning explains observed yields is therefore
mis-set from the start — see § 4.

### 2.7 One crop, one variety, one season
- **Fixed thermal requirement.** 2400 GDD encodes a single maturity class, while farmers choose varieties by
  the season they expect — extra-early tropical maize matures in 80–85 days against 110–140 for medium types
  (FAO). A region that looks unviable for a 2400 GDD variety may be perfectly viable for an early one.
  (`references.md` § 4.2 also shows 842 and 2400 do not describe the same variety.)
- **Bimodal rainfall is flattened.** Much of East Africa has two distinct growing seasons — both of Barron
  et al.'s sites are bimodal, with separate long and short rains that differ in reliability. MPOU counts
  viable days over the whole year and sums them into one number, so a location with two short seasons and one
  with a single long season can receive the same opportunity count with completely different agronomy.

### 2.8 Opportunity days are not independent opportunities
Rainfall is strongly autocorrelated — Barron et al. model it as a first-order Markov process precisely
because the probability of rain depends on whether yesterday was wet. Viable planting days therefore arrive
in runs, so "823 opportunity days over 30 years" is not 823 independent chances; it is a much smaller number
of viable *windows*, repeated. The layer measures something real but its units invite over-reading. A run-
length or per-season window count would carry the same information more honestly.

## 3. Input data

### 3.1 ERA5 over-produces light rain, and MPOU's thresholds are light-rain thresholds
This one interacts badly with the parameter choices. Reanalyses generate drizzle too readily: ERA5
overestimates the number of wet days over Africa and underestimates heavy rainfall, with wet bias arising
largely from precipitation on days that should be dry (Steinkopf & Engelbrecht 2022). Two of MPOU's
thresholds sit exactly in the affected band:

- `dryspell_threshold = 1 mm` — if ERA5 sprinkles sub-millimetre-to-few-millimetre rain on dry days, genuine
  dry runs are **broken up**, dry spells are under-detected, and the pollination test becomes too lenient;
- `min_total_prec_for_germination = 20 mm over 3 days` — too easily satisfied for the same reason, so
  planting opportunities are **over-counted**.

Both biases push the same way: MPOU on ERA5 probably overestimates planting opportunity, most in the
semi-arid areas where the distinction matters most. This deserves a sensitivity test against a
gauge-calibrated product (CHIRPS, TAMSAT) before the numbers are used quantitatively.

### 3.2 Resolution and daily means
A 0.25° pixel is about 28 km across, against smallholder fields of well under a hectare, so every pixel
value is an area average over terrain, soils and farms. Temperature is a daily mean, while the thermal
limits it is compared against describe tissue temperature over hours (`references.md` § 4.3).

## 4. The evaluation was the wrong test — and it was benchmarked against a tool built for a third purpose

**What was done.** Each admin-1 region received its majority MPOU zone; 578 region-years of HarvestStat
maize yield in 100 regions were grouped by that zone and the spread compared against the same grouping by
GYGA climate zone. The implicit criterion is within-zone yield homogeneity.

**Why it cannot work, in four steps:**

1. **Planting opportunity is not a yield predictor, and was never meant to be.** It measures how often the
   weather permitted a crop, not how well that crop would have done. Yield in these systems is dominated by
   nitrogen, soil fertility and management (Ichami et al. 2018: < 33 % of fertilizer-response variation
   explained even *with* soil, climate and management data; 18 % of plots non-responsive). Grouping yields
   by a weather index and finding weak separation is the expected result, not a finding about MPOU.
2. **A 30-year climatology cannot be tested against year-to-year yields.** Opportunity days are a single
   cross-sectional count per pixel, whereas the yield record varies mostly between years. Marcos-Garcia et
   al. (2024) show where the weather signal actually lives: intra-season dry–wet spell *pattern* explains
   50–60 % of interannual maize yield variation in sub-Saharan Africa, against 30–35 % for seasonal means.
   MPOU throws away exactly that per-season dimension when it sums to one number.
3. **Majority-zone aggregation destroys the signal MPOU resolves.** Assigning one modal zone to a whole
   admin-1 region discards within-region variation — the variation the 0.25° map exists to show — and then
   asks the zone to explain a region-mean yield.
4. **GYGA is the wrong yardstick.** GYGA's climate zones were built to **upscale simulated yield
   *potential*** from weather stations to regions (van Wart et al. 2013), not to explain observed yields.
   Technology extrapolation domains — the framing MPOU was conceived against — are explicitly for deciding
   **where an agronomic result transfers**, not for predicting yield level (Rattalino Edreira et al. 2018).
   Scoring both schemes on yield homogeneity judges them by a criterion neither was designed to satisfy, so
   "comparable to GYGA" is close to uninformative.

### Better tests, in order of what I would do first

1. **Validate the window, not the level.** MPOU's strongest claim is *when* planting is viable — and the
   report already shows this working qualitatively: the Malawi day-of-year figure puts the window at
   mid-November to mid-February, matching the local crop calendar. Make it quantitative against observed
   planting dates: crop calendars (Sacks et al. 2010), satellite-derived sowing dates (Rezaei et al. 2020),
   or national crop calendars. The precedent to copy is Black et al. (2023), who validated the TAMSAT-ALERT
   planting-date tool against **more than 30,000 observed planting dates and yields** across Kenya, Rwanda,
   Uganda, Zambia and Malawi, and found farmers planting near the recommendation obtained 7–10 % higher
   yields. That is a defensible evaluation of exactly the quantity MPOU produces.
2. **Go per-season and test anomalies.** Compute viable days per pixel per season and regress detrended
   yield anomalies on them. This tests the mechanism MPOU claims, in the dimension where weather dominates
   (Marcos-Garcia et al. 2024), and it needs no new code — only that `summarize` not collapse the time axis.
3. **Test the extremes, not the mean.** Ask whether seasons with no or very few viable days coincide with
   declared crop failures. This is the early-warning framing of Becker-Reshef et al. (2020), and failure
   years are where a weather-only model should perform best.
4. **Test it as a stratification layer, on the TED criterion.** Do agronomic trial results transfer better
   within MPOU zones than within GYGA zones? That is the question TEDs are evaluated on (Rattalino Edreira
   et al. 2018), and it is the use MPOU was designed for.

## 5. What MPOU is actually good for

Framed as "when can maize be planted here, and how reliably", rather than "how much maize grows here":

- **Planting-window advisories and decision-support input.** The per-day viability series is the natural
  input to the kind of tool Black et al. (2023) validated.
- **Variety and maturity-class targeting.** The season-length layer is directly comparable to the thermal
  requirement of a maturity class, so MPOU can say which maturity class fits where — a use the current
  fixed-2400 GDD parameterisation actively obstructs (§ 2.7) and which multiple runs would unlock.
- **Trial-site selection and scaling-out domains.** The TED use case: where can this result be extrapolated?
- **Risk products.** The frequency of near-zero-opportunity seasons is a climatological risk measure, usable
  for early warning or index insurance design, and it uses the tail of the distribution rather than the mean.
- **Climate-change diagnosis.** Recomputing over moving windows shows whether the planting window is
  shifting, narrowing or becoming less reliable — a question the layers answer natively, and one where
  Lobell et al. (2011) establishes the stakes.
- **A sampling frame for ground data.** Becker-Reshef et al. (2023) note that Africa is precisely where
  recent crop-type ground data is missing; a crop-specific agroclimatic stratification is useful for
  allocating collection effort.

## 6. Ranked changes for v1.1.0

1. **Add a heat test at anthesis** (§ 2.1). Largest gain per unit of work; the anthesis date is already
   computed; the 45 °C daily-mean ceiling is currently inert.
2. **Fix season length's −1 contamination** (§ 1.2) — it corrupts a raw layer that is in use.
3. **Settle 842 vs 2400 and the base temperature** (`references.md` § 4.1, § 4.2). Until then the two GDD
   parameters do not describe one variety.
4. **Re-validate on the window, per season** (§ 4, tests 1 and 2), and stop reporting the GYGA yield-spread
   comparison as the headline evaluation.
5. **Sensitivity-test the rainfall thresholds against a gauge-calibrated product** (§ 3.1), then decide
   whether 1 mm / 20 mm / 450 mm survive.
6. Then the rest: soil water holding capacity (§ 2.3), an excess-water penalty (§ 2.4), the binning
   overflow and the dry-spell offset (§ 1.1, § 1.3), multiple maturity classes (§ 2.7).
