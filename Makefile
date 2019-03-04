
# These are the years of data to download
YEARS := $(shell seq 1978 2017)

COMTRADE_TARGETS := $(foreach year,$(YEARS),build/raw_data/comtrade_data_$(year).json)

FINAL_TARGETS = data/imports.csv data/exports.csv

ALLOC_FILENAME = definitions/SITC_allocation.csv
CONTENTS_FILENAME = definitions/steel_contents.csv
PARAMETER_FILES = $(ALLOC_FILENAME) $(CONTENTS_FILENAME)

LOG_FILE = build/log.log

all: $(COMTRADE_TARGETS) $(FINAL_TARGETS)

# Rule for downloading data files
build/raw_data/comtrade_data_%.json:
	mkdir -p build/raw_data
	pipenv run scripts/download_comtrade_data.py $* $@ >> $(LOG_FILE) 2>&1


$(FINAL_TARGETS): $(COMTRADE_TARGETS) $(PARAMETER_FILES)
	mkdir -p data
	pipenv run scripts/aggregate_trade_flows.py --allocation $(ALLOC_FILENAME) --steel-contents $(CONTENTS_FILENAME) $(COMTRADE_TARGETS) >> $(LOG_FILE) 2>&1
