import sqlite3
import pandas as pd

def count_query(field):
    return f"""
        SELECT
            {field},
            COUNT(*) AS cnt
        FROM subjects sub
        JOIN samples samp ON sub.subject = samp.subject
        WHERE sub.treatment = 'miraclib'
        AND sub.sample_type = 'PBMC'
        AND sub.condition = 'melanoma'
        AND samp.time_from_treatment_start = 0
        GROUP BY {field}
        ORDER BY cnt DESC
    """
def subset_breakdown(query):
    conn = sqlite3.connect('data.db')
    ans = pd.read_sql_query(count_query(query), conn)
    conn.close()
    return ans

if __name__ == "__main__":

    conn = sqlite3.connect('data.db')

    full_query = f"""
        SELECT sample
        FROM samples samp
        JOIN subjects sub ON sub.subject = samp.subject
        WHERE sub.treatment = 'miraclib'
        AND sub.sample_type = 'PBMC'
        AND sub.condition = 'melanoma'
        AND samp.time_from_treatment_start = 0
        """
    full_subset = pd.read_sql_query(full_query, conn)
    full_subset.to_sql('miraclib_pbmc_melanoma_day0_samples', conn, if_exists='replace')
    
    print('Part 4: The following is a table composed of the sample numbers of PBMC day-0 cells from melanoma patients treated with miraclib.')
    df = pd.read_sql_query("SELECT * FROM miraclib_pbmc_melanoma_day0_samples", conn)
    print(df)

    print('We also have these breakdowns by subset:')
    for query in ['sub.project', 'samp.response', 'sub.sex']:
        print()
        print(subset_breakdown(query).to_string(index=False))

    print('\n\n')
 
    conn.close()

