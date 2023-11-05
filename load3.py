import os
import librosa
import hashlib
import sqlite3
import numpy as np

# Initialisation de la connexion à la base de données
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Chemin du dossier contenant les fichiers audio originaux
output_folder = './audio_originals'

# Obtention de la liste des fichiers dans le répertoire
liste_fichiers = [f for f in os.listdir(output_folder)]

for fichier in liste_fichiers:
    # Chargez le fichier WAV
    y, sr = librosa.load(os.path.join(output_folder, fichier))

    # Réglage de la taille de la fenêtre de transformation de Fourier à court terme
    n_fft = 512

    # Caractéristiques audio
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # Création d'une empreinte combinée
    combined_features = np.vstack([chroma, tempo * np.ones_like(chroma), onset_env])

    # Calcul des empreintes à partir des caractéristiques combinées
    hashes = [hashlib.sha256(str(frame).encode()).hexdigest() for frame in combined_features.T]

    fichiers = [fichier for i in range(len(hashes))]

    # Stockage des empreintes digitales dans la base de données SQLite en incluant le nom de la chanson
    for h, song_name in zip(hashes, fichiers):
        # Stockage du hachage sous forme de chaîne de caractères (TEXT)
        cursor.execute("INSERT INTO fingerprints (hash, nom) VALUES (?, ?)", (h, song_name))

conn.commit()
conn.close()
