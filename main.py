import random
import globalstuff
from globalstuff import send_to_char, get_char_by_name
import commands
from time import time, sleep
import _thread
import intro
import factoids
import skills
import npcs
import rooms
import objects
import quests
import dungeons

def getcharinfo():
	while  True:
		name = input("Enter a name for your character: ").strip()
		if name.isalpha() and name != "" and name.find(' ') == -1:
			break
		else:
			print("Invalid character name.")
			continue
	while True:
		got_class = True
		charclass = input("Select a class(mage,warrior,rogue: ")
		for classcounter in globalstuff.classdict:
			if classcounter == charclass.lower():
				gamestate.playerchar = globalstuff.Character(gamestate, name,classcounter,globalstuff.classdict[classcounter].strength,globalstuff.classdict[classcounter].intellect,globalstuff.classdict[classcounter].charisma, 0)
		if got_class == True:
			break
		print("That is not a valid class, choose 'warrior', 'mage', or 'rogue': ")
		continue
				
	print("your base stats are:")
	print("strength:  %d" % gamestate.playerchar.strength)
	print("intellect: %d" % gamestate.playerchar.intellect)
	print("charisma:  %d" % gamestate.playerchar.charisma)
	print("You may specifies a transformation; default: all your stats up to 3 times.")
	rerolls = 0

	while True: #endless loop, exited eventually by a break statement
		reroll = input( "would you like to reroll your stats? [y/n]: ").lower()

		if rerolls >= 2 and len(reroll) > 0 and reroll.lower()[0] == 'y':
			print("You have reached the maximum number of rerolls. Your stats are as follows:")
			print("strength:  %d" % gamestate.playerchar.strength)
			print("intellect: %d" % gamestate.playerchar.intellect)
			print("charisma:  %d" % gamestate.playerchar.charisma)
			break	#the are done, so we exit the loop

		if reroll == "y" or reroll == "yes":
			rerolls = rerolls+1
			gamestate.playerchar.rerollstats()
			print("Your new stat's are as follows:")
			print("strength:  %d" % gamestate.playerchar.strength)
			print("intellect: %d" % gamestate.playerchar.intellect)
			print("charisma:  %d" % gamestate.playerchar.charisma)
			continue
		elif reroll == "n" or reroll == "no":
			print("OK, your stats have been set.")
			break	# exit the loop, as their stats have been set
		else:
			print("you must enter yes or no [y/n]")
			continue	#jump to the beginning of the loop

	globalstuff.send_to_char(gamestate.playerchar, "Welcome to the game. In order to get yourself aquainted with the commands, use the 'help' command." )
	commands.CMD_look(gamestate.playerchar,"")

def check_timers():
	for character in gamestate.charlist:
		if len(character.cooldowns) > 0:
			for event in character.cooldowns:
				if time() > event.endtime:
					if event.name == "attack":
						character.fight()
					character.cooldowns.remove(event)

		if len(character.timelimitedaffects) > 0:
			for event in character.timelimitedaffects:
				if time() > event.endtime:
					character.cooldowns.remove(event)
					send_to_char(character, event.wearofftext)

	if len(gamestate.respawntimers) > 0:
		for respawn in gamestate.respawntimers:
			if time() > respawn.endtime:
				gamestate.respawntimers.remove(respawn)
				npcs.spawn_npc(gamestate,respawn.name)

	if len(gamestate.decaytimers) > 0:
		for timer in gamestate.decaytimers:
			if time() > timer.endtime:
				timer.inlist.remove(timer.obj)
				gamestate.decaytimers.remove(timer)
				if type(timer.msgtarget) == globalstuff.Room:
					globalstuff.send_to_room(timer.msgtarget, "%s decays and turns to dust." % timer.obj.name)
				elif type(timer.msgtarget) == globalstuff.Character:
					send_to_char(timer.msgtarget,"%s decays and turns to dust." % timer.obj.name)
				else:
					print("decay timer msgtarget type unknown, aborting.")
					print(type,timer.msgtarget)
					exit(1)

def refresh_loop():
	while True:
		if gamestate.running == False:
			exit(0)
		for character in gamestate.charlist:
			if character.hp < character.max_hp():
				character.hp = character.hp + 10
				if character.hp > character.max_hp():
					character.hp = character.max_hp()
			if character.mana < character.max_mana():
				character.mana = character.mana + 10
				if character.mana > character.max_mana():
					character.mana = character.max_mana()
		sleep(20)
		if gamestate.running == False:
			exit(0)
		if gamestate.playerchar.sleeping == False:
			if gamestate.running == False:
				exit(0)
			sleep(20)
			if gamestate.playerchar.sleeping == False:
				if gamestate.running == False:
					exit(0)
				sleep(20)			
				if gamestate.playerchar.sleeping == False:
					if gamestate.running == False:
						exit(0)
					sleep(20)
					if gamestate.playerchar.sleeping == False:
						if gamestate.running == False:
							exit(0)
						sleep(20)
						if gamestate.playerchar.sleeping == False:
							if gamestate.running == False:
								exit(0)
							sleep(20)

def timer_loop():
	while True:
		if gamestate.running == False:
			exit(0)
		check_timers()
		sleep(1)
		continue


def maingameloop():
	rungame = True
	while rungame:
		ch = gamestate.playerchar

		ourinput = input("%d hp | %d mana > " % (ch.hp,ch.mana))
		ourinput = ourinput.strip()
		commandfound = False

		if ourinput != "":
			for command in globalstuff.commandlist:
				if gamestate.playerchar.sleeping == False or command.whileasleep == True:
					if  len(ourinput.split()) > 0 and ourinput.split()[0].lower() == command.name.lower():
						if ourinput.find(' ') == -1:
							args = ""
						else:
							args = ourinput.split(' ', 1)[1]
						command.function(gamestate.playerchar,args)
						commandfound = True
						break
				elif command.whileasleep == False and gamestate.playerchar.sleeping == True:
					if len(ourinput.split()) > 0 and ourinput.split()[0].lower() == command.name.lower():
						send_to_char(gamestate.playerchar,"You can't do that while sleeping.")
						commandfound = True
						break

			if commandfound != True:
				for alias, value in globalstuff.commandaliasdict.items():
					if len(ourinput.split()) > 0 and ourinput.split()[0].lower() == alias.lower():
						if ourinput.find(' ') == -1:
							args = ""
						else:
							args = ourinput.split(' ', 1)[1]
						if value[2] == False and gamestate.playerchar.sleeping == True:
							send_to_char(gamestate.playerchar,"You can't do that while sleeping.")
							commandfound = True
							break
						value[1](gamestate.playerchar,args)
						commandfound = True
						break

			if commandfound != True:
				skillfound = False
				skillallowed = True
				for skill in globalstuff.skilllist:
					if len(ourinput.split()) > 0 and ourinput.split()[0].lower() == skill.name.lower():
						if skill.classtype.lower() == globalstuff.classdict[gamestate.playerchar.charclass].name.lower():
							if gamestate.playerchar.sleeping == True:
								send_to_char(gamestate.playerchar,"You can't do that while you're sleeping.")
								commandfound = True
							else:
								skillfound = True
								cooldowndone = True
								ourskill = skill
								for skill2 in gamestate.playerchar.skills:
									if ourskill.name == skill2[0]:
										for cooldown in gamestate.playerchar.cooldowns:
											if cooldown.name == skill.name and skill.type == "skill":
												send_to_char(gamestate.playerchar, "you can't use that skill again yet, wait %d seconds between using this skill" % skill.cooldown)
												commandfound = True
												skillallowed = False
												cooldowndone = False
												executeskill = False

										if skillfound == True and skillallowed and cooldowndone == True:
											if ourinput.find(' ') == -1 and gamestate.playerchar.fightingtarget != None:
												args = gamestate.playerchar.fightingtarget.name
												executeskill = True
											elif ourinput.find(' ') == -1:
												if skill.needstarget == True:
													send_to_char(gamestate.playerchar, "You need a target.")
													executeskill = False
													commandfound = True
												else:
													args = ""
													executeskill = True
											else:		
												args = ourinput.split(' ', 1)[1]
												if get_char_by_name(gamestate.playerchar.inroom, args.lower() ) != None:
													executeskill = True
												else:
														executeskill = False
														send_to_char(gamestate.playerchar, "No target by that name.")
														commandfound = True
										if executeskill == True:
											canskill = False
											for skill2 in gamestate.playerchar.skills:
												if ourskill.name == skill2[0]:
													canskill = True
													if skill2[1] < 100:
														success = random.randrange(1,101)
														if success < skill2[1]:
															skill2[1] += 1
															globalstuff.send_to_char(ch,"You improve your %s skill level." % ourskill.name)
															retvals = ourskill.callskill(gamestate.playerchar, args)
															gamestate.playerchar.cooldowns.append(globalstuff.CooldownTimer(retvals[1],retvals[0]))
															commandfound = True
														else:
															globalstuff.send_to_char(ch,"You fail to properly use the %s skill. Perhaps you need more practice." % ourskill.name)
															gamestate.playerchar.cooldowns.append(globalstuff.CooldownTimer(ourskill.cooldown,ourskill.name))
															commandfound = True
													else:
														retvals = ourskill.callskill(gamestate.playerchar, args)
														gamestate.playerchar.cooldowns.append(globalstuff.CooldownTimer(retvals[1],retvals[0]))
														commandfound = True										
											if canskill == False:
												globalstuff.send_to_char(ch,"You need to learn that skill first")
												commandfound = True
		else:
			commandfound = True
		if commandfound == False:
			send_to_char(gamestate.playerchar, "command not found")
			check_timers()

#start the game
random.seed()
gamestate = globalstuff.GameState()
factoids.load_factoids(gamestate)
objects.load_objects(gamestate)
rooms.load_rooms(gamestate)
npcs.load_npcs(gamestate)
npcs.initspawn(gamestate)
gamestate.storelist.append(globalstuff.Store(gamestate,[2,3],[0,1,2,3,4,5],4,200,[4,5]))
skills.load_skills()
quests.load_quests(gamestate)
gamestate.dungeons.append(dungeons.Dungeon(gamestate,50,50,4,2,"There is a dungeon entrance here","This looks to be a natural cave formation, there is a small rocky opening\nin the ground which appears to open up into a vast network."))
intro.show_intro()
getcharinfo()
gamestate.playerchar.money = 10
_thread.start_new_thread(timer_loop, ())
_thread.start_new_thread(refresh_loop, ())
maingameloop()
