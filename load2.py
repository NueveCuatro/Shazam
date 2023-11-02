import os
import librosa
import hashlib
import sqlite3
import numpy as np

# Chemin vers le dossier contenant les fichiers audio prétraités
preprocessed_folder = './audio_preprocessed'

# Fonction pour extraire les caractéristiques MFCC
def extract_features(y, sr, n_fft, hop_length):
    # Extraction des MFCC
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=n_fft, hop_length=hop_length)
    # Calcul de la moyenne des MFCC sur le temps (compression temporelle)
    mfccs = np.mean(mfccs, axis=1)
    return mfccs

# Connexion à la base de données SQLite
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Récupération de l'ensemble des fichiers .wav dans une liste
liste_fichiers = [f for f in os.listdir(preprocessed_folder) if f.endswith('.wav')]

# Pour chaque fichier audio prétraité dans le dossier
for fichier in liste_fichiers:
    # Chargez le fichier WAV
    y, sr = librosa.load(os.path.join(preprocessed_folder, fichier), sr=None)
    
    # Réglage de la taille de la fenêtre de transformation de Fourier à court terme et de hop_length
    n_fft = 2048  # Une fenêtre plus grande pour une meilleure résolution fréquentielle
    hop_length = 512  # Un plus grand hop_length pour réduire la densité des empreintes digitales

    # Extraction des caractéristiques MFCC
    mfccs = extract_features(y, sr, n_fft, hop_length)

    # Génération d'un hash basé sur les MFCC
    hash_value = hashlib.sha1(mfccs.tobytes()).hexdigest()
    
    # Stockage de l'empreinte digitale dans la base de données
    cursor.execute("INSERT INTO fingerprints (hash, nom) VALUES (?, ?)", (hash_value, fichier))

# Valider les changements dans la base de données
conn.commit()

# Fermer la connexion à la base de données
conn.close()
