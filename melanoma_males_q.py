import sqlite3
import pandas as pd

conn = sqlite3.connect('data.db')

full_query = f"""
    SELECT samp.b_cell
    FROM samples samp
    JOIN subjects sub ON sub.subject = samp.subject
    WHERE sub.sex = 'M'
    AND sub.condition = 'melanoma'
    AND samp.time_from_treatment_start = 0
    """

ans = pd.read_sql_query(full_query, conn)
conn.close()
print(ans)