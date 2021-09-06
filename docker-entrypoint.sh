#!/bin/bash

mkdir key
python kengen.py

nginx &

exec "$@"
