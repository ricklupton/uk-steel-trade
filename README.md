Indirect trade of steel through steel-containing components and products, from
1978 to 2017.

## TODO

- Add first stage to automatically download the data from COMTRADE

## Data

Data on trade in goods between the UK and the rest of the world are supplied
from the UN COMTRADE database. For ease of comparison across years, we use the
old SITC version 2 classification, which is available for data from the present
(ready-recategorised by COMTRADE) back to 1978.

We have mapped each SITC code onto the 20 sectors used by the ISSB statistics.
Each code is assigned or split between *components* and *final goods*, and given
an average steel content (in kg steel per kg product)

## License

TBC Comtrade licence

## Preparation

TODO Run the script to download the data file from COMTRADE
`raw_data/comtrade_trade_data.csv`.

To aggregate the trade flows and find iron contents:

```python
python scripts/aggregate_trade_flows.py
```

This creates the `data/imports.csv` and `data/exports.csv` files.
