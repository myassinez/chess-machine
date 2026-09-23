import cv2

def tracer_rectangles(image_path, output_path, rectangles, color=(0, 100, 0), thickness=1):
    # Charger l'image à partir du fichier
    image = cv2.imread(image_path)

    # Tracer les rectangles sur l'image
    for rect_coords in rectangles:
        x1, y1, x2, y2 = rect_coords
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

    # Enregistrer l'image modifiée à l'emplacement spécifié
    cv2.imwrite(output_path, image)

    # Afficher l'image avec les rectangles (facultatif)


def intersection(rectangle1, rectangle2):
    x_intersection = max(rectangle1[0], rectangle2[0])
    y_intersection = max(rectangle1[1], rectangle2[1])
    x2_intersection = min(rectangle1[2], rectangle2[2])
    y2_intersection = min(rectangle1[3], rectangle2[3])

    if x_intersection < x2_intersection and y_intersection < y2_intersection:
        # Il y a une intersection
        return (x_intersection, y_intersection, x2_intersection, y2_intersection)
    else:
        # Pas d'intersection
        return None



# Définir le chemin de l'image d'entrée
image_path = "C:\\Users\\hp\\Desktop\\connectmobile\\image"
image_name="\\a_de.jpg"
# Définir le chemin de sortie pour l'image modifiée
output_image_path = "C:\\Users\\hp\\Desktop\\connectmobile\\image\\a_modifiee.jpg"

x0=42
y0=50
xf=850
yf=850
yn=48

c8=(42,y0,145,yf)
c7=(145,y0,250,yf)
c6=(250,y0,350,yf)
c5=(350,y0,450,yf)
c4=(450,y0,550,yf)
c3=(550,y0,650,yf)
c2=(650,y0,750,yf)
c1=(750,y0,850,yf)

ch=(x0,50,xf,150)
cg=(x0,150,xf,250)
cf=(x0,250,xf,350)
ce=(x0,350,xf,450)
cd=(x0,450,xf,550)
cc=(x0,550,xf,650)
cb=(x0,650,xf,750)
ca=(x0,750,xf,850)

# Liste des coordonnées des rectangles à tracer
rectangles_list_n = [c1,c2,c3,c4,c5,c6,c7,c8]
rectangles_list_l=[ca,cb,cc,cd,ce,cf,cg,ch]

# Appeler la fonction pour tracer les rectangles et enregistrer l'image
tracer_rectangles(image_path+image_name, output_image_path, rectangles_list_n)
tracer_rectangles(output_image_path, output_image_path, rectangles_list_l,(0,0,255))


def comparer_images(image_path1, image_path2, coords_sup_gauche, coords_inf_droite, output_path):
    # Charger les images
    image1 = cv2.imread(image_path1)
    image2 = cv2.imread(image_path2)

    # Extraire la région d'intérêt des deux images
    region1 = image1[coords_sup_gauche[1]:coords_inf_droite[1], coords_sup_gauche[0]:coords_inf_droite[0]]
    region2 = image2[coords_sup_gauche[1]:coords_inf_droite[1], coords_sup_gauche[0]:coords_inf_droite[0]]

    # Calculer la différence entre les deux régions
    difference = cv2.absdiff(region1, region2)

    # Enregistrer l'image de différence à l'emplacement spécifié
    cv2.imwrite(output_path, difference)

# Exemple d'utilisation avec les coordonnées de l'intersection de c1 et ca
coords_intersection = intersection(c6, ce)

img1="\\a_de.jpg"
img2="\\b_de.jpg"
imgdif="\\difference_image.jpg"
comparer_images(image_path+img1, image_path+img1, coords_intersection[:2], coords_intersection[2:], image_path+imgdif)




