import os
from pydub import AudioSegment
import librosa
import hashlib
import sqlite3
import numpy as np

######### Traitement du son à identifier ###############

# Convertissez le son de test dans le bon format
input_file_to_identify = 'test3.wav'
output_file_to_identify = 'test.wav'
audio_to_identify = AudioSegment.from_file(input_file_to_identify, format='m4a')
audio_to_identify.export(output_file_to_identify, format='wav')

# Fonction pour le prétraitement du signal audio
def preprocess_audio(y, sr):
    # Normalisation du volume
    y = librosa.util.normalize(y)
    # Réduction du silence
    y, _ = librosa.effects.trim(y)
    return y

################# On charge l'extrait et ses hashs #####################
y, sr = librosa.load(output_file_to_identify, sr=None)
# Prétraitement du signal audio
y = preprocess_audio(y, sr)

# Réglage de la taille de la fenêtre de transformation de Fourier à court terme
n_fft = 2048  # Doit correspondre à load.py
hop_length = 512  # Doit correspondre à load.py

# Extraction des caractéristiques MFCC
mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=n_fft, hop_length=hop_length)
# Calcul de la moyenne des MFCC sur le temps (compression temporelle)
mfccs = np.mean(mfccs, axis=1)

# Génération du hash basé sur les MFCC
hash_value = hashlib.sha1(mfccs.tobytes()).hexdigest()

################ Recherche dans la base de données #########################
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Recherchez le hash dans la base de données
cursor.execute("SELECT nom FROM fingerprints WHERE hash=?", (hash_value,))
results = cursor.fetchall()

conn.close()

################# Analyse et Affichage des résultats #####################
if results:
    print("Correspondance(s) trouvée(s) !")
    for (song_name,) in results:
        print(f"Chanson identifiée: {song_name}")
else:
    print("Aucune correspondance trouvée.")
