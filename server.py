# Author: Nick Francisco
# CS 372 Spring 2023
# Date: 6/6/2023

from socket import *

# Header Length
HEADER = 10
# Max send size
SEND_LIMIT = 4096
# host and port
serverName = '127.0.0.1'
serverPort = 56108


# Sends msg to socket
def sendMessage(clientSocket, msg):
    # Encode and get bytes
    encoded = msg.encode()
    numBytes = len(encoded)

    # Set and send message header
    message_header = f"{len(msg):<{10}}".encode()
    clientSocket.send(message_header)

    # Send message
    if numBytes <= SEND_LIMIT:
        clientSocket.send(msg.encode())
    else:
        # Split string into SEND_LIMIT byte strings
        split = [msg[i:i + SEND_LIMIT] for i in range(0, len(msg), SEND_LIMIT)]
        for i in range(len(split)):
            clientSocket.send(split[i].encode())


# Receive message from socket
def recvMessage(clientSocket):
    # Receive header with message length
    messageHeader = clientSocket.recv(10)
    messageLength = int(messageHeader.decode().strip())

    # Receive message
    if messageLength <= SEND_LIMIT:
        message = clientSocket.recv(messageLength).decode()
        return message
    else:
        message = ""
        bytesRec = 0
        while bytesRec < messageLength:
            m = clientSocket.recv(SEND_LIMIT).decode()
            message += m
            bytesRec += len(m)
        return message


# Prints tictactoe board with moves from arr
def printBoard(arr):

    board = "    1  |  2  |  3  \n" \
         "A   0  |  0  |  0  \n" \
         "  -----+-----+-----\n" \
         "B   0  |  0  |  0  \n" \
         "  -----+-----+-----\n" \
         "C   0  |  0  |  0  \n" \

    j = 0
    boardList = list(board)

    # Change 0s with moves from arr
    for i in range(len(boardList)):
        if boardList[i] == '0':
            boardList[i] = arr[j]
            print(boardList[i], end='')
            j += 1
        else:
            print(boardList[i], end='')

    # Return modified string
    boardFilled = ""
    boardFilled = boardFilled.join([str(elem) for elem in boardList])
    return boardFilled


# Get row input from user
def getRow():

    # Get valid input from user
    while 1:
        row = input("Enter a row (A,B,C): ")
        if row == 'A' or row == 'B' or row == 'C':
            return row
        else:
            print("Invalid row")


# Get col input from user
def getCol():

    # Get valid input from user
    while 1:
        col = input("Enter a col (1,2,3): ")
        if col == '1' or col == '2' or col == '3':
            return col
        else:
            print("Invalid col")


# Get index position for row and col input
def rolColToIndex(r, c):
    i = 0
    if r == 'A':
        i = (int(c) - 1)
    elif r == 'B':
        i = (int(c) - 1) + 3
    elif r == 'C':
        i = (int(c) - 1) + 6

    return i


# Check for winner in arr with char player
def checkWinner(arr, player):

    # Check horizontals
    if arr[0] == arr[1] == arr[2] and arr[0] == player:
        return True
    elif arr[3] == arr[4] == arr[5] and arr[3] == player:
        return True
    elif arr[6] == arr[7] == arr[8] and arr[6] == player:
        return True
    
    # Check verticals
    elif arr[0] == arr[3] == arr[6] and arr[0] == player:
        return True
    elif arr[1] == arr[4] == arr[7] and arr[1] == player:
        return True
    elif arr[2] == arr[5] == arr[8] and arr[2] == player:
        return True
    # Check diagonals

    elif arr[0] == arr[4] == arr[8] and arr[0] == player:
        return True
    elif arr[2] == arr[4] == arr[6] and arr[2] == player:
        return True


# Checks for draw by checking available spaces in arr
def checkDraw(arr):
    emptySpace = 0
    # Check for draw
    for elem in arr:
        if elem == ' ':
            emptySpace += 1

    # Draw
    if emptySpace == 0:
        draw = True
        return draw

    return False

# Receive message from client and send message to client
# Checks for /q command and play tic tac toe input
def serverChat(clientSocket, chat, rule):

    # Display rules for first input
    if rule:
        print("Type /q to quit")
        print("Enter a message to send. Please wait for input prompt before entering message...")
        print('Note: Type "play tic tac toe" to start a game of tictactoe')
        rule = False

    # Recv message
    message = recvMessage(clientSocket)

    # Check for quit message
    if message == "/q":
        print("Client requested shutdown. Shutting Down!")
        # Close socket
        clientSocket.close()
        quit()

    # Check for play message
    if message == "play tic tac toe":
        chat = False
        return chat, rule

    # Print client message
    print("From client: ", message)

    # Send response
    data = input("Enter input > ")

    # Set response header
    response_header = f"{len(data):<{HEADER}}".encode()
    clientSocket.send(response_header + data.encode())

    # Close client connection
    clientSocket.close()

    # If sending exit signal don't exit program
    if data == "/q":
        print("Shutting Down!")
        quit()

    # If sending play wait for client to make first move
    if data == "play tic tac toe":
        chat = False

    return chat, rule


# Plays a round of tic tac toe
# Gets a move from the user, sends move to server,
# waits for server move and checks for winner
def playRound(clientSocket, play):

    # Get client move
    clientMove = recvMessage(clientSocket)

    # Update Moves
    updatedMoves = list(clientMove)

    # Check if client won
    if checkWinner(updatedMoves, 'X'):
        printBoard(updatedMoves)
        print("You lost!")
        play = False
        return updatedMoves, play

    # Check for draw after client move
    if checkDraw(updatedMoves):
        printBoard(updatedMoves)
        print("Draw")
        play = False
        return updatedMoves, play

    # Display current board
    printBoard(updatedMoves)

    # Display rules
    print("Enter a row and then a column to place an 0")

    # Check for invalid move
    invalid = True
    while invalid:

        # Get input from user
        row = getRow()
        col = getCol()

        # Row, Col to index position
        index = rolColToIndex(row, col)

        # If valid
        if updatedMoves[index] == ' ':
            updatedMoves[index] = 'O'
            invalid = False
        else:
            print("Invalid move")

    # String of moves to send to client
    movesString = ""
    movesString = movesString.join([str(elem) for elem in updatedMoves])

    # Send client move
    sendMessage(clientSocket, movesString)

    # Check if server one
    if checkWinner(updatedMoves, 'O'):
        printBoard(updatedMoves)
        print("You won!")
        play = False
        return updatedMoves, play

    # Check for draw after server move
    if checkDraw(updatedMoves):
        printBoard(updatedMoves)
        print("Draw")
        play = False
        return updatedMoves, play

    return updatedMoves, play


# Infinite loop to communicate or play tic tac toe
# with client program until quit command received
def server():

    # Set up listening socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind((serverName, serverPort))
    serverSocket.listen(1)
    print(f"Server listening on: localhost on port: {serverPort}")

    chatting = True
    playing = False
    rules = True
    moves = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']

    # Respond to client
    while 1:

        # Accept connection
        connectionSocket, addr = serverSocket.accept()
        if rules:
            print(f"Connected by ('{serverName}', {serverPort})")

        if chatting:
            chatting, rules = serverChat(connectionSocket, chatting, rules)
            if not chatting:
                playing = True
        elif playing:
            moves, playing = playRound(connectionSocket, playing)
            if not playing:
                chatting = True

# Start server
server()
