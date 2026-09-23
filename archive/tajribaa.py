import cv2
import numpy as np

def remove_background(square, average_color):
    # Subtract the average color from each pixel
    result = cv2.subtract(square, average_color)
    
    # Clip negative values to zero
    result = np.maximum(result, 0)

    return result

img = cv2.imread("111.jpg")

chessboard_coordinates = [(chr(72 - i) + str(8 - j)) for i in range(8) for j in range(8)]

for x in range(0, img.shape[0] - 8, img.shape[0] // 8):
    for y in range(0, img.shape[1] - 8, img.shape[1] // 8):
        square = img[x:x + img.shape[0] // 8, y:y + img.shape[1] // 8, :]

        average_rgb = np.mean(square, axis=(0, 1))
        coordinate = chessboard_coordinates[(x // (img.shape[0] // 8)) * 8 + (y // (img.shape[1] // 8))]

        # Assuming 'square' is the image of the chessboard square and 'average_rgb' is its average RGB value
        # Remove background
        result = remove_background(square, average_rgb)

        # Display the original square and the result
        cv2.imshow(f'{coordinate} - Original Square', square)
        cv2.imshow(f'{coordinate} - Result', result)

cv2.waitKey(0)
cv2.destroyAllWindows()
