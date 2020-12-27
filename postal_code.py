#!/usr/bin/env python
# coding: utf_8
import os
import csv, sqlite3
import unicodedata
import pdb

# 0 全国地方公共団体コード
# 1 旧郵便番号
# 2 郵便番号
# 3 都道府県名
# 4 市区町村名
# 5 町域名
# 6 都道府県名
# 7 市区町村名
# 8 町域名
# 9 一町域が二以上の郵便番号で表される場合の表示 (注3) (「1」は該当、「0」は該当せず)
# 10 小字毎に番地が起番されている町域の表示 (注4) (「1」は該当、「0」は該当せず)
# 11 丁目を有する町域の場合の表示 (「1」は該当、「0」は該当せず)
# 12 一つの郵便番号で二以上の町域を表す場合の表示 (注5) (「1」は該当、「0」は該当せず)
# 13 更新の表示(注6)(「0」は変更なし、「1」は変更あり、「2」廃止(廃止データのみ使用))
# 14 変更理由(「0」は変更なし、「1」市政・区政・町政・分区・政令指定都市施行、「2」住居表示の実施、「3」区画整理、「4」郵便区調整等、「5」訂正、「6」廃止(廃止データのみ使用))


class PostalCode:
    def make_db(
        ken_all_csv="./assets/KEN_ALL.CSV", postalcode_sqlite3="./postalcode.sqlite3"
    ):
        if os.path.isfile(postalcode_sqlite3):
            os.remove(postalcode_sqlite3)
        # SQLite3のデータベースを開く --- (*1)
        conn = sqlite3.connect(postalcode_sqlite3)
        c = conn.cursor()
        # テーブルを作る --- (*2)
        c.execute(
            """CREATE TABLE zip (
            postc text, pref text, prefr text, city text, cityr text, addr text, addrr text)"""
        )
        c.execute("begin")
        # CSVファイルを開く
        with open(ken_all_csv, "rt", encoding="Shift_JIS") as fp:
            # CSVを読み込む
            reader = csv.reader(fp)
            # 一行ずつ処理する
            for row in reader:
                postc = row[2]  # 郵便番号
                prefr = unicodedata.normalize("NFKC", row[3])  # 都道府県名(読み),
                cityr = unicodedata.normalize("NFKC", row[4])  # 市区町村名(読み),
                addrr = unicodedata.normalize("NFKC", row[5])  # 町域名(読み),
                pref = row[6]  # 都道府県名
                city = row[7]  # 市区町村名
                addr = row[8]  # 町域名
                if addr == "以下に掲載がない場合":
                    addr = ""
                # SQLiteに追加 --- (*3)
                c.execute(
                    """INSERT INTO zip (postc,pref,prefr,city,cityr,addr,addrr)
                VALUES(?,?,?,?,?,?,?)""",
                    (postc, pref, prefr, city, cityr, addr, addrr),
                )
        # データベースを閉じる --- (*4)
        c.execute("commit")
        conn.close()

    def add_fulladdr(
        incomplete_csv="./incomplete.csv",
        postalcode_sqlite3="./postalcode.sqlite3",
        output_csv="./output.csv",
    ):
        if not os.path.isfile(postalcode_sqlite3):
            return False

        # SQLite3のデータベースを開く
        with sqlite3.connect(postalcode_sqlite3) as conn:
            c = conn.cursor()
            # CSVファイルを開く
            with open(
                incomplete_csv, "r", encoding="utf_8_sig", errors="", newline=""
            ) as fp:
                # CSVを読み込む
                with open(output_csv, "w", encoding="utf_8_sig") as csvoutput:
                    reader = csv.DictReader(
                        fp,
                        delimiter=",",
                        quotechar='"',
                        doublequote=True,
                        skipinitialspace=True,
                    )
                    fn = reader.fieldnames.copy()
                    if fn.count("postc"):
                        fn.remove("postc")
                    if fn.count("pref"):
                        fn.remove("pref")
                    if fn.count("city"):
                        fn.remove("city")
                    if fn.count("addr"):
                        fn.remove("addr")
                    if fn.count("detail1"):
                        fn.remove("detail1")
                    if fn.count("detail2"):
                        fn.remove("detail2")
                    if fn.count("detail3"):
                        fn.remove("detail3")
                    fn = ["postc", "pref", "city", "addr", "detail1", "detail2", "detail3"] + fn
                    writer = csv.DictWriter(csvoutput, fieldnames=fn)
                    writer.writeheader()
                    # 一行ずつ処理する
                    for i, row in enumerate(reader):
                        row["pref"], row["city"], row["addr"] = PostalCode.get_detail(
                            c, row["postc"]
                        )
                        writer.writerow(row)

    def get_detail(cursor, postc):
        cursor.execute(f"SELECT * from zip where postc is {postc}")
        hit = cursor.fetchone()
        return (hit[1], hit[3], hit[5])


def main():
    PostalCode.make_db()


if __name__ == "__main__":
    main()
