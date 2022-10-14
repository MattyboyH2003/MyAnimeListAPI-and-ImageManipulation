import pygame
import MyAnimeListAPI
import MyAnimeListAPI.ImageDownloader as ImageDownloader

from ImageManipulation import Image, Canvas
from ImageManipulation.jpgManager import DecodeJPG


# Gets all the users favourited anime, manga etc...
favourites = MyAnimeListAPI.GetUserFavourites("mattyboyh2003")
types = ["manga"]

# Creates a list of {id : int, type : str} dicts for each manga and then passes it into the bulk download
filesList = []
for type in types:
    filesList.extend([{"id" : i.split("/")[4], "type" : i.split("/")[3]} for i in favourites[type]])
images = ImageDownloader.DownloadBulk(filesList)

imageObjList = []
for imagePath in images:
    # Decodes the JPG to get the RGB Matrix and Image Size
    matrix, size = DecodeJPG(imagePath)

    # Creates a new image using the known matrix and size
    imageObjList.append(Image(resolution = size, matrix = matrix))

standardSize = [int(i) for i in list(pygame.Vector2(imageObjList[0].getSize())/2)]

print(f"Standard Size: {standardSize}")

# Creates a canvas to fit a 5x2 grid of 0.5 scale images (presuming they're all the same size)
canvas = Canvas(standardSize[0]*5, standardSize[1] * 2)

# Blits each of the images into a grid on the canvas
count = 0
for img in imageObjList:
    print(f"\nWorking on image: {images[count]}")
    imgSize = img.getSize()

    #print(f"\nImage Size: {imgSize}")

    canvas.blitImage(img, pos = [(count%5) * standardSize[0], (count//5) * standardSize[1]], size = standardSize)
    count += 1

    canvas.update()

#canvas.saveImage("Test.jpg", type="jpg")

# Keeps the window open
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
    clock.tick(30)
