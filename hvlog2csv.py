#!/usr/bin/env python3
'''
Convert whitespace separated data to CSV-file.

The first column supposed to be a timestamp. 
Skip a sequence of the same data with different timestamps,
but keep the last one of the sequence when data changes. 

'''

import fileinput

OFS = ';'  # Output field separator

last = []
pr_last = False


def prvals(vals):
    try:
        print(OFS.join(vals))
    except BrokenPipeError:
        exit(1)


for line in fileinput.input():
    vals = line.split()
    
    if vals[1:] == last[1:]:  # Are the same but timestamp
        pr_last = True

    else:
        if pr_last is True:  # Print the last value in sequence
            pr_last = False
            prvals(last)
        prvals(vals)
    #
    last = vals

if pr_last is True:
    prvals(last)  # always print the last one


