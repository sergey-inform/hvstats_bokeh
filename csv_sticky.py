#!/usr/bin/env python3
""" 
Output values only when they change for more than desired threshold,
or certain time passed (aka low-pass filter for poor).

The first column is a timestamp.
"""

import fileinput
import sys

THRESH = 0.5


IFS = ';'  # Input field separator
NONES = ["none", "-", "n/a"]
prev_val = 0.0
prev_ts = None


def prline(line):
    try:
        sys.stdout.write(line)
    except BrokenPipeError:
        exit(1)


with fileinput.input() as input:
    for line in input:
        ts, val = line.strip().split(IFS)
        try:
            val = float(val)
        except ValueError:
            if val.lower() in NONES:
                continue
            else:
                raise

        if abs(val - prev_val) > THRESH:
            prline(line)
            prev_val = val
            prev_ts = ts

if ts != prev_ts:
    prline(line)

        
    

