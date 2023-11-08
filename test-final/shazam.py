import librosa
import sqlite3
import numpy as np

# Chemin vers le fichier audio à identifier
input_file_to_identify = '../test2.wav'

# Plages de fréquences pour les bandes
band_ranges = [
    (0, 113), (113, 220), (220, 436),
    (436, 866), (866, 1728), (1728, 5507)
]

# # Fonction pour extraire les empreintes digitales
# def extract_fingerprints(y, sr, n_fft, hop_length, band_ranges):
#     S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
#     fingerprints = []
#     # Diviser le spectrogramme en chunks
#     for i in range(0, S.shape[1], hop_length):
#         end_idx = i + hop_length if i + hop_length < S.shape[1] else S.shape[1]  # S'assurer de ne pas dépasser
#         chunk = S[:, i:end_idx]
#         fingerprint = []
#         for low, high in band_ranges:
#             freq_bin_range = (int(low * (n_fft/sr)), int(high * (n_fft/sr)))
#             max_freq_value = np.max(chunk[freq_bin_range[0]:freq_bin_range[1]]) if freq_bin_range[1] < chunk.shape[0] else 0
#             fingerprint.append(max_freq_value)
#         fingerprints.append(fingerprint)
#     return fingerprints

def extract_fingerprints(y, sr, n_fft, hop_length, band_ranges):
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    fingerprints = []
    # Calcul du nombre de trames (ou 'chunks') dans le spectrogramme
    num_frames = int(np.ceil(len(y) / hop_length))
    
    # Diviser le spectrogramme en chunks
    for i in range(num_frames):
        start_idx = i * hop_length
        end_idx = start_idx + n_fft
        chunk = S[:, start_idx:end_idx] if end_idx <= len(y) else S[:, start_idx:]
        
        # Si le chunk est plus petit que n_fft, le compléter avec des zéros
        if chunk.shape[1] < n_fft:
            padding = np.zeros((S.shape[0], n_fft - chunk.shape[1]))
            chunk = np.hstack((chunk, padding))
        
        fingerprint = []
        for low, high in band_ranges:
            freq_bin_range = (int(low * (n_fft/sr)), int(high * (n_fft/sr)))
            max_freq_value = np.max(chunk[freq_bin_range[0]:freq_bin_range[1]])
            fingerprint.append(max_freq_value)
        fingerprints.append(fingerprint)
    return fingerprints


# Charger et prétraiter l'audio
y, sr = librosa.load(input_file_to_identify, sr=None)
y, _ = librosa.effects.trim(y)  # Réduction du silence

# Réglage de la taille de la fenêtre n_fft et de hop_length
n_fft = 512  # Fenêtre adaptée à la taille des fichiers audio courts
hop_length = 256  # Plus petite valeur pour obtenir plus de chunks

# Extraction des empreintes digitales de l'audio à identifier
fingerprints_to_identify = extract_fingerprints(y, sr, n_fft, hop_length, band_ranges)

# Recherche dans la base de données
conn = sqlite3.connect('shazam_clone.db')
cursor = conn.cursor()

# Marge de tolérance pour la comparaison des empreintes digitales
tolerance = 0.05  # 5% de tolérance

# Préparation de la requête pour trouver des correspondances dans les empreintes digitales
query = '''
SELECT file_name, COUNT(*) as matches FROM fingerprints
WHERE
    (band1 BETWEEN ? AND ?) AND
    (band2 BETWEEN ? AND ?) AND
    (band3 BETWEEN ? AND ?) AND
    (band4 BETWEEN ? AND ?) AND
    (band5 BETWEEN ? AND ?) AND
    (band6 BETWEEN ? AND ?)
GROUP BY file_name
ORDER BY matches DESC
LIMIT 1
'''

# Comparaison de chaque empreinte digitale
best_match = None
max_matches = 0
for fingerprint in fingerprints_to_identify:
    # Création des bornes pour la comparaison avec une marge de tolérance
    bounds = []
    for f in fingerprint:
        bounds.extend([f * (1 - tolerance), f * (1 + tolerance)])
    
    cursor.execute(query, bounds)
    result = cursor.fetchone()
    
    if result:
        file_name, matches = result
        if matches > max_matches:
            best_match = file_name
            max_matches = matches

conn.close()

# Analyse et affichage des résultats
if best_match:
    print(f"Correspondance trouvée : {best_match} avec {max_matches} correspondances")
else:
    print("Aucune correspondance trouvée.")
