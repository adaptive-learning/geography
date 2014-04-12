#!/bin/bash
SELF=$0
SELF_DIR=`dirname $SELF`
if [ $GEOGRAPHY_WORKSPACE_DIR ]; then
	WORKSPACE_DIR=$GEOGRAPHY_WORKSPACE_DIR;
else
	WORKSPACE_DIR=$SELF_DIR/..
fi
APP_DIR="$WORKSPACE_DIR/main"
if [ "$GEOGRAPHY_DATA_DIR" ]; then
	DATA_DIR="$GEOGRAPHY_DATA_DIR"
else
	DATA_DIR="$APP_DIR"
fi

for MODEL in place placerelation answer answer_options answer_ab_values ab_value ab_group placerelation_related_places; do
	$APP_DIR/manage.py table2csv geography_$MODEL ${DATA_DIR}/geography.$MODEL.csv
	zip --junk-paths ${DATA_DIR}/geography.$MODEL.zip ${DATA_DIR}/geography.$MODEL.csv
	rm -rf ${DATA_DIR}/geography.$MODEL.csv
done
