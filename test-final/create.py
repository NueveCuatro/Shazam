import sqlite3

# Création de la base de donnée et/ou connexion
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Supprimez les tables "audios" et "fingerprints" si elles existent
cursor.execute("DROP TABLE IF EXISTS fingerprints")

# Création de la table "fingerprints" avec les bandes de fréquences et la temporalité
cursor.execute('''
    CREATE TABLE IF NOT EXISTS fingerprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,
    chunk_order INTEGER,
    band1 REAL,
    band2 REAL,
    band3 REAL,
    band4 REAL,
    band5 REAL,
    band6 REAL
    )

''')

# On valide la création et on ferme la connexion
conn.commit()
conn.close()

