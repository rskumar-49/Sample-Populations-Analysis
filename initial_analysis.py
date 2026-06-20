import sqlite3
import pandas as pd

BATCH_SIZE = 1000
populations = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']

conn = sqlite3.connect('data.db')
read_cur = conn.cursor()
write_cur = conn.cursor()

write_cur.execute("""
CREATE TABLE IF NOT EXISTS populations_samplewise (
    sample TEXT,
    total_count INT,     
    population TEXT,
    count INTEGER,
    percentage REAL,
    PRIMARY KEY (sample, population)
)
""")

read_cur.execute("SELECT sample, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte FROM samples")

while True:
    rows = read_cur.fetchmany(BATCH_SIZE)
    if not rows:
        break

    output_rows = []
    for row in rows:
        sample, counts = row[0], row[1:]
        total_count = sum(counts)

        for population, count in zip(populations, counts):
            pct = (count / total_count) * 100
            output_rows.append( (sample, total_count, population, count, pct) )

    write_cur.executemany("""
        INSERT INTO populations_samplewise
        (sample, total_count, population, count, percentage)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(sample, population) DO NOTHING
    """, output_rows)
    conn.commit()

###################################
### Printing ## ###################
###################################

df = pd.read_sql_query("SELECT * FROM populations_samplewise", conn)
print('Part 2: This is the table answer.')
print(df)
print('\n\n')
conn.close()