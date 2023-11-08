import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Exécutez une requête SQL pour compter le nombre de lignes dans la table "fingerprints"
cursor.execute("SELECT COUNT(*) FROM fingerprints")
row = cursor.fetchone()

cursor.execute("SELECT * FROM fingerprints LIMIT 10")
# cursor.execute("SELECT * FROM fingerprints ")
rows = cursor.fetchall()

# Récupérez le résultat de la requête
count = row[0]

# Fermez la connexion à la base de données
conn.close()

# Vérifiez si la base de données n'est pas vide
if count > 0:
    print("La base de données n'est pas vide. Elle contient", count, "empreintes digitales.")
else:
    print("La base de données est vide.")


# Affichez les 10 premiers éléments
for exemple in rows:
    print(exemple)


