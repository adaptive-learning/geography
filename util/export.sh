#!/bin/bash
SELF=`readlink -f $0`
SELF_DIR=`dirname $SELF`

APP_DIR="$SELF_DIR/../main"
if [ "$GEOGRAPHY_DATA_DIR" ]; then
	DATA_DIR="$GEOGRAPHY_DATA_DIR"
else
	DATA_DIR="$APP_DIR"
fi

for MODEL in place placerelation answer answer_options; do
	$APP_DIR/manage.py table2csv geography_$MODEL ${DATA_DIR}/geography.$MODEL.csv
	zip --junk-paths ${DATA_DIR}/geography.$MODEL.zip ${DATA_DIR}/geography.$MODEL.csv
	rm -rf ${DATA_DIR}/geography.$MODEL.csv
done
