#!/usr/bin/env python
# coding: utf_8
import os
import sys
import csv, sqlite3
import unicodedata
from postal_code import PostalCode as ps


def main():
    args = sys.argv[1:]
    for csv in args:
        ps.add_fulladdr(incomplete_csv=csv, output_csv="住所付き_" + csv)


if __name__ == "__main__":
    main()
