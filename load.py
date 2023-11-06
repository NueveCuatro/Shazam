import os 
import numpy as np
import librosa
import hashlib
import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

output_folder = './audio_originals'
liste_fichiers = [f for f in os.listdir(output_folder)]

for fichier in liste_fichiers:
    y, sr = librosa.load(output_folder + '/' + fichier)

    # Taille des blocs pour l'analyse FFT
    block_size = 4096
    hop_length = block_size // 2  # La moitié du bloc pour le chevauchement

    # Liste pour stocker les empreintes de chaque fichier
    fingerprints = []

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
        
        fingerprints.append(selected_freqs)

    # Convertir les empreintes en chaînes pour le stockage
    hashes = [hashlib.sha1(str(frame).encode()).hexdigest() for frame in fingerprints]

    # Stocker les empreintes dans la base de données
    for h in hashes:
        cursor.execute("INSERT INTO fingerprints (hash, nom) VALUES (?, ?)", (h, fichier))

conn.commit()
conn.close()
