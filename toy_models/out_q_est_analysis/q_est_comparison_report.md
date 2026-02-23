# Q_est comparison against prior runner outputs

Inputs:
- q_est: `toy_models/out_sparc_runs_full_with_composition/q_est.csv`
- summary: `toy_models/out_sparc_runs_full_with_composition/summary.csv`

## Join integrity
- Joined galaxies: 175

## Sanity counts
- q_est < 0: 2
- v_est_asym = sqrt(max(q_est,0)) is NaN (due to q_est<=0 or missing): 2

## Q-space comparison (q_est_kms2 vs q_best_kms2)
- Pearson r: 0.8714
- Spearman ρ: 0.9729
- Theil–Sen fit: q_est ≈ a + b·q_best with a=-493.1, b=1.014
- Δq = q_est − q_best: median=-370.9, MAD=966.5
- log10(q_est/q_best) (positive ratios only): median=-0.04051

## v-space comparison (v_est_asym_kms vs v_extra_asym_kms)
- Pearson r: 0.9485
- Spearman ρ: 0.972
- Theil–Sen fit: v_est ≈ a + b·v_extra with a=-7.043, b=1.042
- Δv = v_est − v_extra: median=-3.364, MAD=6.465

## Differences by outer selection rule
- `lastfrac`: n=73, median(Δq)=-806.8, MAD(Δq)=738.4; median(Δv)=-6.31, MAD(Δv)=5.291
- `rfrac`: n=102, median(Δq)=-67.02, MAD(Δq)=1310; median(Δv)=-0.3428, MAD(Δv)=6.013

## Largest |Δv| robust outliers
(Ranked by |robust z| on Δv)

|rank|galaxy|Δv (km/s)|
|---:|---|---:|
|1|UGC11914|-185.6|
|2|ESO563-G021|48.75|
|3|UGC06614|43.19|
|4|NGC5005|-47.09|
|5|NGC3521|-45.46|
|6|NGC3726|36.62|
|7|NGC3949|-36.38|
|8|UGC05750|-36.26|
|9|UGC09037|29.26|
|10|UGC02916|-33.85|

## Files written
- `toy_models/out_q_est_analysis\q_est_joined_summary.csv`
- `toy_models/out_q_est_analysis\q_est_comparison_report.md`
