async def sender(websocket, room, message1, message2=None):
    if message2:
        string = room + '|' + message1 + '|' + message2
    else:
        string = room + '|' + message1
    print('>> {}'.format(string))
    await websocket.send(string)

async def searching(websocket):
    await sender(websocket, "", "/search gen7randombattle")

async def challenge(websocket, player):
    await sender(websocket, "", "/challenge " + player + ", gen7randombattle")

async def sendmessage(websocket, room_id, message):
    await sender(websocket, "battle-gen7randombattle-" + room_id, message)

async def sendmove(websocket, room_id, move, turn):
    await sender(websocket, "battle-gen7randombattle-" + room_id, "/choose move " + str(move), str(turn))

async def sendswitch(websocket, room_id, pokemon, turn):
    await sender(websocket, "battle-gen7randombattle-" + room_id, "/choose switch " + str(pokemon), str(turn))

async def leaving(websocket, room_id):
    await sender(websocket, "", "/leave battle-gen7randombattle-" + room_id)
