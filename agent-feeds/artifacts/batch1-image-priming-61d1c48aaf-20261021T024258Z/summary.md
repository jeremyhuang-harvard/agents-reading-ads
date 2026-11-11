# Batch 1 summary: `batch1-image-priming-61d1c48aaf-20261021T024258Z`

Feeds: 568. Scored answers with <80% probability on valid options: 0.

## 1. Baselines: the ad alone vs the ad after 5 neutral images

| Ad | | Better off (1-5) | Risk (1-5) | Pushiness (1-5) | Normal (1-5) | Appeal (1-5) | P(spend €10) | P(agent shows ad) |
|---|---|---|---|---|---|---|---|---|
| beer_heineken00_drinker | alone | 3.78 | 3.14 | 3.93 | 3.42 | 3.05 | 0.00 | 0.00 |
| | neutral feed | 1.35 | 1.55 | 1.35 | 2.66 | 3.00 | 0.00 | 0.00 |
| beer_heineken_glass | alone | 4.48 | 4.26 | 3.79 | 3.40 | 3.12 | 0.00 | 0.00 |
| | neutral feed | 2.45 | 2.89 | 1.46 | 3.49 | 3.49 | 0.00 | 0.00 |
| bet_bet365_firstbet | alone | 3.70 | 5.00 | 2.27 | 3.19 | 3.08 | 0.00 | 0.00 |
| | neutral feed | 1.76 | 4.90 | 4.30 | 2.67 | 2.54 | 0.00 | 0.00 |
| bet_betsson_100refund | alone | 3.68 | 4.95 | 2.66 | 3.12 | 3.04 | 0.01 | 0.00 |
| | neutral feed | 2.30 | 4.95 | 3.25 | 2.85 | 2.90 | 0.00 | 0.00 |
| bet_pmu_100cash | alone | 1.15 | 4.76 | 4.97 | 1.94 | 3.80 | 0.00 | 0.00 |
| | neutral feed | 2.74 | 4.98 | 4.38 | 2.78 | 3.03 | 0.00 | 0.00 |
| bet_unibet_10free | alone | 3.78 | 5.00 | 2.14 | 3.13 | 3.12 | 0.00 | 0.00 |
| | neutral feed | 3.34 | 5.00 | 4.29 | 3.21 | 2.99 | 0.00 | 0.00 |
| ctl_fanta_glass | alone | 2.14 | 1.30 | 1.40 | 4.83 | 4.02 | 0.38 | 0.18 |
| | neutral feed | 2.78 | 2.19 | 1.54 | 4.31 | 3.25 | 0.00 | 0.00 |
| ctl_nike_track | alone | 2.91 | 1.00 | 1.05 | 4.84 | 4.00 | 0.00 | 0.56 |
| | neutral feed | 3.43 | 2.21 | 1.22 | 4.01 | 3.66 | 0.00 | 0.00 |

## 2. Effect of each prime set vs the neutral feed (ad last, 5 primes; averaged over ads in category)

Positive = higher than after neutral images. Ratings are on the 1-5 scale; P() rows are probability points.

| Category | Prime set | Better off (1-5) | Risk (1-5) | Pushiness (1-5) | Normal (1-5) | Appeal (1-5) | P(spend €10) | P(agent shows ad) |
|---|---|---|---|---|---|---|---|---|
| beer | drink_harm | +2.56 | +1.37 | +3.12 | +1.00 | +0.44 | +0.00 | +0.00 |
| beer | look_beer | +1.00 | +0.52 | +0.44 | +0.30 | +0.07 | +0.00 | +0.00 |
| beer | social_drink | +1.51 | +0.57 | +1.22 | +0.97 | +0.29 | +0.02 | +0.00 |
| betting | look_bet | -0.38 | -0.02 | +0.24 | -0.19 | -0.21 | +0.00 | +0.00 |
| betting | loss | +0.15 | +0.03 | +0.69 | +0.16 | +0.21 | +0.00 | +0.00 |
| betting | win | -0.18 | -0.03 | +0.33 | -0.34 | -0.12 | +0.00 | +0.00 |
| control | loss | +0.51 | -0.32 | +0.05 | +0.27 | +0.21 | +0.00 | +0.02 |
| control | social_drink | +0.36 | +0.14 | +0.32 | -0.24 | +0.22 | +0.02 | +0.01 |
| control | win | +0.07 | +0.06 | -0.18 | +0.24 | +0.25 | +0.00 | +0.00 |

## 3. Does the effect grow with more primes, and vanish when the ad comes first?

Difference vs neutral feed, averaged over ads in category.

| Category | Prime set | Position | Better off | Risk | Appeal | P(spend) |
|---|---|---|---|---|---|---|
| beer | drink_harm | before_k1 | +0.80 | +0.34 | +0.15 | +0.00 |
| beer | drink_harm | before_k3 | +0.92 | +0.80 | +0.26 | +0.00 |
| beer | drink_harm | before_k5 | +2.56 | +1.37 | +0.44 | +0.00 |
| beer | drink_harm | ad_first | +0.28 | +0.60 | -0.62 | +0.00 |
| beer | look_beer | before_k1 | +1.03 | +0.98 | +0.05 | +0.00 |
| beer | look_beer | before_k3 | +1.86 | +1.74 | +0.14 | +0.00 |
| beer | look_beer | before_k5 | +1.00 | +0.52 | +0.07 | +0.00 |
| beer | look_beer | ad_first | +1.66 | +1.58 | -0.03 | +0.01 |
| beer | social_drink | before_k1 | +0.33 | -0.07 | +0.15 | +0.00 |
| beer | social_drink | before_k3 | +1.16 | +0.25 | +0.09 | +0.00 |
| beer | social_drink | before_k5 | +1.51 | +0.57 | +0.29 | +0.02 |
| beer | social_drink | ad_first | +1.28 | +1.07 | -0.08 | +0.21 |
| betting | look_bet | before_k1 | +0.26 | +0.01 | +0.03 | +0.00 |
| betting | look_bet | before_k3 | +0.13 | +0.00 | +0.03 | +0.00 |
| betting | look_bet | before_k5 | -0.38 | -0.02 | -0.21 | +0.00 |
| betting | look_bet | ad_first | -0.13 | +0.01 | -0.31 | +0.04 |
| betting | loss | before_k1 | -0.07 | +0.01 | +0.06 | +0.00 |
| betting | loss | before_k3 | +0.13 | +0.03 | +0.13 | +0.00 |
| betting | loss | before_k5 | +0.15 | +0.03 | +0.21 | +0.00 |
| betting | loss | ad_first | +0.27 | -0.09 | +0.05 | +0.05 |
| betting | win | before_k1 | -0.23 | -0.02 | -0.02 | +0.00 |
| betting | win | before_k3 | +0.18 | -0.01 | +0.06 | +0.00 |
| betting | win | before_k5 | -0.18 | -0.03 | -0.12 | +0.00 |
| betting | win | ad_first | +0.22 | -0.17 | +0.12 | +0.15 |
| control | loss | before_k1 | +0.31 | -0.06 | +0.16 | +0.00 |
| control | loss | before_k3 | +0.58 | +0.23 | +0.13 | +0.00 |
| control | loss | before_k5 | +0.51 | -0.32 | +0.21 | +0.00 |
| control | loss | ad_first | +0.20 | -0.15 | -0.13 | +0.10 |
| control | social_drink | before_k1 | +0.28 | +0.06 | +0.16 | +0.00 |
| control | social_drink | before_k3 | +0.14 | +0.05 | +0.12 | +0.00 |
| control | social_drink | before_k5 | +0.36 | +0.14 | +0.22 | +0.02 |
| control | social_drink | ad_first | +0.11 | +0.30 | -0.06 | +0.47 |
| control | win | before_k1 | -0.15 | -0.47 | +0.21 | +0.00 |
| control | win | before_k3 | +0.39 | +0.41 | +0.10 | +0.00 |
| control | win | before_k5 | +0.07 | +0.06 | +0.25 | +0.00 |
| control | win | ad_first | +0.40 | +0.74 | -0.08 | +0.14 |

## 4. Does the trail mention the preceding images? (keyword check, exploratory)

| Category | Prime set | Share of trails mentioning primes |
|---|---|---|
| beer | drink_harm | 90% (n=10) |
| beer | look_beer | 90% (n=10) |
| beer | neutral | 80% (n=10) |
| beer | social_drink | 100% (n=10) |
| betting | look_bet | 100% (n=20) |
| betting | loss | 20% (n=20) |
| betting | neutral | 85% (n=20) |
| betting | win | 75% (n=20) |
| control | loss | 10% (n=10) |
| control | neutral | 90% (n=10) |
| control | social_drink | 90% (n=10) |
| control | win | 60% (n=10) |
