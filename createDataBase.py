import sqlite3
if __name__ == "__main__":
    database_name = "higSschool.db"
    all_tables = """CREATE TABLE IF NOT EXISTS "en_prep" ( que text, ans text, tags text, time int, testing_blacklist text default "");
CREATE TABLE IF NOT EXISTS "en_voc" ( que text, ans text, tags text, time int, testing_blacklist text default "");
CREATE TABLE IF NOT EXISTS "en_gra" ( que text, ans text, tags text, time int, testing_blacklist text default "");
CREATE TABLE IF NOT EXISTS "notes" (
        "que"   text,
        "ans"   text,
        "method_name"   text,
        "tags"  text,
        "method_time"   int,
        "time"  int,
        "testing_blacklist"     TEXT DEFAULT ""
);
CREATE TABLE IF NOT EXISTS "record_list" (
        "method_names"  INTEGER NOT NULL,
        "tags"  TEXT NOT NULL,
        "id"    INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "record_data" (
        "id"    INTEGER NOT NULL,
        "method_name"   TEXT NOT NULL,
        "time"  INTEGER NOT NULL
);"""
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    table_list = all_tables.split(';')
    for table in table_list:
        cur.execute(table)
    cur.close()
    con.commit()
    con.close()

