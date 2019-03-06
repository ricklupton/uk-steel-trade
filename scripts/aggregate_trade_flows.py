#!/usr/bin/env python

"""Load COMTRADE data, aggregate and calculate steel contents.

Usage:
  aggregate_trade_flows.py --allocation ALLOCATION-FILE --steel-contents CONTENTS-FILE COMTRADE-FILE...

Options:
  --allocation ALLOCATION-FILE      CSV file with mappings from SITC v2 codes to product categories
  --steel-contents CONTENTS-FILE    CSV file with steel contents for each category
"""

import os
import os.path
import json
import pandas as pd
from logzero import logger
from docopt import docopt

logger.info('Starting %s', os.path.basename(__file__))


def load_file(filename):
    """Load one JSON file from UN COMTRADE."""
    with open(filename, 'rt') as f:
        d = json.load(f)
    return pd.DataFrame.from_records(d['dataset'])


def load_all_data(files):
    """Load all the given JSON files."""
    return pd.concat([load_file(file) for file in files], ignore_index=True)


def overwrite_data(trade, code, flow, years):
    ii = ((trade['cmdCode'] == code) &
          (trade['period'].isin(years)) &
          (trade['rgDesc'] == flow))
    assert sum(ii) > 0, 'No matches!'
    new_value = trade['NetWeight'][ii & (trade['period'] == years[0])].iloc[0]
    logger.debug('overwriting %s %s for %s to %s', code, flow, years, new_value)
    trade.loc[ii, 'NetWeight'] = new_value


def check_values(df, column, value):
    msg = 'Expected "%s" column to be %r' % (column, value)
    assert all(df[column] == value), msg


def main(files, alloc_filename, contents_filename):
    # Load the trade data
    trade = load_all_data(files)

    # Apply "corrections"
    overwrite_data(trade, '69402', 'Import', [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007])
    overwrite_data(trade, '874', 'Import', [1999, 2000])

    # Check that it has the expected data
    check_values(trade, 'rt3ISO', 'GBR')
    check_values(trade, 'pt3ISO', 'WLD')

    # Load the allocation table and category iron contents
    alloc = pd.read_csv(alloc_filename, index_col='SITC_code')
    cats = pd.read_csv(contents_filename, index_col=0)

    # Validate allocations
    mult_sums = alloc['multiplier'].groupby('SITC_code').sum()
    assert all((mult_sums == 0) | (mult_sums == 1)), 'Multipliers must sum to 0 or 1'
    split_allocs = alloc[(alloc['multiplier'] != 0) &
                        (alloc['multiplier'] != 1) &
                        ~pd.isnull(alloc['multiplier'])]
    logger.debug('Split allocations:\n' +
                str(split_allocs[['sector_code', 'stage', 'multiplier']]))

    # Join the table and aggregate
    table = trade \
        .join(alloc, on='cmdCode', how='outer') \
        .join(cats, on='sector_code') \
        .dropna(subset=['sector_code']) \
        .rename(columns={'period': 'year',
                        'rgDesc': 'direction'})

    # Convert kg to kt and add in the category iron contents. `multiplier` is for
    # sharing an HS4-flow between multiple sector-flows
    table['mass'] = table['NetWeight'] * table['multiplier'] / 1e6
    table['mass_iron'] = table['mass'] * table['iron_content']

    os.makedirs('build', exist_ok=True)
    table.to_csv('build/checking_table.csv', index=False)

    agg = table \
        .groupby(['direction', 'sector_code', 'stage', 'year'], as_index=False) \
        .agg({
            'mass': 'sum',
            'mass_iron': 'sum',
            'sector_group': 'first',  # same in each group of sector_codes
            'sector_name': 'first',
            'iron_content': 'first',
        })


    # Save
    df = agg[['sector_code', 'sector_group', 'sector_name', 'direction',
              'stage', 'year', 'iron_content', 'mass', 'mass_iron']]
    df['year'] = df['year'].astype(int)
    df['iron_content'] = df['iron_content'].round(2)
    df['mass'] = df['mass'].round(1)
    df['mass_iron'] = df['mass_iron'].round(1)
    df['direction'] = df['direction'].str.lower()

    df.to_csv('data/trade.csv', index=False)


if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)
    main(files=args['COMTRADE-FILE'],
         alloc_filename=args['--allocation'],
         contents_filename=args['--steel-contents'])
