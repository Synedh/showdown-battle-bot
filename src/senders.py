from datetime import datetime


class Sender():
    """
    Class singleton to send showdown messages.
    """

    def __new__(cls, _=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Sender, cls).__new__(cls)
        return cls.instance

    def __init__(self, websocket=None):
        if not hasattr(self, 'websocket'):
            self.websocket = websocket
        if not self.websocket:
            raise ValueError('Field "websocket" needs to be initialised at least one time.')

    async def send(self, room: str, *messages: str):
        """
        Default websocket sender. Format message, log and send websocket.
        :param room: Room name.
        :param messages: List of messages to send.
        """
        string = f'{room}|{"|".join(messages)}'
        print(f'[{datetime.now().replace(microsecond=0).isoformat()}] >> {string}')
        await self.websocket.send(string)

    async def searching(self, battle_format: str):
        """
        Battle search, call sender function.
        :param battle_format: String, battle format.
        """
        await self.send('', f'/search {battle_format}')

    async def challenge(self, player: str, battle_format: str):
        """
        Send challenge to player in format, call sender function.
        :param player: Player name.
        :param battle_format: String, battle format.
        """
        await self.send('', f'/challenge {player}, {battle_format}')

    async def sendmove(self, battletag: str, move: int, turn: int):
        """
        Battle move choice, call sender function.
        :param battletag: Battletag string.
        :param move: Move id (1, 2, 3, 4).
        :param turn: Battle turn (1, 2, ...). Different from the one sent by server.
        """
        await self.send(battletag, f'/choose move {move}', str(turn))

    async def sendswitch(self, battletag: str, pokemon: int, turn: int):
        """
        Battle switch choice, call sender function.
        :param battletag: Battletag string.
        :param pokemon: Pokemon id (1, 2, 3, 4, 5, 6).
        :param turn: Battle turn (1, 2, ...). Different from the one sent by server.
        """
        await self.send(battletag, f'/choose switch {pokemon}', str(turn))

    async def leaving(self, battletag: str):
        """
        Leaving room, call sender function.
        :param battletag: Battletag string.
        """
        await self.send('', f'/leave {battletag}')

    async def forfeit(self, battletag: str):
        """
        Forfeit and leave battle, call sender function.
        :param battletag: Battletag string.
        """
        await self.send(battletag, '/forfeit')
        await self.leaving(battletag)
