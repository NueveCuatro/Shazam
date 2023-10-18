######### Code permettant l'identification du son ##########

############ Bibliothèques utiles #############

import os 
from pydub import AudioSegment
import librosa
import hashlib
import sqlite3
######### Traitement du son à identifier ###############

# On convertit le son de test dans le bon format 
input_file_to_identify = 'test.m4a'
output_file_to_identify = 'test.wav'
audio_to_identify = AudioSegment.from_file(input_file_to_identify, format='m4a')
audio_to_identify.export(output_file_to_identify, format='wav')
##########################################################

#################On charge l'extrait et ses hashs #####################
y, sr = librosa.load(output_file_to_identify)

# Réglage de la taille de la fenêtre de transformation de Fourier à court terme
n_fft = 512

# Calculez la transformée de Fourier à court terme (STFT) avec n_fft spécifié
stft = librosa.stft(y, n_fft=n_fft)

# Calculez les empreintes digitales audio en utilisant chroma
chroma = librosa.feature.chroma_stft(S=stft, sr=sr)
hashes_to_identify = [hashlib.sha1(str(frame).encode()).hexdigest() for frame in chroma.T]
############################################################################


################ Recherche dans la base de données #########################
# ouverture de la base de données 
# Connexion à la base de données SQLite
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

matches = set()  # Utilisez un ensemble pour stocker les noms de chansons uniques

# Parcourez les empreintes digitales à identifier
for h in hashes_to_identify:
    cursor.execute("SELECT nom FROM fingerprints WHERE hash=?", (h,))
    song_name = cursor.fetchone()
    if song_name:
        
        matches.add(song_name[0])  # Ajoutez le nom de la chanson à l'ensemble

conn.close()

print(matches)



if matches:
    print("Chanson(s) identifiée(s) !")
    # Comptez les occurrences de chaque chanson
    chanson_occurrences = {}
    for match in matches:
        if match in chanson_occurrences:
            chanson_occurrences[match] += 1
        else:
            chanson_occurrences[match] = 1

    # Triez les correspondances par nombre d'occurrences (de la plus courante à la moins courante)
    matches_sorted = sorted(chanson_occurrences, key=chanson_occurrences.get, reverse=True)

    # Affichez la chanson la plus courante
    print("Chanson correspondante la plus probable :", matches_sorted[0])
else:
    print("Aucune correspondance trouvée.")
