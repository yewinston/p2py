from src.protocol import *
import base64

ENCODING = 'utf-8'

def encodeToBytes(file_name:str):
    pieces = []
    numPieces = 0
    with open(file_name, "rb") as input_file:
        piece = input_file.read(PIECE_SIZE)
        while piece:
            numPieces+=1
            encodedPiece = base64.b64encode(piece)
            hexPiece = encodedPiece.decode(ENCODING)
            pieces.append(hexPiece)
            piece = input_file.read(PIECE_SIZE)
    return pieces, numPieces

def decodeToFile(pieces:[], output_name:str):
    with open(output_name, "wb") as output_file:
        for block in pieces:
            encodedBlock = block.encode(ENCODING)
            decodedBlock = base64.b64decode(encodedBlock)
            output_file.write(decodedBlock)


# TESTING:
# pieces, numPieces = encodeToBytes("./files/sample.txt")
# print(numPieces)
# decodeToFile(pieces, "./files/output.txt")

# pieces, numPieces = encodeToBytes("./files/sfu_sample.png")
# print(numPieces)
# decodeToFile(pieces, "./files/sfu_output.png")
