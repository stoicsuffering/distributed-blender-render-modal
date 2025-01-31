#!/bin/bash

gdb --batch \
  -ex "set pagination off" \
  -ex "run" \
  -ex "bt" \
  -ex "quit" \
  --args python3.11 /opt/debug_eevee.py -- $1