import os, sqlite3, sys

fname = sys.argv[1]

conn = sqlite3.connect(fname)
conn.row_factory = sqlite3.Row
conn.text_factory = str
data = conn.cursor()
data.execute("UPDATE tv_channels SET params='[]'")
data.execute("UPDATE radio_channels SET params='[]'")

conn.commit()