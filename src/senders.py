async def sender(websocket, room, message1, message2=None):
    """
    Default websocket sender. Format message and send websocket.
    :param websocket: Websocket stream.
    :param room: Room name.
    :param message1: First part of message.
    :param message2: Second part of message. Optional.
    """
    if message2:
        string = room + '|' + message1 + '|' + message2
    else:
        string = room + '|' + message1
    print('>> {}'.format(string))
    await websocket.send(string)

async def searching(websocket):
    """
    Format search websocket, call sender function.
    :param websocket: Websocket stream.
    """
    await sender(websocket, "", "/search gen7randombattle")

async def challenge(websocket, player):
    """
    Format challenging websocket, call sender function.
    :param websocket: Websocket stream
    :param player: Player name.
    """
    await sender(websocket, "", "/challenge " + player + ", gen7randombattle")

async def sendmessage(websocket, room_id, message):
    """
    Format text websocket, call sender function.
    :param websocket: Websocket stream.
    :param room_id: Room name.
    :param message: Message to sent.
    """
    await sender(websocket, "battle-gen7randombattle-" + room_id, message)

async def sendmove(websocket, room_id, move, turn):
    """
    Format move choice websocket, call sender function.
    :param websocket: Websocket stream.
    :param room_id: Room name.
    :param move: Move id (1, 2, 3, 4).
    :param turn: Battle turn (1, 2, ...). Different from the one sent by server.
    """
    await sender(websocket, "battle-gen7randombattle-" + room_id, "/choose move " + str(move), str(turn))

async def sendswitch(websocket, room_id, pokemon, turn):
    """
    Format switch choice websocket, call sender function.
    :param websocket: Websocket stream.
    :param room_id: Room name.
    :param pokemon: Pokemon id (1, 2, 3, 4, 5, 6).
    :param turn: Battle turn (1, 2, ...). Different from the one sent by server.
    """
    await sender(websocket, "battle-gen7randombattle-" + room_id, "/choose switch " + str(pokemon), str(turn))

async def leaving(websocket, room_id):
    """
    Format leaving room websocket, call sender function.
    :param websocket: Websocket stream.
    :param room_id: Room name.
    """
    await sender(websocket, "", "/leave battle-gen7randombattle-" + room_id)
