import cv2
image_path = "C:\\Users\\hp\\Desktop\\connectmobile\\image"
def crop_image(input_image, output_path, x, y, width, height):
    # Charger l'image
    img = cv2.imread(input_image)

    # Découper l'image en utilisant les coordonnées x, y, largeur et hauteur spécifiées
    cropped_img = img[y:y+height, x:x+width]

    # Enregistrer l'image découpée
    cv2.imwrite(output_path, cropped_img)

input_image_path = f"{image_path}\\c.jpg"
output_image_path = f"{image_path}\\c_de.jpg"

# Spécifier les coordonnées et les dimensions du rectangle de découpe
x = 0
y = 420
width = 1000
height = 883

# Appeler la fonction pour découper l'image
#crop_image(input_image_path, output_image_path, x, y, width, height)




