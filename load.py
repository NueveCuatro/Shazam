########## Fichier qui permet de charger les fingerprint dans la BDD ############
############ Bibliothèques utiles #############

import os 
from pydub import AudioSegment
import librosa
import hashlib
import sqlite3



########### On initialise l'ouverture de la base de donnée

conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

########### On récupère l'ensemble des fichier dan une liste ####################

output_folder='./audio_wav'

# Obtenez la liste des fichiers dans le répertoire
liste_fichiers = [f for f in os.listdir(output_folder)]

print(liste_fichiers)

# Pour chaque fichier on va l'importer dans la Base de donées
for fichier in liste_fichiers:
    
    # Chargez le fichier WAV
    y, sr = librosa.load(output_folder + '/' + fichier)

    # Réglage de la taille de la fenêtre de transformation de Fourier à court terme
    n_fft = 512

    # Calculez la transformée de Fourier à court terme (STFT) avec n_fft spécifié
    stft = librosa.stft(y, n_fft=n_fft)

    # Calculez les empreintes digitales audio en utilisant chroma
    chroma = librosa.feature.chroma_stft(S=stft, sr=sr)
    hashes = [hashlib.sha1(str(frame).encode()).hexdigest() for frame in chroma.T]

    fichiers = [ fichier for i in range (len(hashes)) ]

    # Stockez les empreintes digitales dans la base de données SQLite en incluant le nom de la chanson
    for h, song_name in zip(hashes, fichiers):
        cursor.execute("INSERT INTO fingerprints (hash, nom) VALUES (?, ?)", (h, song_name))



conn.commit()
conn.close()