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

export_table() {
	echo $1
	echo $2
	$APP_DIR/manage.py table2csv $1 ${DATA_DIR}/$2.csv
	zip --junk-paths ${DATA_DIR}/$2.zip ${DATA_DIR}/$2.csv
	rm -rf ${DATA_DIR}/$2.csv
}

for MODEL in place placerelation answer answer_options answer_ab_values ab_value ab_group placerelation_related_places; do
	export_table geography_$MODEL geography.$MODEL;
done

for MODEL in rating; do
	export_table proso_feedback_$MODEL feedback.$MODLE;
done
