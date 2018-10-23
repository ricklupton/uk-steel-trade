import pandas as pd

from logzero import logger
import os
import os.path

logger.info('Starting %s', os.path.basename(__file__))

# Load the trade data
trade = pd.read_csv('raw_data/comtrade_trade_data.csv')

def check_values(df, column, value):
    msg = 'Expected "%s" column to be %r' % (column, value)
    assert all(df[column] == value), msg

# Check that it has the expected data
check_values(trade, 'Reporter', 'United Kingdom')
check_values(trade, 'Partner', 'World')

# Load the allocation table and category iron contents
alloc = pd.read_csv('scripts/SITC_allocation.csv', index_col='SITC_code')
cats = pd.read_csv('scripts/steel_contents.csv', index_col=0)

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
    .join(alloc, on='Commodity Code', how='outer') \
    .join(cats, on='sector_code') \
    .dropna(subset=['sector_code']) \
    .rename(columns={'Period': 'year',
                     'Trade Flow': 'direction'})

# Convert kg to kt and add in the category iron contents. `multiplier` is for
# sharing an HS4-flow between multiple sector-flows
table['mass'] = table['NetWeight (kg)'] * table['multiplier'] / 1e6
table['mass_iron'] = table['mass'] * table['iron_content']

os.makedirs('checking', exist_ok=True)
table.to_csv('checking/checking_table.csv', index=False)

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
df = agg.set_index('direction')
df = df[['sector_code', 'sector_group', 'sector_name', 'stage', 'year',
         'iron_content', 'mass', 'mass_iron']]
df['year'] = df['year'].astype(int)
df['iron_content'] = df['iron_content'].round(2)
df['mass'] = df['mass'].round(1)
df['mass_iron'] = df['mass_iron'].round(1)

df.loc['Import'].to_csv('data/imports.csv', index=False)
df.loc['Export'].to_csv('data/exports.csv', index=False)
