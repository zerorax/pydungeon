def show_intro():
	print( """Welcome to the game,
I am currently in the very early stages of development.
Eventually there will be a tutorial inside the game that
will teach you to play, but for now I've created this
introduction section so you understand the commands and
mechanics I have so far implemented and can experiment
with the game engine/
Press [ENTER] to continute or type 'skip' followed by
[ENTER] to skip directly to the game""" )
	introq = input("")
	if introq.lower() == "skip":
		pass
	else:
		print("""The first thing you need to know, is that
you move by typing the direction of an exit in the room you
are in(north, south, east, west). You can pick up items from
the ground with the get command. You can drop items with the
drop command. You can get items from containers with the get
command, for example 'get a wooden sword from the corpse of
a giant troll' will take the object 'a wooden sword' from the
object on the ground called 'the corpse of a giant troll'. You
can also get items from containers in your inventory. The first
thing you will want to do is get some gear. You can find equipment
and other items in the corpses of your enemies. To kill them
initiate a fight with the attack command or with an offensive
skill or spell.""")
		introq = input("Press [ENTER] to continue.")
		print("""There is a couple test NPC's that have useful
items you can loot after killing them, and for now the leveling
rate is very fast for testing purposes. Once you get an item
from someones corpse, you can equip it with with equip command.
If you want to change items, you can use the remove command to
remove an item you are wearing. You can look at items using the
look command, followed by the word at, followed by the items name.
The look command without any arguments will show you the room you
are in and it's contents. Using the look command with an exit
direction will show you the room in that direction, if there is
one. You can always type score to see your progress in the game.
You can use offensive skills in a fight without an argument  If
you include an argument, it will be assumed to be your target.
Currently the only skill is kick for warriors, can you can 
cast the fireball spell with a target or while fighting. To
see a list of all available commands at this time use the
commands command, and every command has help text which you can
find with the help command.
""")
		introq = input("Press [ENTER] to continue.")
		return
