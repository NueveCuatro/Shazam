import os
from pydub import AudioSegment
import librosa
import hashlib
import sqlite3
import numpy as np
from Levenshtein import ratio

# Traitement du son à identifier
input_file_to_identify = 'test2.m4a'
output_file_to_identify = 'test2.wav'
audio_to_identify = AudioSegment.from_file(input_file_to_identify, format='m4a')
audio_to_identify.export(output_file_to_identify, format='wav')

y, sr = librosa.load(output_file_to_identify)
n_fft = 512

# Caractéristiques audio
chroma = librosa.feature.chroma_stft(y=y, sr=sr)
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
onset_env = librosa.onset.onset_strength(y=y, sr=sr)

# Création d'une empreinte combinée
combined_features = np.vstack([chroma, tempo * np.ones_like(chroma), onset_env])

# Calcul des empreintes à partir des caractéristiques combinées
hashes_to_identify = [hashlib.sha256(str(frame).encode()).hexdigest() for frame in combined_features.T]

# Recherche dans la base de données
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Récupération des empreintes stockées en base de données
cursor.execute("SELECT hash FROM fingerprints")
stored_hashes = cursor.fetchall()
stored_hashes = [item[0] for item in stored_hashes]

# Calcul des similarités avec la similarité de Levenshtein
levenshtein_similarities = [ratio(hashes_to_identify, hash_from_db) for hash_from_db in stored_hashes]

# Seuil pour la correspondance
threshold = 0 # Seuil de similarité de 0.8 pour un exemple

# Identification des chansons correspondantes
matches = [i for i, similarity in enumerate(levenshtein_similarities) if similarity > threshold]

if matches:
    # Votre logique pour traiter les correspondances
    pass
else:
    print("Aucune correspondance trouvée.")
