#!/usr/bin/bash

if [[ ! -f "naev.6" ]]; then
   echo "Please run from Naev root directory."
   exit -1
fi

set -x

TMPFILE=$(mktemp)

echo "src/log.h" > "$TMPFILE"
find src/ -name "*.c" | sort >> "$TMPFILE"
find dat/ -name "*.lua" | sort >> "$TMPFILE"
#echo "dat/commodity.xml" >> "$TMPFILE"

cat "$TMPFILE" | sort > po/POTFILES.in

