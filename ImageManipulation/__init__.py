import pygame

from struct import unpack

from ImageManipulation.Errors import ImageError
from ImageManipulation.jpgManager import DecodeJPG, EncodeJPG, FlipMatrix


class Image:
    def __init__(self, **kwargs):
        """
        Requires at least 1 of `file` or `matrix`
        `resolution` (optional) - The resolution of the image\n
        `alpha` (optional) - The rgb colour to swap with clear pixels when drawn\n
        `file` (optional) - The file path for the image (bin or jpg alowed)\n
        `matrix` (optional) - The (x, y) RGB matrix of the image
        """

        if "resolution" in list(kwargs.keys()):
            self.resolution = kwargs["resolution"]

        if "file" in list(kwargs.keys()):
            self.loadFile(kwargs["file"])
        elif "matrix" in list(kwargs.keys()):
            self.rgbMatrix = kwargs["matrix"]
            self.resolution = [len(kwargs["matrix"]), len(kwargs["matrix"][0])]
        else:
            raise ImageError("No file or raw data provided")
        
        if "alpha" in list(kwargs.keys()):
            self.alpha = kwargs["alpha"]
        else:
            self.alpha = None
    
    def loadFile(self, file):
        fileExtention = file.split(".")[-1]
        if fileExtention == "bin":
            self.decodeBin(file)
        elif fileExtention == "jpg" or fileExtention == "jpeg":
            self.decodeJpeg(file)
        else:
            raise ImageError("Invalid file type provided")
    def decodeBin(self, file):
        with open(file, "rb") as file:
            raw = Image(file.read())
            self.rawDecode(raw)
    def decodeJpeg(self, file):
        self.rgbMatrix, self.resolution = DecodeJPG(file)
    def rawDecode(self, raw):
        (width,) = unpack(">H", raw[:2])
        (height,) = unpack(">H", raw[2:4])

        raw = raw[4:]

        print(f"Image Size: {width}, {height}")

        self.resolution = (width, height)

        self.rgbMatrix = [[[] for _ in range(0, height)] for i in range(0, width)]

        count = 0

        print(width*height)
        print(len(raw)//3)

        while raw:

            self.rgbMatrix[count//height][count%height] = unpack("BBB", raw[:3])
            raw = raw[3:]

            count += 1

    def saveImage(self, saveFile):
        with open(f"{__file__.replace('Image.py', '')}/RawImages/{saveFile}.bin", "wb") as file:
            file.write(self.resolution[0].to_bytes(2, byteorder='big'))
            file.write(self.resolution[1].to_bytes(2, byteorder='big'))

            count = 0
            for x in range(self.resolution[0]):
                for y in range(self.resolution[1]):
                    pixel = self.rgbMatrix[x][y]
                    if pixel:
                        file.write(pixel[0].to_bytes(1, byteorder='big'))
                        file.write(pixel[1].to_bytes(1, byteorder='big'))
                        file.write(pixel[2].to_bytes(1, byteorder='big'))
                        count += 1
    def drawImage(self, window, displayScale):
        for x, column in enumerate(self.rgbMatrix):
            if None in column:
                column.remove(None)
            for y, pixel in enumerate(column):
                if pixel:
                    pygame.draw.rect(window, pixel, ((x * displayScale.as_integer_ratio()[0]) // displayScale.as_integer_ratio()[1], (y * displayScale.as_integer_ratio()[0]) // displayScale.as_integer_ratio()[1],1,1))
    
    def getSize(self):
        return self.resolution
    def getMatrix(self):
        return self.rgbMatrix
    def getAlpha(self):
        return self.alpha

    def setAlpha(self, alpha):
        self.alpha = alpha

class Canvas:
    def __init__(self, width, height, bgcolour = [0, 0, 0]):
        self.updated = False
        self.size = [width, height]
        self.matrix = [[bgcolour for _ in range(height)] for _ in range(width)]

        pygame.display.set_caption("Canvas 1")
        self.window = pygame.display.set_mode(self.size)
  
    #########################
    # - Scaling Functions - #
    #########################

    @staticmethod
    def _scaleMatrixBase(matrix, scaling, type):
        if type == "size": # [300, 600] -> [400, 800]
            return Canvas._scaleBySizeBase(matrix, scaling)
        if type == "scale": 
            if isinstance(scaling, int): # [300, 600] -> [300 * scale, 600 * scale]
                return Canvas._scaleByNumbersBase(matrix, [scaling, scaling])
            if isinstance(scaling, list): # [300, 600] -> [300 * scale[0], 600 * scale[1]]
                return Canvas._scaleByNumbersBase(matrix, scaling)

    @staticmethod
    def _scaleByNumbersBase(matrix, scale):
        size = [int(len(matrix) * scale[0]), int(len(matrix[0]) * scale[1])]
        return Canvas._scaleBySizeBase(matrix, size)
    @staticmethod
    def _scaleBySizeBase(matrix, size):
        matrix = Canvas._scaleBySizeX(matrix, size[0])
        matrix = Canvas._scaleBySizeY(matrix, size[1])

        return matrix, size
    
    @staticmethod
    def _scaleBySizeX(matrix, size):
        return Canvas._scaleBySize(matrix, size)
    @staticmethod
    def _scaleBySizeY(matrix, size):
        matrix = Canvas._scaleBySize(FlipMatrix(matrix), size)
        return FlipMatrix(matrix)
    
    @staticmethod
    def _scaleBySize(matrix, size):
        if len(matrix) == size:
            return matrix
        if len(matrix) < size:
            return Canvas._scaleBySizeUp(matrix, size)
        elif len(matrix) > size:
            return Canvas._scaleBySizeDown(matrix, size)
         
    @staticmethod
    def _scaleBySizeUp(matrix, size):
        currentSize = len(matrix)
        toAdd = size - currentSize
        newMatrix = []

        if toAdd > currentSize:
            stretch = toAdd // currentSize
            remainder = toAdd % currentSize

            rCounter = 0
            for set in matrix:
                newMatrix.append(set)
                
                count = stretch + (rCounter < remainder)
                for _ in range(count):
                    newMatrix.append(set)
                
                rCounter += 1

        elif currentSize > toAdd:
            addEvery = currentSize // toAdd

            counter = 0
            added = 0
            for set in matrix:
                newMatrix.append(set)
                if (not counter % addEvery) and (added < toAdd):
                    added += 1
                    newMatrix.append(set)
                
                counter += 1
        
        #print(f"Scale Up - Desired Size: {size}, Size: {len(newMatrix)}")

        return newMatrix[:size]
    @staticmethod
    def _scaleBySizeDown(matrix, size):
        newMatrix = matrix

        startSize = len(matrix)
        endSize = size
        toRemove = startSize - endSize
        spacing = startSize/toRemove

        removed = 0
        fPixelToRemove = 0
        while round(fPixelToRemove - removed) < len(newMatrix):
            fPixelToRemove += spacing
            if round(fPixelToRemove - removed) < len(newMatrix):
                newMatrix.pop(round(fPixelToRemove - removed))
                removed += 1

        #print(f"Scale Down - Desired Size: {size}, Size: {len(newMatrix)}")

        return newMatrix[:size]


    #######################
    # - Other Functions - #
    #######################

    def addLine(self, position, colour, direction):
        if isinstance(direction, int):
            direction = "horizontal" if direction else "vertical"
        direction = direction.lower()
        direction = "vertical" if direction == "down" else direction
        direction = "horizonal" if direction == "across" else direction
        
        if isinstance(position, int):
            position = [position]
        
        if direction == "horizontal":
            for pos in position:
                self.matrix = Canvas._addHorizontalLine(self.matrix, pos, colour)
        elif direction == "vertical":
            for pos in position:
                self.matrix = Canvas._addVertialLine(self.matrix, pos, colour)

    @staticmethod
    def _addHorizontalLine(matrix, position, colour):
        matrix = Canvas._addLine(FlipMatrix(matrix), position, colour)
        return FlipMatrix(matrix)
        
    @staticmethod
    def _addVertialLine(matrix, position, colour):
        return Canvas._addLine(matrix, position, colour)
    @staticmethod
    def _addLine(matrix, position, colour):
        matrix[position] = [colour]*len(matrix[position-1])
        
        return matrix

    def blitImage(self, img : Image, pos = [0,0], alphaOverride = None, **kwargs):
        if not alphaOverride:
            alpha = img.getAlpha()
        else:
            alpha = alphaOverride
        
        imgMatrix = img.getMatrix()
        if "scale" in list(kwargs.keys()):
            imgMatrix, size = Canvas._scaleMatrixBase(imgMatrix, kwargs["scale"], type="scale")
        if "size" in list(kwargs.keys()):
            imgMatrix, size = Canvas._scaleMatrixBase(imgMatrix, kwargs["size"], type="size")

        for x in range(0, len(imgMatrix)):
            for y in range(0, len(imgMatrix[0])):
                if imgMatrix[x][y] == alpha:
                    continue

                xx = x + pos[0]
                yy = y + pos[1]

                if xx > len(self.matrix)-1 or yy > len(self.matrix[0])-1:
                    continue
                else:
                    self.matrix[xx][yy] = imgMatrix[x][y]
        
        self.updated = False

    def saveImage(self, saveFile, type = "bin"):
        type = type.lower()
        if type == "bin":
            with open(f"{__file__.replace('Image.py', '')}/RawImages/{saveFile}.bin", "wb") as file:
                file.write(self.size[0].to_bytes(2, byteorder='big'))
                file.write(self.size[1].to_bytes(2, byteorder='big'))

                count = 0
                for x in range(self.size[0]):
                    for y in range(self.size[1]):
                        pixel = self.matrix[x][y]
                        if pixel:
                            file.write(pixel[0].to_bytes(1, byteorder='big'))
                            file.write(pixel[1].to_bytes(1, byteorder='big'))
                            file.write(pixel[2].to_bytes(1, byteorder='big'))
                            count += 1
        elif type == "jpeg" or "jpg":
            EncodeJPG(self.matrix, saveFile)
        else:
            raise ImageError(f"Unable to save to file type {type}")

    def getMatrix(self):
        return self.matrix
    def getSize(self):
        return self.size

    def update(self):
        if not self.updated:
            self.updated = True

            #print("Updating")

            for x, column in enumerate(self.matrix):
                if None in column:
                    column.remove(None)
                for y, pixel in enumerate(column):
                    if pixel:
                        pygame.draw.rect(self.window, pixel, (x, y, 1, 1))
        
            pygame.display.update()
