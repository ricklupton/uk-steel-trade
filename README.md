[![goodtables.io](https://goodtables.io/badge/github/ricklupton/uk-steel-trade.svg)](https://goodtables.io/github/ricklupton/uk-steel-trade)

Indirect trade of steel through steel-containing components and products, from
1978 to 2017.

This repository is a [Data Package](https://frictionlessdata.io/data-packages/):
use the viewer to [browse the metadata and
data](https://data.okfn.org/tools/view?url=https%3A%2F%2Fgithub.com%2Fricklupton%2Fuk-steel-trade).

## Data

Data on trade in goods between the UK and the rest of the world are supplied
from the UN COMTRADE database. For ease of comparison across years, we use the
old SITC version 2 classification, which is available for data from the present
(ready-recategorised by COMTRADE) back to 1978.

We have mapped each SITC code onto the 20 sectors used by the ISSB statistics.
Each code is assigned or split between *components* and *final goods*, and given
an average steel content (in kg steel per kg product)

## Uses

This data was prepared for the *TBC report details*.

## Contributing

Corrections and improvements are welcome! Please [get in
touch](https://ricklupton.name), or open an issue or a pull request.

## License

[![Creative Commons License](https://i.creativecommons.org/l/by/3.0/88x31.png)](http://creativecommons.org/licenses/by/3.0)

This work is licensed under a [CC-BY
License](http://creativecommons.org/licenses/by/3.0/). Please attribute it as follows:

```
Richard Lupton and André Cabrera Serrenho. *UK steel trade flows*. DOI: TBC.
```

## Preparation

Run the scripts to download and prepare the COMTRADE data using Make:

```
make
```

This will:
- Download the raw data to `build/raw_data`
- Output detailed tables to `build/checking_table.csv`
- Write the aggregated import and exports data to `data/imports.csv` and
  `data/exports.csv`.
