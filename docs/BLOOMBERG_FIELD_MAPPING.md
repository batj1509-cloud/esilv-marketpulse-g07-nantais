# Bloomberg Field Mapping

## Access mode

`APPROVED_SAMPLE`

La source utilisée est l’[échantillon pédagogique fourni](../data/sample/bloomberg_reference_sample.json). Le fichier identifie ses valeurs comme des exemples issus du CSV de cours. La connexion à Bloomberg en direct reste à démontrer. Les clés décrites ci-dessous appartiennent au format pédagogique. Les noms de champs Bloomberg en mode LIVE restent à vérifier dans l’environnement de cours.

L’[énoncé du TD09](../labs/TD09_BLOOMBERG_INTRODUCTION.md) indique le fichier complémentaire `docs/10_BLOOMBERG_INSTRUCTOR_REFERENCE.md`, absent de la base du dépôt utilisée pour ce TD. La correspondance est vérifiée avec le [résultat canonique fourni](../data/sample/bloomberg_reference_expected.json).

## Market instruments

| Rôle | Ticker MarketPulse | Identifiant Bloomberg dans l’échantillon |
|---|---|---|
| Instrument | `AAPL` | `AAPL US Equity` |
| Indice de référence | `SP500` | `SPX Index` |

Le tableau JSON `series` contient les deux séries. Chaque entrée renseigne `role`, `canonical_ticker`, `provider_identifier` et un tableau `observations`. Chaque série compte 21 observations quotidiennes du 1er au 30 septembre 2026, sur les mêmes dates.

| Série inspectée | Date | Ouverture | Plus haut | Plus bas | Clôture | Volume |
|---|---|---:|---:|---:|---:|---:|
| `AAPL US Equity` | `2026-09-01` | 249,20 | 251,50 | 248,00 | 250,00 | 38 000 000 |
| `SPX Index` | `2026-09-01` | 6 592 | 6 615 | 6 580 | 6 600 | 0 |

## Field mapping

| Champ MarketPulse | Source dans l’échantillon | Type et règle |
|---|---|---|
| `date` | `observations[].observation_date` | Chaîne ISO `YYYY-MM-DD`, conservée telle quelle. |
| `ticker` | `series[].canonical_ticker` | Chaîne copiée de la série parente dans chaque observation. |
| `open` | `observations[].open_value` | Nombre converti en `float`. |
| `high` | `observations[].high_value` | Nombre converti en `float`. |
| `low` | `observations[].low_value` | Nombre converti en `float`. |
| `close` | `observations[].close_value` | Nombre converti en `float`. |
| `volume` | `observations[].volume_value` | Entier. Pour `SP500`, les 21 observations de l’échantillon contiennent explicitement `0`. |

Les 42 observations contiennent les six clés attendues et des valeurs renseignées. Le volume nul de l’indice est une valeur de l’échantillon, à conserver dans le résultat canonique.

## TD10 handoff

En mode `APPROVED_SAMPLE`, parcourir les observations de `AAPL US Equity` et de `SPX Index` dans le JSON, en conservant les tickers `AAPL` et `SP500`. Produire une ligne par observation avec les sept champs du tableau et comparer les lignes au [résultat canonique attendu](../data/sample/bloomberg_reference_expected.json). Les fonctions d’alignement par date et de comparaison du TD7 peuvent alors consommer ces lignes directement. Les règles de traitement des champs manquants en mode LIVE restent à établir à partir d’une réponse observée.
