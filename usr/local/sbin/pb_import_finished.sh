#!/bin/bash
DEVICE=$1
TMPFILEPATH="/tmp/phoniebox"

rm "$TMPFILEPATH/export_$DEVICE"
rm "$TMPFILEPATH/import_$DEVICE"

exit 0