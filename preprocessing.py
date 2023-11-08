import os
import librosa
import soundfile as sf

# Chemin vers le dossier contenant les fichiers audio originaux
input_folder = './audio_originals'
# Chemin vers le dossier où les fichiers prétraités seront sauvegardés
output_folder = './audio_preprocessed'

# Assurez-vous que le dossier de sortie existe
os.makedirs(output_folder, exist_ok=True)

# Fonction pour l'augmentation de données
def augment_sound(y, sr):
    variations = []
    # Changement de hauteur (pitch shifting)
    y_pitch_up = librosa.effects.pitch_shift(y, sr=sr, n_steps=2)  # 2 demi-tons vers le haut
    y_pitch_down = librosa.effects.pitch_shift(y, sr=sr, n_steps=-2)  # 2 demi-tons vers le bas
    variations.extend([y_pitch_up, y_pitch_down])
    
    # Changement de vitesse (time stretching)
    y_speed_up = librosa.effects.time_stretch(y, rate=1.1)
    y_slow_down = librosa.effects.time_stretch(y, rate=0.9)
    variations.extend([y_speed_up, y_slow_down])
    
    return variations


# Traitement de chaque fichier dans le dossier d'entrée
for filename in os.listdir(input_folder):
    if filename.endswith('.wav'):  # Assurez-vous que c'est un fichier WAV
        # Chemin complet du fichier
        file_path = os.path.join(input_folder, filename)
        # Chargez le fichier WAV
        y, sr = librosa.load(file_path, sr=None)
        # Normalisation du volume et découpage du silence
        y = librosa.util.normalize(y)
        y, _ = librosa.effects.trim(y)
        
        # Générer des variations pour l'augmentation de données
        variations = augment_sound(y, sr)
        
        # Enregistrement du fichier prétraité et de ses variations
        for i, y_var in enumerate([y] + variations):
            output_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_var{i}.wav")
            sf.write(output_file, y_var, sr)

print("Prétraitement terminé.")
