import subprocess
import time
from PIL import Image

# Adresse IP de l'appareil Android
IP_DU_DISPOSITIF = ""

# Port ADB par défaut
PORT_ADB = 5555

# Dossier de destination sur le PC
DOSSIER_DESTINATION_PC = r"C:\Users\hp\Desktop\connectmobile\image"

# Dossier de destination sur l'appareil Android
DOSSIER_DESTINATION_ANDROID = "/sdcard/DCIM/Camera/mobile"

def redimensionner_image(chemin_image, largeur, hauteur):
    image = Image.open(chemin_image)
    nouvelle_image = image.resize((largeur, hauteur))
    nouvelle_image.save(chemin_image)


def capture_photo(nom_photo):
    # Démarrer le chronomètre global
    debut_chronometre_global = time.time()
    
    # Commande ADB pour prendre une photo
    commande_capture_photo = f"adb connect {IP_DU_DISPOSITIF}:{PORT_ADB} && adb shell input keyevent KEYCODE_CAMERA"
    subprocess.run(commande_capture_photo, shell=True)
    
    time.sleep(2)
    
    # Commande ADB pour savoir le dernier image
    commande_derniere_image = f"adb shell \"ls -t /sdcard/DCIM/Camera/ | head -n 1\""
    derniere_image = subprocess.run(commande_derniere_image, shell=True, capture_output=True, text=True)
    derniere_image = derniere_image.stdout.strip()

    
    # Commande pour changer le nom et le chemin de l'image
    commande_changer = f"adb shell mv /sdcard/DCIM/Camera/{derniere_image} {DOSSIER_DESTINATION_ANDROID}/{nom_photo}"
    subprocess.run(commande_changer, shell=True)
    

    
    # Copier la photo de l'appareil Android vers le PC
    commande_copie_photo = f"adb pull {DOSSIER_DESTINATION_ANDROID}/{nom_photo} {DOSSIER_DESTINATION_PC}/{nom_photo}"
    subprocess.run(commande_copie_photo, shell=True)
    
    chemin_image_pc = f"{DOSSIER_DESTINATION_PC}/{nom_photo}"
    redimensionner_image(chemin_image_pc, largeur=1008, hauteur=567)  # Remplacez 100 par les dimensions souhaitées

    # Arrêter le chronomètre global et calculer la durée totale d'exécution
    duree_ecoulee_global = time.time() - debut_chronometre_global
    afficher_duree(duree_ecoulee_global)
    


    # Redémarrer le serveur ADB
    redemmarer_serveur()

def afficher_duree(duree):
    heures, reste = divmod(duree, 3600)
    minutes, secondes = divmod(reste, 60)
    print(f"Durée totale : {int(heures)} heures, {int(minutes)} minutes, {int(secondes)} secondes")

def redemmarer_serveur():
    tuer_serveur = "adb kill-server"
    subprocess.run(tuer_serveur, shell=True)
    lancer_serveur = "adb start-server"
    subprocess.run(lancer_serveur, shell=True)

# Exemple d'utilisation
nom_photo_personnalise = "setranj.jpg"
capture_photo(nom_photo_personnalise)

