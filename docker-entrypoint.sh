#!/bin/bash
python kengen.py
nginx &
exec "$@"
