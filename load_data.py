import csv
import sqlite3

BATCH_SZ, batch_subjects, batch_samples = 1000, [], []

conn = sqlite3.connect('data.db')
cur = conn.cursor()

###################################
### Make tables ###################
###################################

cur.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    subject TEXT PRIMARY KEY,
    project TEXT,     
    condition TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    sample_type TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS samples (
    sample TEXT PRIMARY KEY,
    subject TEXT,     
    response TEXT,
    time_from_treatment_start INTEGER,
    b_cell INT,
    cd8_t_cell INT,
    cd4_t_cell INT,
    nk_cell INT,
    monocyte INT
)
""")

###################################
### Populate tables ###############
###################################

def send_batch(cursor, batch_sbj, batch_samp):
    cursor.executemany(
        """
        INSERT INTO subjects
        (subject, project, condition, age, sex, treatment, sample_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(subject) DO NOTHING
        """,
        batch_sbj,
    )

    cursor.executemany(
        """
        INSERT INTO samples
        (sample, subject, response, time_from_treatment_start, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(sample) DO NOTHING
        """,
        batch_samp,
    )


with open("cell-count.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        batch_subjects.append( (row["subject"], row["project"], row["condition"], int(row["age"]), row["sex"], row["treatment"], row["sample_type"]) )
        batch_samples.append( (row["sample"], row["subject"], row["response"], int(row["time_from_treatment_start"]), 
                               row["b_cell"], row["cd8_t_cell"], row["cd4_t_cell"], row["nk_cell"], row["monocyte"]) )
        if len(batch_subjects) >= BATCH_SZ:
            send_batch(cur, batch_subjects, batch_samples)
            conn.commit()
            batch_subjects, batch_samples = [], []

if batch_subjects:
    send_batch(cur, batch_subjects, batch_samples)
    conn.commit()

conn.close()


###################################
### Validation  ###################
###################################

# conn = sqlite3.connect('data.db')
# cur = conn.cursor()
# count = 0
# for row in cur.execute('SELECT * FROM subjects'):
#     if count < 10:
#         print(row)
#     count+=1
# print(count)

# count = 0
# for row in cur.execute('SELECT * FROM samples'):
#     if count < 10:
#         print(row)
#     count+=1
# print(count)

conn.close()