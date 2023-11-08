import os
import sqlite3

# Chemin vers le dossier contenant les fichiers audio prétraités
preprocessed_folder = '../audio_preprocessed'

# Création de la base de donnée et/ou connexion
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Assurez-vous que la table 'audios' existe déjà
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS audios (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         nom TEXT
#     )
# ''')

# Récupération de l'ensemble des fichiers audio dans une liste
liste_fichiers = [f for f in os.listdir(preprocessed_folder) if f.endswith('.wav')]

# Insertion des informations de chaque fichier audio dans la table 'audios'
for fichier in liste_fichiers:
    cursor.execute("INSERT INTO audios (nom) VALUES (?)", (fichier,))

# Valider les changements dans la base de données
conn.commit()

# Fermer la connexion à la base de données
conn.close()

print(f"{len(liste_fichiers)} fichiers audio ont été chargés dans la table 'audios'.")
