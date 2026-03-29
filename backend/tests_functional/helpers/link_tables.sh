#!/bin/sh
# Creates a soft link for the SQLAlchemy tables file in the test environment

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RELATIVE_PATH="../../database"
TABLES_FILE="tables.py"
SRC_FILE="$RELATIVE_PATH/$TABLES_FILE"
LN_FILE="$SCRIPT_DIR/$TABLES_FILE"

if [ -f "$LN_FILE" ] && [ ! -L "$LN_FILE" ]; then
  echo "$TABLES_FILE already exists as a regular file, skipping soft link creation"
elif [ -L "$LN_FILE" ]; then
  ln -s -f -- "$SRC_FILE" "$LN_FILE"
  echo "Recreated $TABLES_FILE link"
else
  ln -s -- "$SRC_FILE" "$LN_FILE"
  echo "Created $TABLES_FILE link"
fi
