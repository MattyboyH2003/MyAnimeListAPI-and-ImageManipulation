from copy import deepcopy
from numpy import uint8
from numpy import array as ndarray
from simplejpeg import encode_jpeg, decode_jpeg, decode_jpeg_header

def FlipMatrix(l : list) -> list:
    y = len(l)
    x = len(l[0])

    matrix = [[None for _ in range(y)] for _ in range(x)]

    for yy in range(y):
        for xx in range(x):
            matrix[xx][yy] = l[yy][xx]
    
    return matrix

def DecodeJPG(filePath):
    with open(filePath, "rb") as f:
        fileContents = f.read()
        size = list(decode_jpeg_header(deepcopy(fileContents))[:2]) # Gets the size of the image (y, x)
        size.reverse() # Flips image size to (x, y)
        matrix = FlipMatrix(decode_jpeg(deepcopy(fileContents)).tolist())

    return matrix, size

def EncodeJPG(matrix, filePath):
    matrix = FlipMatrix(matrix)
    arr = ndarray(matrix, dtype = uint8)

    with open(filePath, "wb") as f:
        f.write(encode_jpeg(arr))
