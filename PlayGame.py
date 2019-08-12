"""
__author__ = "Pablo Barros"

__version__ = "0.1"
__maintainer__ = "Pablo Barros"
__email__ = "pablovin@gmail.com"
__status__ = "Alpha"


Script that logs a UNO game.

"""


import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import datetime
import pyttsx3
engine = pyttsx3.init()

import csv


#directoy and file name of where the log will be saved.
saveLog = "dealingDrawDiscard.csv"

#How many cards each player starts with
drawCardsPerPlayer = 5

frameNumber = 0


with open(saveLog, mode='w') as saveLogFile:
    saveLogWriter = csv.writer(saveLogFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    saveLogWriter.writerow(['Time', 'Event', "Actor", 'Player1', 'Player2', 'Player3', 'Player4', 'discardPile'])

cap = cv2.VideoCapture(0)

#Cards that each player has in their hands
player1 = []
player2 = []
player3 = []
player4 = []

#Cards that were discarded
discarded = []


currentTurn = 0

#Current cards on the deck/discarded pile
currentCardDeck = ""
currentDiscard = ""


lastAction = ""
currentPlayer = ""

action = "draw"

def decodeCard(image):
    barcodes = decode(image)
    barcodeData = "none"

    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw the
        # bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # the barcode data is a bytes object so if we want to draw it on
        # our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)

        # print the barcode type and data to the terminal
        #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

    return image, barcodeData


#Saves an action on the log
def recordAction(card, currentTurn, actionWrite ):

    timeNow = datetime.datetime.now()

    with open(saveLog, mode='a') as saveLogFile:
        saveLogWriter = csv.writer(saveLogFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        saveLogWriter.writerow(
            [timeNow, str(actionWrite)+"_"+str(card), str(currentTurn), str(player1), str(player2), str(player3), str(player4), str(discarded)])



def dealCard(player, card, currentTurn):

    if player == 1:
        player1.append(card)
    elif player == 2:
        player2.append(card)
    elif player == 3:
        player3.append(card)
    elif player == 4:
        player4.append(card)

    recordAction(card, currentTurn, "Deal Card")


def isEndGame():
    if len(player1) == 0:
        return 1
    elif len(player2) == 0:
        return 2
    elif len(player3) == 0:
        return 3
    elif len(player4) == 0:
        return 4

    return -1


phrase = ""


while(True):

    # Capture frame-by-frame
    ret, frame = cap.read()

    timeNow = datetime.datetime.now()


    #Cut the region of the deck and discard pile
    deck = frame [0:-1, 0:300]
    discard = frame[0:-1, 350:-1]

    # Decode the deck and discard pile
    deck,cardDeck = decodeCard(deck)
    discard, cardDiscard = decodeCard(discard)

    if cardDeck == "none":
        cardDeck = currentCardDeck

    #Check action
    if action == "player turn":

        #Player discard a card


        if not cardDiscard == "none" and not currentDiscard == cardDiscard:
                lastPlayer = currentPlayer

                removeFrom = 0
                discarded.append(cardDiscard)
                if cardDiscard in player1:
                    player1.remove(cardDiscard)
                    removeFrom = 1
                    currentPlayer = 1

                    if len(player1)==1:
                        engine.say("Player " + str(1) + " says Uno.")
                        engine.runAndWait()

                elif cardDiscard in player2:

                    player2.remove(cardDiscard)
                    removeFrom = 2
                    currentPlayer = 2

                    if len(player2)==1:
                        engine.say("Player " + str(2) + " says Uno.")
                        engine.runAndWait()

                elif cardDiscard in player3:
                    removeFrom = 3
                    player3.remove(cardDiscard)
                    currentPlayer = 3

                    if len(player3)==1:
                        engine.say("Player " + str(3) + " says Uno.")
                        engine.runAndWait()

                elif cardDiscard in player4:
                    removeFrom = 4
                    player4.remove(cardDiscard)
                    currentPlayer = 4

                    if len(player4)==1:
                        engine.say("Player " + str(4) + " says Uno.")
                        engine.runAndWait()


                engine.say("Player "+str(currentPlayer)+" discarded a card.")
                engine.runAndWait()
                phrase = "Player "+str(currentPlayer)+" discarded a card."

                currentDiscard = cardDiscard

                currentPlayer = currentPlayer+1
                if currentPlayer > 4:
                    currentPlayer = 1

                lastAction = "discard"

                recordAction(cardDiscard, removeFrom, actionWrite="discard")

                #verify end of the game
                if isEndGame() == -1:
                    engine.say("Player " + str(currentPlayer) + " must do its action.")
                    engine.runAndWait()
                    phrase = "Player " + str(currentPlayer) + " must do its action."
                else:
                    engine.say("Player " + str(isEndGame()) + " wins the game.")
                    engine.runAndWait()
                    phrase = "Player " + str(currentPlayer) + " wins the game."
                    break



        # Player Draw Card
        elif not cardDeck == "none" and not currentCardDeck == cardDeck:


            if lastAction == "draw":
                currentPlayer = currentPlayer + 1
                if currentPlayer > 4:
                    currentPlayer = 1
                    engine.say("Player " + str(currentPlayer) + " is playing now.")
                    engine.runAndWait()
                    phrase = "Player " + str(currentPlayer) + " is playing now."


            addTo = 0
            if currentPlayer == 1:
                player1.append(currentCardDeck)

            elif currentPlayer == 2:
                player2.append(currentCardDeck)

            elif currentPlayer == 3:
                player3.append(currentCardDeck)


            elif currentPlayer == 4:
                player4.append(currentCardDeck)


            engine.say("Player " + str(currentPlayer) + " drew a card.")
            engine.runAndWait()

            phrase = "Player " + str(currentPlayer) + " drew a card."


            recordAction(currentCardDeck, currentPlayer, actionWrite="draw")

            lastPlayer = currentPlayer

            lastAction = "draw"

            currentCardDeck = cardDeck

    #Deal cards
    if not currentCardDeck == cardDeck and action=="draw":

        if currentTurn > 0:
            engine.say("Deal card for player " + str(currentTurn))
            engine.runAndWait()
            phrase = "Deal card for player "

        dealCard(currentTurn,currentCardDeck, currentTurn)
        if len(player4) == drawCardsPerPlayer:
            action= "draw discard"
            engine.say("Now turn the first discard card.")
            engine.runAndWait()

            phrase = "Now turn the first discard card."


        currentCardDeck = cardDeck
        currentTurn = currentTurn + 1
        if currentTurn > 4:
            currentTurn = 1

    # Draw first card for the discarded pile
    if not currentCardDeck == cardDeck and action == "draw discard":
        engine.say("Discard card turned.")
        engine.runAndWait()
        discarded.append(currentCardDeck)
        currentDiscard = currentCardDeck
        recordAction(currentCardDeck, 0, "Draw Discard")
        action ="player turn"

        currentPlayer = 1
        engine.say("Player 1 start game.")
        engine.runAndWait()
        phrase = "Player 1 start game."

    currentCardDeck = cardDeck


    cv2.putText(frame, phrase + str(currentTurn),
                (15, 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, str(timeNow), (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    #Saves the images
    cv2.imwrite("/data/code/UnoCodes/unocodes/savedImages/"+str(frameNumber)+".png", frame)
    frameNumber = frameNumber+1



    # Display the resulting frame
    cv2.imshow('discard', discard)
    cv2.imshow('deck', deck)
    cv2.imshow('Game', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
