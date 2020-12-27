#!/usr/bin/env python
# coding: utf_8
import os
import csv, sqlite3
import unicodedata
from postal_code import PostalCode as ps


def main():
    ps.add_fulladdr(incomplete_csv="./郵便番号のみの住所.csv", output_csv="./郵便番号と住所.csv")


if __name__ == "__main__":
    main()
