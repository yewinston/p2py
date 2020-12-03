import protocol as p

def encodeToBytes(file_name):
    pieces = []
    numPieces = 0
    with open(file_name, "rb") as input_file:
        piece = input_file.read(p.PIECE_SIZE)
        while piece:
            numPieces+=1
            pieces.append(piece)
            piece = input_file.read(p.PIECE_SIZE)
    return pieces, numPieces

def decodeToFile(pieces, output_name):
    with open(output_name, "wb") as output_file:
        for block in pieces:
            output_file.write(block)


# TESTING:
# pieces, numPieces = encodeToBytes("./files/sample.txt")
# print(numPieces)
# decodeToFile(pieces, "./files/output.txt")

# pieces, numPieces = encodeToBytes("./files/sfu_sample.png")
# print(numPieces)
# decodeToFile(pieces, "./files/sfu_output.png")
