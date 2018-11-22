# showdown-battle-bot

Socket battle bot for the pokemon simulator [Pokemon Showdown](http://pokemonshowdown.com). Developped in Python 3.5.X

### Requirements
- python 3.5.X
- requests
- asyncio
- websockets

### Supported formats
- gen7randombattle
- gen7monotyperandombattle
- gen7hackmonscup
- gen7challengecup1v1
- gen6battlefactory
- gen7bssfactory

(More upcoming)

### Installation
```
pip3 install -r requirements.txt
./main
```

### How does that works
The bot works in three parts : I/O process, game engine and AI.
  
I/O process is about sending and receiving datas from Showdown's servers.  
Showdown use websockets to send datas, therefor I use them too. 
Then all I had to do is to follow the [Pokemon Showdown Protocol](https://github.com/Zarel/Pokemon-Showdown/blob/master/PROTOCOL.md). 
Tricky part is about connection, the protocol is not very precise about it.
To be simple, once connected to the websockets' server, you receive a message formated this way : `|challstr|<CHALLSTR>`. 
Then you send a post request to `https://play.pokemonshowdown.com/action.php` with the `<CHALLSTR>` but web-formated (beware of special characters) and the ids of the bot.
In the answer, you have to extract the `assertion` part.
Finally, you have to send a websrequest this format : `/trn <USERNAME>,0,<ASSERTION>` where `<USERNAME>` is the one you gave previously and `<ASSERTION>` the one you extract just before.
For more informations about it, check the [login.py](src/login.py) file.

Game engine is about simulate battles, teams and pokemons.  
For each battle, an object is created and filled with informations sent by Showdown's servers. 
For the unkowns informations (enemy's team), moves are filled thanks to a file take from source code where moves and pokemons are listed.
See [data](data/) forlder for more informations.

Bot's brain, the AI.  
At the moment I write theses lines, the AI is static. It means if you put the bot in the same situation X times, it will act the same way X times.
On each turn, a player (here, the bot) has the choice between switch and use a move.
To choose the move, the bot "just" calculate the efficiency of each move based on base power, stats, typechart, items and abilities.
To choose a pokemon to switch, the bot will parse every of its pokemons and calculate its efficiency based on speed and moves power (same calculus as the above one).
All the difficulty of building the bot is to choose between use a move and switch. 
What I mean here is : I (the bot) know that this pokemon is dangerous, but is it enough dangerous to switch, or attack is more interresting ?
Today, this choice is manual. There is a value beyond wich the bot switch.
In the long term, I would like to modify this behavior to allow the bot to evolve, based on its previous experiences, but that's hard and I miss some knowledge.

More informations (FR only) : https://drive.google.com/file/d/0B7f94AM8vUSONWIyX1cwOWNVQ1k
