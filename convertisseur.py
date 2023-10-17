############ CONVERTISSEUR ET BDD #############

# Les fichiers du dictaphone sont en format M4A nous devons les convertir en MAV
# MAV est le format par default des bibliothèques python sonores

############ Bibliothèques utiles #############

import os 
from pydub import AudioSegment
import shutil


########### From M4A to MAV ####################
path_folder='./audio'
output_folder='./audio_wav'


# Obtenez la liste des fichiers dans le répertoire
liste_fichiers = [f for f in os.listdir(path_folder)]

# Affichez les noms des fichiers
for fichier in liste_fichiers:
    output_file = fichier.split('.')[0] + '.wav'
    audio = AudioSegment.from_file(path_folder+'/'+fichier, format='m4a')
    audio.export(output_file, format='wav')
    shutil.move(output_file, output_folder)
    print(fichier)

 

