import os 
import numpy as np
import librosa
import hashlib
import sqlite3
from pydub import AudioSegment

# On convertit le son de test dans le bon format 
input_file_to_identify = 'test.m4a'
output_file_to_identify = 'test.wav'
audio_to_identify = AudioSegment.from_file(input_file_to_identify, format='m4a')
audio_to_identify.export(output_file_to_identify, format='wav')
y, sr = librosa.load(output_file_to_identify)

# Connexion à la base de données SQLite
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Taille des blocs pour l'analyse FFT
block_size = 4096
hop_length = block_size // 2  # La moitié du bloc pour le chevauchement

# Liste pour stocker les empreintes du son à identifier
hashes_to_identify = []

# Diviser le signal en blocs et appliquer la FFT sur chaque bloc
for i in range(0, len(y) - block_size, hop_length):
    block = y[i:i + block_size]
    fft_block = np.fft.fft(block)
    freqs = np.fft.fftfreq(len(fft_block), 1/sr)
    
    # Diviser les fréquences en 6 bandes
    freq_bands = [
        np.where((freqs >= 0) & (freqs <= 113))[0],
        np.where((freqs > 113) & (freqs <= 220))[0],
        np.where((freqs > 220) & (freqs <= 436))[0],
        np.where((freqs > 436) & (freqs <= 866))[0],
        np.where((freqs > 866) & (freqs <= 1728))[0],
        np.where((freqs > 1728) & (freqs <= 5507))[0]
    ]
    
    # Trouver la fréquence de plus grande amplitude dans chaque bande
    selected_freqs = []
    for band in freq_bands:
        if len(band) > 0:
            max_amp_index = band[np.argmax(np.abs(fft_block[band]))]
            selected_freqs.append(freqs[max_amp_index])
    
    hashes_to_identify.append(selected_freqs)

# Convertir les empreintes en chaînes pour la comparaison
hashes_to_identify = [hashlib.sha1(str(frame).encode()).hexdigest() for frame in hashes_to_identify]

# Recherche dans la base de données pour des correspondances
matches = set()

for h in hashes_to_identify:
    cursor.execute("SELECT nom FROM fingerprints WHERE hash=?", (h,))
    song_name = cursor.fetchone()
    if song_name:
        matches.add(song_name[0])

conn.close()

# Afficher les correspondances
if matches:
    print("Chanson(s) identifiée(s) :", matches)
else:
    print("Aucune correspondance trouvée.")
