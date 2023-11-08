import os
import librosa
import sqlite3
import numpy as np

# Chemin vers le dossier contenant les fichiers audio prétraités
preprocessed_folder = './audio_preprocessed'

# Plages de fréquences pour les bandes
band_ranges = [
    (0, 113), (113, 220), (220, 436),
    (436, 866), (866, 1728), (1728, 5507)
]

# Fonction pour extraire les empreintes digitales
def extract_fingerprints(y, sr, n_fft, hop_length, band_ranges):
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    # print("Spectrogramme créé avec la forme :", S.shape)  # Vérifiez la taille du spectrogramme
    fingerprints = []

    if S.size == 0:
        print("Le spectrogramme est vide. Aucune donnée à traiter.")
        return fingerprints

    freq_bins = S.shape[0]  # Nombre de bins de fréquences dans le spectrogramme
    time_frames = S.shape[1]  # Nombre de trames temporelles dans le spectrogramme

    # Traitement de tous les chunks, y compris le dernier qui pourrait être plus petit
    for i in range(0, S.shape[1], hop_length):
        end_idx = i + hop_length if i + hop_length < S.shape[1] else S.shape[1]
        chunk = S[:, i:end_idx]
        fingerprint = []
        for low_idx, high_idx in [(int(low * freq_bins / (sr/2)), int(high * freq_bins / (sr/2))) for low, high in band_ranges]:
            max_freq_value = np.max(chunk[low_idx:high_idx]) if high_idx <= freq_bins else 0
            fingerprint.append(max_freq_value)
        fingerprints.append(fingerprint)
        # print("Empreinte digitale pour le chunk courant:", fingerprint)

    return fingerprints



# Connexion à la base de données SQLite
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Création de la table fingerprints si elle n'existe pas déjà
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

# Récupération de l'ensemble des fichiers .wav dans une liste
liste_fichiers = [f for f in os.listdir(preprocessed_folder) if f.endswith('.wav')]

# if not liste_fichiers:
#     print(f"Aucun fichier .wav trouvé dans {preprocessed_folder}.")
# else:
#     print(f"Nombre de fichiers audio trouvés : {len(liste_fichiers)}")

# Pour chaque fichier audio prétraité dans le dossier
for fichier in liste_fichiers:
    # Chargez le fichier WAV
    y, sr = librosa.load(os.path.join(preprocessed_folder, fichier), sr=None)

    # if y.size == 0:
    #     print(f"Le fichier {liste_fichiers[0]} semble être vide après chargement.")
    # else:
    #     print(f"Le fichier {liste_fichiers[0]} a été chargé avec {y.size} échantillons.")


    # Réglage de la taille de la fenêtre n_fft et de hop_length
    n_fft = 512  # Fenêtre adaptée à la taille des chunks
    hop_length = 256  # Taille des chunks dans le spectrogramme

    # Extraction des empreintes digitales
    fingerprints = extract_fingerprints(y, sr, n_fft, hop_length, band_ranges)

    # if not fingerprints:
    #     print("Aucune empreinte digitale n'a été générée.")
    # else:
    #     print(f"Nombre d'empreintes digitales générées : {len(fingerprints)}")
    #     print("Première empreinte digitale :", fingerprints[0])


    # Stockage des empreintes digitales dans la base de données
    for chunk_order, fingerprint in enumerate(fingerprints):

        fingerprint = [float(value) for value in fingerprint]
        cursor.execute("""
            INSERT INTO fingerprints (file_name, chunk_order, band1, band2, band3, band4, band5, band6) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fichier, chunk_order, *fingerprint))

# Valider les changements dans la base de données
conn.commit()

# Fermer la connexion à la base de données
conn.close()
