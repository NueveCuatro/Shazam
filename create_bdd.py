######### Création de la base de donnée du projet #########

############ Bibliothèques utiles #############
import sqlite3

################################################

# Création de la base de donnée et/ou connexion
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()


# Supprimez la table "fingerprints" si elle existe
cursor.execute("DROP TABLE IF EXISTS fingerprints")

# Création de la table: fingerprint: composé d'une clé et d'un hash 


cursor.execute('''CREATE TABLE IF NOT EXISTS fingerprints
                 (id INTEGER PRIMARY KEY, hash TEXT, nom TEXT)''')

#### On valide sa création et on ferme la connexion ###########

conn.commit()
conn.close()
