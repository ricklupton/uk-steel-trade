#!/usr/bin/env python

"""Download COMTRADE data from the API and save to disk.

Usage:
  download_comtrade_data.py YEAR FILENAME

Copyright 2019 Richard Lupton
"""


from docopt import docopt
import json
import requests
from logzero import logger


# Reporter 826 == United Kingdom
URL_PATTERN = 'https://comtrade.un.org/api/get?max={max}&freq=A&px=S2&ps={year}&r=826&p=0&rg=all&cc=all&fmt=json'

# Maximum number of results that can be returned.
MAX_COUNT = 50000


def build_url(year):
    return URL_PATTERN.format(
        year=year,
        max=MAX_COUNT,
    )


def download_year(year, output_filename):
    """Download data for one year, check and save as JSON."""

    url = build_url(year)
    logger.info('Downloading %s', url)
    r = requests.get(url)
    logger.info('Response: %s', r.status_code)
    data = r.json()

    # Do some checks...
    check_data(data, year)
    logger.info('Checks passed')

    # Save the result
    with open(output_filename, 'wt') as f:
        json.dump(data, f)
    logger.info('Data written to %s', output_filename)


def check_data(data, year):
    val = data['validation']

    if val['status']['name'] != 'Ok':
        raise ValueError('Unsuccessful query: %r' % val['status'])

    if val['count']['value'] >= MAX_COUNT:
        raise ValueError('Too many results found -- some data is missing.')

    records = data['dataset']
    if records:
        r = records[0]
        assert r['rt3ISO'] == 'GBR'  # reporter
        assert r['pt3ISO'] == 'WLD'  # partner
        assert r['yr'] == year


if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)
    year = int(args['YEAR'])
    download_year(year, args['FILENAME'])
