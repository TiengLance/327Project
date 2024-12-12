import struct
# String to binary
def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

# Converts binary to string
def binary_to_message(binary):
    chars = [chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)]
    return ''.join(chars)

def read_bmp(file):
      with open(file, "rb") as f:
            # Read BMP header
            header = f.read(54)

            # Gets width, height, and bits per pixel or bpp
            width = struct.unpack("<I", header[18:22])[0]
            height = struct.unpack("<I", header[22:26])[0]
            bpp = struct.unpack("<H", header[28:30])[0]

            # Needs to be 24 bits becuase 3 values, r, g, b, 8 bits each.
            if bpp != 24:
                  return print("Only 24-bit BMP images are supported.")

            # Ensures that the image stays aligned because of the bit padding neeading to be in multipels of 4.
            RPad = (4 - (width * 3 % 4)) % 4

            #Reads pixel value from bottom row up
            pixels = []
            for y in range(height - 1, -1, -1):
                  row = []
                  for x in range(width):
                        b, g, r = struct.unpack("<BBB", f.read(3))
                        row.append((r, g, b))
                  pixels.append(row)
                  # Ignores the padding of file
                  f.read(RPad)
      return pixels, width, height, RPad
def write_bmp(file, pixels, width, height, RPad):
      with open(file, "wb") as f:
            # Reads and copies BMP header to other header
            header = bytearray(54)
            struct.pack_into("<2sIHHIIIIHHIIIIII", header, 0, b"BM", 54 + (width * 3 + RPad) * height, 0, 0, 54, 40, width, height, 1, 24, 0, (width * 3 + RPad) * height, 0, 0, 0, 0)
            f.write(header)

            # Writes pixel data to the new encrypted file
            for row in (pixels):
                  for r, g, b in row:
                        f.write(struct.pack("<BBB", b, g, r))
                  #Adds the row padding
                  f.write(b'\x00' * RPad)

def encode_message(pixels, message):
      #Adds delimeter 
      binary_message = message_to_binary(message) + '1111111111111110'
      message_index = 0
      message_length = len(binary_message)
      #Encodes pixel by reading he least signigicant bit, if it needs to be changed add 1 if not do nothing
      for row in pixels:
            for i in range(len(row)):
                  pixel = list(row[i])
                  for j in range(3):            
                        if message_index < message_length:
                              pixel[j] = (pixel[j] & ~1) | int(binary_message[message_index])
                              message_index += 1
                  row[i] = tuple(pixel)
                  if message_index >= message_length:
                        return pixels
      return print("Not enough pixels")

def decode(pixels):
      binary_message = ''
      #Gets the least significant bit from color and adds to our binary string
      for row in pixels:
            for pixel in row:
                  for color in pixel:
                        binary_message += str(color & 1)
      #If delimiter is read then return binary_to_message(binnary_message)
      delimiter = '1111111111111110'
      #Removes delimiter fromm the binary message
      if delimiter in binary_message:
            binary_message = binary_message[:binary_message.index(delimiter)]
      else:
            return print("No message found in image (Delimiter was not read)")

      return binary_to_message(binary_message)

#Will ask for user inputs for nescessary information for encoding and decoding messages quit to exit program
def start():
      while(True):
            choice = input("Please enter if you want to encode or decode a bmp file (decode/encode/quits): ")
            if choice == "decode":
                  userFile = input("Please enter the name of the file you wish to decode (Include ender, image.bmp): ")
                  EPixels, _,_,_ = read_bmp(userFile)
                  message = decode(EPixels)
                  rmessage = binary_to_message(message)
                  print("Here is your decoded message: " + rmessage)
            elif (choice == "encode"):
                  userFile = input("Please enter the name of the file you wish to encode (Include ender, image.bmp): ")
                  message = input("Please enter message to be encoded into file: ")
                  binaryM = message_to_binary(message)
                  pixels, width, height, RPad = read_bmp(userFile)            
                  encodedPixels = encode_message(pixels, binaryM)
                  outputFile = input("Please enter the name of encoded file (Include ender .bmp to file)")
                  write_bmp(outputFile, encodedPixels, width, height, RPad)
            elif (choice == "quit"):
                  break
start()
