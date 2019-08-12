"""
__author__ = "Pablo Barros"

__version__ = "0.1"
__maintainer__ = "Pablo Barros"
__email__ = "pablovin@gmail.com"
__status__ = "Alpha"


Script that generates the PDFs for printing the cards.

"""



import cv2
import numpy
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from fpdf import FPDF


import qrcode
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=8,
    border=1,
)

#Directoy where the deck images and PDFs will be saved.
saveDeck = "/data/code/UnoCodes/unocodes/imgDeckExample/"

#Card size in pixels
cardSize = (336,240,3)
paperSize = (1048,760,3)


# Color of the deck cards: Red, Green, Blue, Yellow
colours = ("R", "G", "B", "Y")

#Numbers of the deck cards 1 to 10
numbers = list(range(10))[1:]


#Pritnable PDF
pdf = FPDF()

#Draw rotated text

def draw_rotated_text(image, angle, xy, text, fill, *args, **kwargs):
    """ Draw text at an angle into an image, takes the same arguments
        as Image.text() except for:

    :param image: Image to write text into
    :param angle: Angle to write text at
    """
    # get the size of our image
    width, height = image.size
    max_dim = max(width, height)

    # build a transparency mask large enough to hold the text
    mask_size = (max_dim * 2, max_dim * 2)
    mask = Image.new('L', mask_size, 0)

    # add text to mask
    draw = ImageDraw.Draw(mask)
    draw.text((max_dim, max_dim), text, 255, *args, **kwargs)

    if angle % 90 == 0:
        # rotate by multiple of 90 deg is easier
        rotated_mask = mask.rotate(angle)
    else:
        # rotate an an enlarged mask to minimize jaggies
        bigger_mask = mask.resize((max_dim*8, max_dim*8),
                                  resample=Image.BICUBIC)
        rotated_mask = bigger_mask.rotate(angle).resize(
            mask_size, resample=Image.LANCZOS)

    # crop the mask to match image
    mask_xy = (max_dim - xy[0], max_dim - xy[1])
    b_box = mask_xy + (mask_xy[0] + width, mask_xy[1] + height)
    mask = rotated_mask.crop(b_box)

    # paste the appropriate color, with the text transparency mask
    color_image = Image.new('RGBA', image.size, fill)
    image.paste(color_image, mask)




# Get the pixel colour of the cards
def getColor(c):


    print ("Color:", c)
    if c == "R":
        return (0, 0, 255)
    elif c == "G":
        return (0, 255, 0)
    elif c == "B":
        return (255, 0, 0)
    elif c == "Y":
        return (0, 255, 255)


#Iterate over the colours, numbers, and version (each card has 2 versions of the same colour/number).
for c in colours:
    allCards = []
    allBackCards = []
    for n in numbers:
        #2 versions of each card
        for i in list(range(2)):
            # e.g. R_0_0,R_0_1,R_1_0..., Y_R_0,Y_R_1
            id = c +"_"+ str(n)+"_" + str(i)

            #Make QrCode
            qr.add_data(id)
            qr.make(fit=True)

            qrCode = qr.make_image(fill_color="black", back_color="white")
            qrCodeImage = qr.make_image(fill_color="black", back_color="white")
            qrCodeImage.save(saveDeck + "QrCode.png")
            qrCodeImage = numpy.array(cv2.imread(saveDeck + "QrCode.png"))
            qrCodeImageShape = qrCodeImage.shape

            # Make Front Card
            card = numpy.zeros(cardSize, dtype=numpy.uint8)
            card.fill(255)

            # Add Border
            cv2.rectangle(card, (0, 0), (240, 336), (0,0,0), thickness=3)

            #Add backgroundColor
            color = getColor(c)
            cv2.rectangle(card, (10,10), (230,326), color , thickness=-1)

            #Add card Number top
            pillowImage = Image.fromarray(card)

            font = ImageFont.truetype("arial.ttf", 52)

            draw_rotated_text(pillowImage, 0, (20,10), str(n), (255, 255, 255), font=font)
            draw_rotated_text(pillowImage, 0, (180, 10), str(n), (255, 255, 255), font=font)

            # Add card Number top
            draw_rotated_text(pillowImage, 180, (50, 325), str(n), (255, 255, 255), font=font)
            draw_rotated_text(pillowImage, 180, (210, 325), str(n), (255, 255, 255), font=font)

            card = numpy.array(pillowImage)

            #Add QrCode to Card
            card[80:80+qrCodeImageShape[0], 25:25+qrCodeImageShape[1]] = qrCodeImage

            #SaveCard
            allCards.append(card)

            #Make back of the card
            cardBack = numpy.zeros(cardSize, dtype=numpy.uint8)
            cardBack.fill(0)

            # Add QrCode to BackCard
            cardBack[80:80 + qrCodeImageShape[0], 25:25 + qrCodeImageShape[1]] = qrCodeImage

            pillowImage = Image.fromarray(cardBack)

            font = ImageFont.truetype("arial.ttf", 52)

            cardBack = numpy.array(pillowImage)

            allBackCards.append(cardBack)

            #Clean the QR code for the next card
            qr.clear()

            # Only 1 zero card of each colour
            if n == 0:
                break

    #Create printable paper sheet front and back
    printablePaper = numpy.zeros(paperSize, dtype=numpy.uint8)
    printablePaper.fill(255)

    printableBackPaper = numpy.zeros(paperSize, dtype=numpy.uint8)
    printableBackPaper.fill(255)

    #Add cards to the printable paper sheet
    cardCounter = 0
    for cardNumber in range (2):
        for cardColumn in range(3):
            for cardRow in range(3):

                intervalPosition = 10

                printablePaper[intervalPosition+cardSize[0]*cardColumn: intervalPosition+cardSize[0]+cardColumn*cardSize[0], intervalPosition+cardSize[1]*cardRow: intervalPosition+cardSize[1]+cardRow*cardSize[1]] = allCards[cardCounter]

                #Back side - invert vertically so the back/front match

                intervalPositionX = 30
                intervalPositionY = 10
                printableBackPaper[
                intervalPositionY + cardSize[0] * cardColumn: intervalPositionY + cardSize[0] + cardColumn * cardSize[0],
                intervalPositionX + cardSize[1] * (2-cardRow): intervalPositionX + cardSize[1] + (2-cardRow) * cardSize[1]] = allBackCards[cardCounter]

                cardCounter = cardCounter + 1


        #Save the images as PNG
        cv2.imwrite(saveDeck + "Printable_"+str(c)+"_" +str(cardNumber)+".png", printablePaper)
        cv2.imwrite(saveDeck + "Printable_" + str(c) + "_" + str(cardNumber) + "Back.png", printableBackPaper)

        # Add the images to a printable PDF
        pdf.add_page()
        pdf.image(saveDeck + "Printable_"+str(c)+"_" +str(cardNumber)+".png", 0, 0, 210, 297)
        pdf.add_page()
        pdf.image(saveDeck + "Printable_" + str(c) + "_" + str(cardNumber) + "Back.png", 0, 0, 210, 297)

# Generate the printable PDF
pdf.output("/data/code/UnoCodes/unocodes/imgDeckExample/printableVersion.pdf", "F")
