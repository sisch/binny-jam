# Letter of Sean ... or Was It Marque?
This repo will possibly become an entry to the [binny birthday jam](https://itch.io/jam/binnys-birthday-jam-2022)

## Outline
You commandeer a ship (nautical term™) and you have cannons. What you do not have is gold.
So sail away, plunder some ships, and upgrade yours.
Upgrades give you extended range, more cannons (shoot in parallel), 
Bathe (nautical term™) in the nostalgic feeling of playing a totally underrated mini game from a traditional Point&Click adventure from somewhere deep in the carribean.  
**No sword fights were fought during the production of this game.**

## How to win
Defeat all enemies

## How to start
- Make sure Python >=3.8 is installed on your system
- Create a virtual environment in your current directory by running `python -m venv env` in a terminal
- Activate the environment and install all dependencies
```shell
# Windows
env/Scripts/activate.ps1
# Unix
source env/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
- And run the game by typing:
```shell
python main.py
```

## Progress
- [x] Ship can move around and shoot
- [x] Ship does move faster with the wind and slower against it
- [ ] ~~Enemy ships spawn~~
- [x] Enemy ships move
- [x] Cannonballs interact with ships
- [x] Ships have a damage system
- [x] Upgrades for player ship
- [x] Show upgrade points and cannons available
- [x] Think of a win condition
- [x] Implement it!

## Controls
- Player Movement `Left`/`Right`
- Drop / Raise Anchor (Stop ship) `Down`
- Upgrade ship `Up` 
- Shooting (`Q`/`E`)
- Wind (test direction with `W`)


## License
MIT License &copy; 2022 Plantprogrammer (see [LICENSE](LICENSE))

Feel free to add, adapt, or otherwise tinker with the project. Especially writing enemy AI was 
completely out of scope of this game jam and would need some love :)  
