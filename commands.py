import globalstuff
import objects
import skills
import random

def CMD_use(ch,args):
	if args == "":
		globalstuff.send_to_char(ch,"use what?")
		return
	if ch.inroom.usables != []:
		if args.find(' ') == -1:
			words = [args.lower().strip()]
		else:
			words = args.lower().strip().split()
		for usable in ch.inroom.usables:
			if args.lower().strip() in usable.name.lower():
				usable.beused(ch)
				return
		for usable in ch.inroom.usables:
			if all(word in usable.keywords for word in words):
				usable.beused(ch)
				return
		for usable in ch.inroom.usables:
			if any(word in usable.keywords for word in words):
				usable.beused(ch)
				return
		globalstuff.send_to_char(ch,"There is no object here by that name to use.")
	else:
		globalstuff.send_to_char(ch, "You don't see an item by that name to use.")

def CMD_quests(ch,args):
	if ch.questlist == []:
		globalstuff.send_to_char(ch,"You don't have any quests currently.")
	else:
		for quest in ch.questlist:
			globalstuff.send_to_char(ch, quest.name)
			globalstuff.send_to_char(ch, quest.questinfo)
			globalstuff.send_to_char(ch, "")


def CMD_search(ch,args):
	if ch.inroom.contents != []:
		for item in ch.inroom.contents:
			if "hidden" in item.flaglist:
				globalstuff.send_to_char(ch,"You uncover %s in your search." % item.name)
				ch.foundhidden.append(item)
				return
	globalstuff.send_to_char(ch,"You find nothing.")

def CMD_learn(ch,args):
	if args.find(" ") != -1:
		if args.split(' ',1)[0] == "from":
			targetname = args.split(' ',1)[1].strip()
			target = globalstuff.get_char_by_name(ch.inroom,targetname)
			if target == None:
				globalstuff.send_to_char(ch,"There is no one by that name here to learn from.")
				return
			if "skillteacher" not in target.flags:
				globalstuff.send_to_char(ch, "That character does not teach any skills")
				return
			if target.skills == []:
				globalstuff.send_to_char(ch,"That character has nothing to teach you.")
				return
			globalstuff.send_to_char(ch,"%s can teach you the following skills/spells." % target.name)
			for skill in target.skills:
				if skills.get_skill_by_name(skill[0]).classtype == ch.charclass:
					globalstuff.send_to_char(ch,skill[0])
			return
	if args.find(" from ") != -1 and len(args.split(" from ",1)) > 1:
		skillname = args.lower().split(" from ",1)[0]
		targetname = args.lower().split(" from ",1)[1]

		target = globalstuff.get_char_by_name(ch.inroom,targetname)
		if target == None:
			globalstuff.send_to_char(ch,"There is no one here by that name to learn from.")
			return
		if "skillteacher" not in target.flags or target.skills == None:
			globalstuff.send_to_char(ch, "That character does not teach any skills.")
			return

		if target.skills != []:
			for skill in target.skills:
				if skillname.strip() == skill[0]:
					if ch.skillpoints > 0:
						for chskill in ch.skills:							
							if skill[0] == chskill[0]:
								globalstuff.send_to_char(ch,"You already know that skill.")
								return
						if skills.get_skill_by_name(skillname.strip()).classtype != ch.charclass:
							globalstuff.send_to_char(ch,"Your class cannot learn that.")
							return
						ch.skills.append([skillname.strip(),ch.getintellect()*2])
						globalstuff.send_to_char(ch,"You learn %s from %s. Now you need to practice it!" % (skillname.strip(),target.name))
						ch.skillpoints -= 1
						return
					else:
						globalstuff.send_to_char(ch,"You don't have any skill points!")
						return
			globalstuff.send_to_char(ch,"They can't teach you that.")
			return
		else:
			globalstuff.send_to_char(ch,"They don't have any skills to teach you.")
			return
	else:
		globalstuff.send_to_char(ch,"Learn what from who?")

def CMD_ask(ch,args):
	if args == "" or args.find(' ') == -1 or len(args.split()) < 2 or args.lower().find(" about " ) == -1:
		globalstuff.send_to_char(ch,"Ask what to whom?")
		return
	targetname = args.lower().split(" about ",1)[0].strip().lower()
	subject = args.lower().split(" about ",1)[1].strip().lower()
	target = globalstuff.get_char_by_name(ch.inroom,targetname)
	if target == None:
		globalstuff.send_to_char(ch,"You don't see anyone by that name here.")
		return
	if len(target.npc.factoids) > 0:
		for factoid in target.npc.factoids:
			if factoid.name.lower() == subject.lower():
				globalstuff.send_to_char(ch,"Follow carefully:")
				globalstuff.send_to_char(ch,factoid.name)
				globalstuff.send_to_char(ch,factoid.details)
				return
			if factoid.name.lower() in subject.lower():
				globalstuff.send_to_char(ch,"Follow carefully:")
				globalstuff.send_to_char(ch,factoid.name)
				globalstuff.send_to_char(ch,factoid.details)
				return
			if subject.find(' ') != -1 and len(subject) > 0:
				words = subject.lower().strip().split()
			else:
				words = [subject.lower().strip()]
			words = globalstuff.strip_generic_words(words)
			if all(word in factoid.keywords for word in words):
				globalstuff.send_to_char(ch,"Follow carefully:")
				globalstuff.send_to_char(ch,factoid.name)
				globalstuff.send_to_char(ch,factoid.details)
				return
	for quest in ch.questlist:
		if quest in target.questlist:
			if subject.find(' ') != -1:
				words = subject.lower().strip().split()
			else:
				words = [subject.lower().strip()]
			words = globalstuff.strip_generic_words(words)
			if all( word in quest.questkeywords for word in words):
				if quest.questcount < 1:
					globalstuff.send_to_char(ch,quest.rewardmessage)
					ch.questlist.remove(quest)
					target.questlist.remove(quest)
					ch.experience += quest.experience
					ch.honor += quest.honor
					ch.money += quest.silver
					globalstuff.send_to_char(ch,"You earn %d silver, %d experience, and %d honor for completing this quest." % (quest.silver,quest.experience,quest.honor)) 
					ch.checklevelup()
					return
				else:
					globalstuff.send_to_char("You have not completed that quest, come back when you have.")
					return
	for quest in ch.questlist:
		if quest in target.questlist:
			if subject.find(' ') != -1:
				words = subject.lower().strip().split()
			else:
				words = [subject.lower().strip()]
			words = globalstuff.strip_generic_words(words)
			if any( word in quest.questkeywords for word in words):
				if quest.questcount < 1:
					globalstuff.send_to_char(ch,quest.rewardmessage)
					ch.questlist.remove(quest)
					target.questlist.remove(quest)
					ch.experience += quest.experience
					ch.honor += quest.honor
					ch.money += quest.silver
					globalstuff.send_to_char(ch,"You earn %d silver, %d experience, and %d honor for completing this quest." % (quest.silver,quest.experience,quest.honor)) 
					ch.checklevelup()
					ch.showprompt()
					return
				else:
					globalstuff.send_to_char("You have not completed that quest, come back when you have.")
					return
	for quest in target.questlist:
		if quest not in ch.questlist:
			if subject.find(' ') != -1:
				words = subject.lower().strip().split()
			else:
				words = [subject.lower().strip()]
			words = globalstuff.strip_generic_words(words)
			if all(word in quest.questkeywords for word in words):
				while True:
					globalstuff.send_to_char(ch,quest.questmessage)
					answer = input("Will you help? ")
					if answer.lower() == "n" or answer.lower() == "no":
						globalstuff.send_to_char(ch,"%s says 'Very well, if you change your mind please do speak to me again" % quest.questgiver.name)
						return
					elif answer.lower() == "y" or answer.lower() == "yes":
						ch.questlist.append(quest)
						globalstuff.send_to_char(ch,"You accept the quest, onwards now!")
						return
	if len(target.npc.factoids) > 0:
		if subject.find(' ') != -1:
			words = subject.lower().strip().split()
		else:
			words = [subject.lower().strip()]
		words = globalstuff.strip_generic_words(words)
		for factoid in target.npc.factoids:
			if any(word in factoid.keywords for word in words):
				globalstuff.send_to_char(ch,"Follow carefully:")
				globalstuff.send_to_char(ch,factoid.name)
				globalstuff.send_to_char(ch,factoid.details)
				return
	globalstuff.send_to_char(ch,"%s does not understand your question." % target.name)

def CMD_talk(ch,args):
	if len(ch.inroom.charsinroom) < 2:
		globalstuff.send_to_char(ch,"There's no one here to talk to.")
		return
	if args.find(' ') != -1:
		if args.split()[0].lower() == "to":
			if args.find(' about ') != -1:
				targetname = args.split(' ',1)[1].strip().split(" about ",1)[0]
				if len(args.split(' ',1)[1].strip().split(" about ",1)) > 1:
					subject = args.split(' ',1)[1].strip().split(" about ",1)[1]
				else:
					globalstuff.send_to_char(ch, "Talk to them about what?")
					return
				target = globalstuff.get_char_by_name(ch.inroom,targetname)
			else:
				targetname = args.split(' ',1)[1]
				subject = None
				target = globalstuff.get_char_by_name(ch.inroom,targetname)
			if target == None:
				globalstuff.send_to_char(ch,"There is no one here by that name.")
				return
			if target == ch:
				globalstuff.send_to_char(ch,"You talk to yourself.")
				return
			if subject == None and target.npc != None and target.npc.metplayer == False:
				globalstuff.send_to_room(ch.inroom,target.npc.introduction)
				target.npc.metplayer = True
				return
				# add some if check here to focus on which quest they are asking about
			if target.questlist != []:
				for quest in target.questlist:
					if subject != None:
						if len(subject.split()) > 1:
							words = subject.strip().split()
						elif len(subject) > 0:
							words = [subject.strip()]
						else:
							print("no subject")
						words = globalstuff.strip_generic_words(words)
					else:
						words = []
					if all(word.lower() in quest.questkeywords for word in words):
						if quest in ch.questlist:
							if quest.questcount < 1:
								globalstuff.send_to_char(ch,quest.rewardmessage)
								ch.questlist.remove(quest)
								target.questlist.remove(quest)
								ch.experience += quest.experience
								ch.honor += quest.honor
								ch.money += quest.silver
								globalstuff.send_to_char(ch,"You earn %d silver, %d experience, and %d honor for completing this quest." % (quest.silver,quest.experience,quest.honor)) 
								ch.checklevelup()
								return
							else:
								globalstuff.send_to_char(ch, "You have not completed this quest yet, please return when you have.")
								return
						else:
							globalstuff.send_to_char(ch, "this NPC has quests for you.")
						if quest.queststarted == False:
							globalstuff.send_to_char(ch,quest.questmessage)
							while True:
								answer = input("Will you help? ")
								if answer.lower() == "n" or answer.lower() == "no":
									globalstuff.send_to_char(ch,"%s says 'Very well, if you change your mind please do speak to me again" % quest.questgiver.name)
									return
								elif answer.lower() == "y" or answer.lower() == "yes":
									ch.questlist.append(quest)
									globalstuff.send_to_char(ch,"You accept the quest, onwards now!")
									return
								else:
									globalstuff.send_to_char(ch,"Yes, or No?")
									continue
					if target.questlist != []:
						for item in target.questlist:
							if item not in ch.questlist:
								globalstuff.send_to_char(ch,item.questmessage)
								answer = input("Will you help? ")
								if answer.lower() == "n" or answer.lower() == "no":
									globalstuff.send_to_char(ch,"%s says 'Very well, if you change your mind please do speak to me again" % quest.questgiver.name)
									return
								elif answer.lower() == "y" or answer.lower() == "yes":
									ch.questlist.append(item)
									globalstuff.send_to_char(ch,"You accept the quest, onwards now!")
									return
					else:
						#insert text to show quests available, and other information the npc can tell
						globalstuff.send_to_char(ch,"Show available quests and conversations here.")
						return
				else:
					target.npc.process_text("%s says '%s' to you." % (ch.name,args.split(' ',1)[1]))
			else:
				if target == None:
					globalstuff.send_to_char(ch,"There is no one here by that name to talk to.")
					return
				if subject == None:
					if target.questlist != []:
						for x in range(len(target.questlist)):
							if target.questlist[x] not in ch.questlist:
								globalstuff.send_to_char(ch,target.questlist[x].questmessage)
								while True:
									answer = input("Will you help? ")
									if answer.lower() == "n" or answer.lower() == "no":
										globalstuff.send_to_char(ch,"%s says 'Very well, if you change your mind please do speak to me again" % quest.questgiver.name)
										return
									elif answer.lower() == "y" or answer.lower() == "yes":
										ch.questlist.append(target.questlist[x])
										globalstuff.send_to_char(ch,"You accept the quest, onwards now!")
										return
									else:
										globalstuff.send_to_char(ch,"Yes, or No?")
										continue
							else:
								glbobalstuff,send_to_char(ch,target.questlist[x].questmessage)
								return
						else:
							globalstuff.send_to_char(ch,"They have nothing to tell you.")
							return
				else:
					if len(target.npc.factoids) > 0:
						if subject.find(' ') != -1:
							words = subject.lower().strip().split()
						else:
							words = [subject.lower().strip()]
						words = globalstuff.strip_generic_words(words)
						for factoid in target.npc.factoids:
							if subject in factoid.keywords:
								globalstuff.send_to_char(ch,factoid.details)
								return
							if all(word in factoid.keywords for word in words):
								globalstuff.send_to_char(ch,factoid.details)
								return
						for factoid in target.npc.factoids:
							if any(word in factoid.keywords for word in words):
								globalstuff.send_to_char(ch,factoid.details)
								return
			globalstuff.send_to_char(ch,"Greetings friend, how may I be of assistance?")
		else:
			globalstuff.send_to_char(ch,"You need specify who you want to talk to.")
	else:
		globalstuff.send_to_char(ch,"Talk to who about what?")

def CMD_say(ch,args):
	if args == "":
		globalstuff.send_to_char(ch,"say what?")
	else:
		globalstuff.send_from_char(ch,"%s says '%s'." %(ch.name,args.strip()))
		globalstuff.send_to_char(ch,"You say '%s'." % args.strip())

def CMD_buy(ch,args):
	if ch.inroom.store == None:
		globalstuff.send_to_char(ch,"You are not in a store.")
		return
	container = globalstuff.get_obj_by_name_room(ch.inroom,"shelves")
	item = globalstuff.get_obj_by_name_container(container,args)
	if item == None:
		globalstuff.send_to_char(ch,"There is no item in this store by that name.")
		return
	else:
		if ch.get_weight() + item.weight > ch.maxweight():
			globalstuff.send_to_char(ch,"You cannot carry any more.")
		else:
			container.contents.remove(item)
			ch.inventory.append(item)
			ch.inroom.store.playerbalance += item.value
			ch.inroom.store.playertook.append(item)
			globalstuff.send_to_char(ch,"You take %s off the shelf. Your balance owing at this store is %d." % (item.name,ch.inroom.store.playerbalance))
			if ch.npc == None:
				while True:
					paynow = input("Would you like to pay now for your purchase?\notherwise you may continue browsing the shop [y/n]:")
					if paynow.strip().lower() == "yes" or paynow.strip().lower() == "y":
						CMD_pay(ch,"")
						break
					elif paynow.strip().lower() == "no" or paynow.strip().lower() == "n":
						globalstuff.send_to_char(ch,"Ok, feel free to keep shopping, but don't forget to 'pay'.")
						break
					else:
						globalstuff.send_to_char(ch,"Yes or No?")
						continue

def CMD_balance(ch,args):
	globalstuff.send_to_char(ch,"You have %d silver coins." % ch.money)
	if ch.inroom.store != None:
		globalstuff.send_to_char(ch,"You owe %d silver to the store you are in." % ch.inroom.store.playerbalance)

def CMD_negotiate(ch,args):
	#this command should alter the playerbalance of the store object based on charisma ratio between them and the merchant they negotiate with - should only be able to negotiate once on an item
	pass

def CMD_sell(ch,args):
# TODO add 'sell to <shopkeeper>'
	if ch.inroom.store == None:
		send_to_char(ch,"You are not in a store.")
		return
	if ch.inroom.store.npclist == []:
		globalstuff.send_to_char(ch,"There is no shopkeeper to sell your item to.")
		return
	item = globalstuff.get_obj_by_name_inv(ch,args)
	if item == None:
		globalstuff.send_to_char(ch,"You don't have that item to sell.")
		return
	if item.type in ch.inroom.store.itemtypes:
		if ch.inroom.store.money > item.value:
			ch.inroom.store.money -= item.value
			container = globalstuff.get_obj_by_name_room(ch.inroom,"shelves")
			ch.inventory.remove(item)
			container.contents.append(item)
			ch.money += item.value
			ch.inroom.store.money -= item.value
			globalstuff.send_to_char(ch,"You sell %s for %d. %s puts it on to the shelves for display." % (item.name,item.value,ch.inroom.store.npclist[0].character.name))
			return
		else:
			globalstuff.send_to_char(ch,"The store can't afford to buy this item from you.")
			return
	else:
		 globalstuff.send_to_char(ch, "This store is not interested in this type of item.")

def CMD_pay(ch,args):
	if ch.inroom.store != None:
		if ch.inroom.store.playerbalance > ch.money:
			globalstuff.send_to_char(ch, "You don't have enough money for the items you have chosen.\nPerhaps you should put some back.")
			return
		elif ch.inroom.store.playertook == []:
			globalstuff.send_to_char(ch,"You don't have any purchases to pay for.")
			return
		else:
			ch.money -= ch.inroom.store.playerbalance
			globalstuff.send_to_char(ch,"You pay %d to the shopkeeper." % ch.inroom.store.playerbalance )
			ch.inroom.store.playerbalance = 0
			ch.inroom.store.playertook = []
	else:
		globalstuff.send_to_char(ch,"You are not in a store.")
		return

def CMD_remove(ch,args):
	objtypes = globalstuff.ObjTypes()
	if args.find(' ') != -1:
		words = args.split()
	else:
		words = args
	for item in ch.equipment:
		if item != None:
			if item.name.lower() == args.lower() or args.lower() in item.name.lower() or all(word.lower() in item.name.lower() for word in words):
				ch.inventory.append(item)
				globalstuff.send_to_char(ch, "You remove %s." % item.name)
				if item.mana != 0:
					ch.mana -= item.mana
				if item.hp != 0:
					ch.hp -= item.hp
					if ch.hp < 1:
						ch.hp = 1
				if item.type == objtypes.OBJ_CHEST:
					ch.equipment[objtypes.OBJ_CHEST] = None
				elif item.type == objtypes.OBJ_HEAD:
					ch.equipment[objtypes.OBJ_HEAD] = None
				elif item.type == objtypes.OBJ_LEGS:
					ch.equipment[objtypes.OBJ_LEGS] = None
				elif item.type == objtypes.OBJ_WRIST:
					ch.equipment[objtypes.OBJ_WRIST] = None
				elif item.type == objtypes.OBJ_WEAPON:
					ch.equipment[objtypes.OBJ_WEAPON] = None				
				return
	globalstuff.send_to_char(ch, "You do not have an item equiped by that name.")

def CMD_enter(ch,args):
	if ch.inroom == None:
		globalstuff.send_to_char(ch, "There is no entrance here, you are already in a dungeon.")
		return
	elif ch.inroom.dungeonentrance != None:
		globalstuff.send_to_char(ch, "You descend into the dungeon.")
		ch.inroom.charsinroom.remove(ch)
		ch.dungeon = ch.inroom.dungeonentrance.dungeon
		ch.dungeonloc = ch.dungeon.start
		ch.inroom = None
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.append(ch)
		CMD_look(ch, "")
	else:
		globalstuff.send_to_char(ch, "There is no entrances here")

def CMD_drop(ch, args):
	if args == "":
		globalstuff.send_to_char("Drop what?")
		return
	item = globalstuff.get_obj_by_name_inv(ch,args)
	if item == None:
		globalstuff.send_to_char(ch, "You don't have an item by that name.")
		return
	if ch.inroom.store != None and item in ch.inroom.store.playertook:
		globalstuff.send_to_char(ch,"You can't leave items in a store. If you wish to return an item,\nput it back, or give it back to a storekeeper.")
		return
	elif ch.inroom.store != None:
		globalstuff.send_to_char(ch,"You can't drop items in a store, have some manners!")
		return
		
	if args.find(' ') == -1:
		words = args
	else:
		words = args.split()
	if item.name.lower() == args.lower() or args.lower() in item.name.lower() or all(word.lower() in item.name.lower() for word in words):
		ch.inroom.contents.append(item)
		ch.inventory.remove(item)
		globalstuff.send_to_char(ch, "You drop %s.." % item.name )

def CMD_boost(ch,args):
	if ch.statpoints < 1:
		globalstuff.send_to_char(ch,"You don't have enough stat points.")
	elif args.strip().lower() == "strength":
		ch.strength += 1
		ch.statpoints -= 1
		globalstuff.send_to_char(ch,"You have increased your strength by 1, spending 1 stat point.")
	elif args.strip().lower() == "charisma":
		ch.charisma += 1
		ch.statpoints -= 1
		globalstuff.send_to_char(ch,"You have increased your charisma by 1, spending 1 stat point.")
	elif args.strip().lower() == "intellect":
		ch.intellect += 1
		ch.statpoints -= 1
		globalstuff.send_to_char(ch,"You have increased your intellect by 1, spending 1 stat point.")
	else:
		globalstuff.send_to_char(ch,"Arguments: strength, charisma, intellect. Spends 1 stat point to increase your chosen stat.")

def CMD_score(ch, args):
	globalstuff.send_to_char(ch, "Name:        %s" % ch.name)
	globalstuff.send_to_char(ch, "Level:       %d" % ch.level)
	globalstuff.send_to_char(ch, "Experience:  %d" % ch.experience)
	globalstuff.send_to_char(ch, "Next level:  %d" % ch.getnextlevelexp())
	globalstuff.send_to_char(ch, "Strength:    %d (%d)" % (ch.strength, ch.getstrength()))
	globalstuff.send_to_char(ch, "Intellect:   %d (%d)" % (ch.intellect, ch.getintellect()))
	globalstuff.send_to_char(ch, "Charisma:    %d (%d)" % (ch.charisma, ch.getcharisma()))
	globalstuff.send_to_char(ch, "HP:          %d (%d)" % (ch.hp,ch.max_hp()))
	globalstuff.send_to_char(ch, "MANA:        %d (%d)" % (ch.mana,ch.max_mana()))
	globalstuff.send_to_char(ch, "HONOR:       %d" % ch.honor)
	globalstuff.send_to_char(ch, "Stat Points: %d" % ch.statpoints)
	globalstuff.send_to_char(ch, "Skill Points:%d" % ch.skillpoints)
	globalstuff.send_to_char(ch, "Silver coins %d" % ch.money)

def CMD_give(ch, args):
	if args.find(" back to ") != -1:
		itemname = args.split(" back to ",1)[0]
		targetname = args.split(" back to ",1)[1]
		item = globalstuff.get_obj_by_name_inv(ch, itemname.lower().strip())
		if item == None:
			globalstuff.send_to_char(ch,"You don't have an item called %s." % itemname)
			return
		target = globalstuff.get_char_by_name(ch.inroom,targetname.lower().strip())
		if target == None:
			globalstuff.send_to_char(ch,"You don't see anyone by that name here.")
		if ch.inroom.store != None and item in ch.inroom.store.playertook:
			ch.inventory.remove(item)
			target.inventory.append(item)
			ch.inroom.store.playertook.remove(item)
			ch.inroom.store.playerbalance -= item.value
			globalstuff.send_to_char(ch,"You give back %s to %s, your balance owing has been adjusted." % (item.name,target.name))
			container = globalstuff.get_obj_by_name_room(ch.inroom,"shelves")
			if container == None:
				print("Error, shelves container not found in shop, aborting.")
				exit(1)
			target.inventory.remove(item)
			container.contents.append(item)
			globalstuff.send_to_room(ch.inroom,"%s puts away %s on the shelves." %(item.name,target.name))
			return
	elif args.find(" to ") == -1:
		globalstuff.send_to_char(ch,"give what to who?")
		return
	else:
		split = args.strip.split(" to ", 1)
		item = get_obj_by_name_inv(ch,split[0].strip())
		if item == None:
			globalstuff.send_to_char(ch, "You don't have that item.")
		else:
			target = globalstuff.get_char_by_name(ch.inroom,split[1].strip())
			if target == None:
				globalstuff.send_to_char("There is no one here by that name.")
				return
			ch.inventory.remove(item)
			target.inventory.append(item)
			globalstuff.send_to_char(ch, "You give %s to %s." % (item.name,target.name))
			globalstuff.send_to_char(target,"%s gives %s to you." % (item.name,target.name))
			if ch.inroom.store != None and target in ch.inroom.store.npclist:
				target.inventory.remove(item)
				container = get_obj_by_name_room(ch.inroom,"shelves")
				container.contents.append(item)
				globalstuff.send_to_char(ch,"%s offers words of thanks and puts %s on the store shelves."% target.name, item.name)
				ch.honor += 1

def CMD_skills(ch, args):
	if ch.skills == []:
		globalstuff.send_to_char(ch,"You don't know any skills or spells.")
		return
	globalstuff.send_to_char(ch,"You know the following skills/spells:")
	for skill in ch.skills:
		globalstuff.send_to_char(ch, skill[0] + ": %d%%" % skill[1])

def CMD_put(ch, args):
	objtypes = globalstuff.ObjTypes()
	if args.find(' ') != -1 and args.split()[0] == "back":
		if ch.inroom.store == None:
			globalstuff.send_to_char(ch,"You are not in a store.")
			return
		item = globalstuff.get_obj_by_name_inv(ch,args.split(' ',1)[1])
		if item == None:
			globalstuff.send_to_char(ch,"You don't have an item by that name in your inventory.")
			return
		if item in ch.inroom.store.playertook:
			ch.inventory.remove(item)
			container = objects.get_obj_by_name_room(ch.inroom,"shelves")
			container.contents.append(item)
			ch.inroom.store.playerbalance -= item.value
			ch.inroom.store.playertook.remove(item)
			globalstuff.send_to_char(ch, "You put %s into %s, your balance at this store is now %d. " % (item.name, container.name, ch.inroom.store.playerbalance))
			return
		else:
			globalstuff.send_to_char(ch,'You didn\'t get that here.')
			return
	elif args.find(" in ") != -1 and len(args.split(" in ", 1)) > 1:
		itemname = args.split( " in ", 1)[0]
		containername = args.split( " in ", 1)[1]
		targetitem = None
		targetcontainer = None
		targetitem = globalstuff.get_obj_by_name_inv(ch, itemname.lower())
	if targetitem == None:
		globalstuff.send_to_char(ch,"You don't have an item called %s" % itemname)
		return
	targetcontainer = globalstuff.get_obj_by_name_inv(ch, itemname.lower())
	if targetcontainer == None:
		targetcontainer = globalstuff.get_obj_by_name_room(ch.inroom,containername)
		if targetcontainer == None:
			globalstuff.send_to_char(ch,"You don't see a container called %s." % containername)
		return
	if "noputin" in targetcontainer.flaglist:
		globalstuff.send_to_char(ch, "You cannot put things into %s." % targetcontainer.name)
		return
	if targetcontainer.type != objtypes.OBJ_CONTAINER:
		globalstuff.send_to_char( ch, "You can't put things in %s." % targetcontainer.name )
		return
	elif len(args.lower) == 0:
		globalstuff.send_to_char(ch,"put what in what?")
		return
	elif args.lower.find("in") == -1 and args.lower.find("back") == -1:
		globalstuff.send_to_char(ch,"Put what in what?")
		return
	else:
		ch.inventory.remove(targetitem)
		targetcontainer.contents.append(targetitem)
		globalstuff.send_to_char(ch, "You put %s into %s." % (targetitem.name, targetcontainer.name))

def CMD_loot(ch, args):
	if args == "":
		globalstuff.send_to_char(ch,"Loot what?")
		return
	if ch.inroom.store != None and ch.inroom.store.npclist != []:
		globalstuff.send_to_char(ch,"You can't loot store shelves and containers while the\nshop keepers are watching.")
		return
	objtypes = globalstuff.ObjTypes()

	gotitems = False
	container = globalstuff.get_obj_by_name_room(ch.inroom,args)
	if container != None:
		if "hidden" in container.flaglist and container not in ch.foundhidden:
			globalstuff.send_to_char(ch,"Nothing found by that name to loot.")
			return
		if container.type == objtypes.OBJ_CONTAINER:
			if len(container.contents) > 0:
				for item in container.contents:
					if ch.get_weight() + item.weight > ch.maxweight():
						globalstuff.send_to_char(ch,"You cannot carry anymore")
						return
					else:
						globalstuff.send_to_char(ch, "You get %s from %s." % (item.name, container.name))
						ch.inventory.append(item)
						container.contents.remove(item)
						gotitems = True
			if gotitems == False:
				globalstuff.send_to_char(ch, "There is no items to loot in %s." % container.name)
				return
		else:
			globalstuff.send_to_char(ch, "%s is not lootable." % container.name)
			return
	else:
		globalstuff.send_to_char(ch,"Nothing found by the name to loot.")

def CMD_get(ch, args):
	objtypes = globalstuff.ObjTypes()
	if args.find( " from " ) != -1 and len(args.split(" from ", 1)) > 1:
		itemname = args.split(" from ",1)[0]
		containername = args.split(" from ",1)[1]
		container = globalstuff.get_obj_by_name_room(ch.inroom,containername.lower())
		if container == None:
			container = globalstuff.get_obj_by_name_inv(ch,containername.lower())
			if container == None:
				globalstuff.send_to_char(ch,"You can't find that container.")
				return
			if "hidden" not in container.flags or container in ch.foundhidden:
				globalstuff.send_to_char( ch, "You can't find that container" )
				return

		if container.type != objtypes.OBJ_CONTAINER:
			globalstuff.send_to_char(ch,"You get things from that.")
			return
		item = globalstuff.get_obj_by_name_container(container, itemname.lower())
		if item == None:
			globalstuff.send_to_char(ch,"There is nothing in %s by that name." % container.name)
			return
		if ch.get_weight() + item.weight < ch.maxweight():
			container.contents.remove(item)
			ch.inventory.append(item)
			globalstuff.send_to_char(ch, "you get %s from %s." % (item.name,container.name))
			if ch.inroom.store != None and container in ch.inroom.contents:
				if ch.inroom.store.npclist != []:
					globalstuff.send_to_char(ch,"%d has been added to your balance owing." % item.value)
					ch.inroom.store.playerbalance += item.value
					ch.inroom.store.playertook.append(item)
				elif ch.inroom.store.playerdishonored == False:
					ch.honor -= 1
					globalstuff.send_to_char(ch,"you steal %s from the store. You lose 1 honor." % item.name)
					ch.inroom.store.playerdishonored = True
				else:
					globalstuff.send_to_char(ch,"you steal %s from the store." % item.name)
		else:
			globalstuff.send_to_char(ch,"You cannot carry any more weight.")
		return
	else:
		item = globalstuff.get_obj_by_name_room(ch.inroom,args)
		if item == None:
			globalstuff.send_to_char(ch,"There is no object by that name here.")
			return
		if "hidden" in item.flaglist and item not in ch.foundhidden:
			globalstuff.send_to_char( ch, "There is no object by that name here." )
			return
		if "nopickup" in item.flaglist:
			globalstuff.send_to_char(ch,"You can't pick that up.")
			return
		if ch.get_weight() + item.weight < ch.maxweight():
			ch.inroom.contents.remove(item)
			ch.inventory.append(item)
			globalstuff.send_to_char(ch,"You pick up %s." % item.name)
		else:
			globalstuff.send_to_char(ch,"You cannot carry any more weight.")

def CMD_cast(ch, args):
	args = args.strip()
	if args == "" and ch.fightingtarget != None:
		args = ch.fightingtarget.name
	if args == "":	
		globalstuff.send_to_char(ch, "Cast what?")
		return
	if args.find(' ') != -1 and args.split()[0] == "a":
		args = args.split(' ',1)[1]
	if args.find(' at ') != -1:
		args = args.split(' at ',1)[0] + " " + args.split(' at ',1)[1]
	if args.count(' ') > 0:
		spellname = args.split(' ', 1)[0]
		targetname = args.split(' ', 1)[1]
	else:
		spellname = args
		if ch.fightingtarget == None:
			targetname = ""
		else:
			targetname = ch.fightingtarget.name
	knowsspell = False
	spelllevel = 0
	for spell in ch.skills:
		if spell[0] == spellname.strip().lower():
			spelllevel = spell[1]
			knowsspell = True
	if knowsspell == False:
		globalstuff.send_to_char(ch,"You don't know any spell by that name.")
		return
	for spell in globalstuff.skilllist:
		if spell.type.lower() == "spell" and ch.charclass == spell.classtype and spell.name == spellname:
			if targetname != "":
				if globalstuff.get_char_by_name(ch.inroom, targetname.lower()) != None:
					for cooldown in ch.cooldowns:
						if cooldown.name == spell.name:
							globalstuff.send_to_char(ch,"You must wait %d seconds between casting this spell." % spell.cooldown)
							return
					if spelllevel < 100:
						success = random.randrange(1,101)
						if success < spelllevel:
							ch.cooldowns.append(globalstuff.CooldownTimer(spell.cooldown,spell.name))
							globalstuff.send_to_char(ch,"You fail to cast %s, perhaps you need more practice." % skill.name)
							return
						for spell2 in ch.skills:
							if spell2[0] == spellname.strip().lower():
								globalstuff.send_to_char(ch,"You succeed in casting the spell, your skill rating has been improved.")
								spelllevel = spell2[1]+1
					retvals = spell.callskill(ch.gamestate.playerchar, targetname)
					ch.cooldowns.append(globalstuff.CooldownTimer(retvals[1],retvals[0]))
					return
				else: 
					globalstuff.send_to_char(ch, "No target found by that name.")
					return
			else:
				globalstuff.send_to_char(ch,"You need to choose a target.")
				return
	globalstuff.send_to_char(ch,"You don't know any spell by that name.")

def CMD_commands(ch, args):
	globalstuff.send_to_char(ch, "The available commands are:")
	for command in globalstuff.commandlist:
		globalstuff.send_to_char(ch, command.name)
	globalstuff.send_to_char(ch, "You may read about each command by typing 'help <command>'.\nTo learn about command shortcuts, use the command 'alias'.\nMany commands have a shorter alias you can use instead.")

def CMD_alias(ch,args):
	globalstuff.send_to_char(ch,"The following alias commands are avalable:")
	for alias, values in globalstuff.commandaliasdict.items():
		globalstuff.send_to_char(ch, alias + ": " + values[0])
	globalstuff.send_to_char(ch, "To use an alias, simply replace the command you would norally\ntype with it's alias, followed by it's normal arguments if there is any.")

def CMD_equipment(ch,args):
	objtypes = globalstuff.ObjTypes()
	if ch.equipment == [None,None,None,None,None]:
		globalstuff.send_to_char(ch, "You are not using any items.")
		return
	globalstuff.send_to_char( ch, "You are using the following:" )
	if ch.equipment[objtypes.OBJ_CHEST] != None:
		globalstuff.send_to_char( ch, "Chest: " + ch.equipment[objtypes.OBJ_CHEST].name)
	if ch.equipment[objtypes.OBJ_HEAD] != None:
		globalstuff.send_to_char( ch, "Head: " + ch.equipment[objtypes.OBJ_HEAD].name)
	if ch.equipment[objtypes.OBJ_LEGS] != None:
		globalstuff.send_to_char( ch, "Legs: " + ch.equipment[objtypes.OBJ_LEGS].name)
	if ch.equipment[objtypes.OBJ_WRIST] != None:
		globalstuff.send_to_char( ch, "Wrists: " + ch.equipment[objtypes.OBJ_WRIST].name)
	if ch.equipment[objtypes.OBJ_WEAPON] != None:
		globalstuff.send_to_char( ch, "Weapon: " + ch.equipment[objtypes.OBJ_WEAPON].name)

def CMD_sleep(ch,args):
	if ch.sleeping == True:
		globalstuff.send_to_char(ch,"You are already sleeping.")
	else:
		ch.sleeping = True
		globalstuff.send_to_char(ch,"You fall alseep.")
		globalstuff.send_to_room(ch.inroom,"%s falls asleep." % ch.name)

def CMD_wake(ch,args):
	if ch.sleeping == False:
		globalstuff.send_to_char(ch,"You are already awake.")
	else:
		globalstuff.send_to_room(ch.inroom,"%s rises from their slumber." % ch.name)
		ch.sleeping = False
		globalstuff.send_to_char(ch,"You awake from your slumber.")

def CMD_equip(ch,args):
		item = globalstuff.get_obj_by_name_inv(ch, args.lower().strip())
		if item == None:
			globalstuff.send_to_char(ch, "You don't have that item to equip.")
			return
		if item.type > 4:
			globalstuff.send_to_char(ch,"You can't equip %s." % item.name)
			return
		if ch.equipment[item.type] == None and item.type < 5:
			ch.equipment[item.type] = item
			globalstuff.send_to_char( ch, "You equip %s." % item.name )
			ch.inventory.remove(item)
			if item.hp != 0:
				ch.hp += item.hp
			if item.mana != 0:
				ch.mana += item.mana
			return
		else:
			globalstuff.send_to_char( ch, "You are already using an item in that slot, unequip it to use this item." )

def CMD_inventory(ch,args):
	if ch.inventory == []:
		globalstuff.send_to_char( ch, "You aren't carrying anything." )
	else:
		globalstuff.send_to_char( ch, "Items you are carrying:" )
		for item in ch.inventory:
			globalstuff.send_to_char( ch, item.name )

def CMD_north(ch,args):
	
	if ch.fightingtarget != None or ch.fightinglist != []:
		globalstuff.send_to_char(ch,"You cannot leave while fighting.")
		return
	if ch.dungeon != None:
		if ch.dungeonloc[1] == ch.dungeon.height:
			globalstuff.send_to_char(ch, "You cannot go that way.")
			return
		if ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]+1].roomtype == None:
			globalstuff.send_to_char(ch, "You cannot go that way.")
			return
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.remove(ch)
		ch.dungeonloc[1] += 1
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.append(ch)
		CMD_look(ch,"")
		return

	if ch.inroom.store != None and ch.inroom.store.playerbalance > 0 and ch.inroom.store.playerwarned == True and ch.inroom.store.npclist != []:
		if len(ch.inroom.store.npclist) > 0:
			if ch.fightinglist == [] and ch.fightingtarget == None:
				ch.begincombat(ch.inroom.store.npclist[0].character)
				globalstuff.send_to_char(ch, "%s shouts 'You won't get away with this!'" % ch.inroom.store.npclist[0].character.name)
			ch.honor -= 1
			ch.inroom.playerdishonored = True
			for npc in ch.inroom.store.npclist:
				if npc.character not in ch.fightinglist:
					ch.fightinglist.append(npc.character)
					npc.character.fightingtarget = ch
			return
	elif ch.inroom.store != None and ch.inroom.store.playerbalance > 0 and ch.inroom.store.npclist != []:
		globalstuff.send_to_char(ch,"%s stands in front of your path, blocking you from leaving." % ch.inroom.store.npclist[0].character.name)
		globalstuff.send_to_char(ch,"%s says 'Either pay for those times or put them back, otherwie there will be trouble" % ch.inroom.store.npclist[0].character.name)
		ch.inroom.store.playerwarned = True
		return
	if ch.inroom.exits[0] != None:
		if ch.inroom.store !=  None and ch.inroom.store.npclist == [] and ch.inroom.store.playerbalance > 0:
			ch.inroom.store.playerbalance = 0
			ch.honor -= 1
			globalstuff.send_to_char(ch,"You walk out without paying, leaving the corpses of the store\nworkers to rot. You lose 1 honor point")
		globalstuff.send_from_char(ch,"%s walks to the north." % ch.name)
		ch.inroom.charsinroom.remove(ch)
		ch.inroom = ch.inroom.exits[0]
		ch.inroom.charsinroom.append(ch)
		globalstuff.send_from_char(ch,"%s walks in from the south." % ch.name)
		CMD_look(ch,"")
		for character in ch.inroom.charsinroom:
			if ch in character.enemies:
				globalstuff.send_to_char(ch, "%s lunges at you and attacks, remembering your previous encounter." % character.name)
				ch.begincombat(character)
			elif "aggro" in character.flags:
				globalstuff.send_to_char(ch, "%s attacks you as immediately." % character.name)
				ch.begincombat(character)
	else:
		globalstuff.send_to_char( ch, "You cannot go that way" )

def CMD_east(ch,args):
	if ch.fightingtarget != None or ch.fightinglist != []:
		globalstuff.send_to_char(ch,"You cannot leave while fighting.")
		return
	if ch.dungeon != None:
		if ch.dungeonloc[0] == ch.dungeon.width:
			globalstuff.send_to_char(ch, "You cannot go that way.")
			return
		if ch.dungeon.matrix[ch.dungeonloc[0]+1][ch.dungeonloc[1]].roomtype == None:
			globalstuff.send_to_char(ch, "You cannot go that way.")
			return
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.remove(ch)
		ch.dungeonloc[0] += 1
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.append(ch)
		CMD_look(ch,"")
		return

	if ch.inroom.store != None and ch.inroom.store.playerbalance != 0 and ch.inroom.store.playerwarned == True and ch.inroom.store.npclist != []:
		if len(ch.inroom.store.npclist) > 0:
			if ch.fightinglist == [] and ch.fightingtarget == None:
				ch.begincombat(ch.inroom.store.npclist[0].character)
				globalstuff.send_to_char(ch, "%s shouts 'You won't get away with this!'" % ch.inroom.store.npclist[0].character.name)
			ch.inroom.playerdishonored = True
			ch.honor -= 1
			for npc in ch.inroom.store.npclist:
				if npc.character not in ch.fightinglist:
					ch.fightinglist.append(npc.character)
					npc.character.fightingtarget = ch
			return
	elif ch.inroom.store != None and ch.inroom.store.playerbalance != 0 and ch.inroom.store.npclist == []:
		globalstuff.send_to_char(ch,"%s stands in front of your path, blocking you from leaving." % ch.inroom.store.npclist[0].character.name)
		globalstuff.send_to_char(ch,"%s says 'Either pay for those times or put them back, otherwie there will be trouble" % ch.inroom.store.npclist[0].character.name)
		ch.inroom.store.playerwarned = True
		return
	if ch.inroom.exits[1] != None:
		if ch.inroom.store !=  None and ch.inroom.store.npclist == [] and ch.inroom.store.playerbalance > 0:
			ch.inroom.store.playerbalance = 0
			ch.honor -= 1
			globalstuff.send_to_char(ch,"You walk out without paying, leaving the corpses of the store\nworkers to rot. You lose 1 honor point")
		globalstuff.send_from_char(ch,"%s walks to the east." % ch.name)
		ch.inroom.charsinroom.remove(ch)
		ch.inroom = ch.inroom.exits[1]
		ch.inroom.charsinroom.append(ch)
		globalstuff.send_from_char(ch,"%s walks in from the west." % ch.name)
		CMD_look(ch,"")
		for character in ch.inroom.charsinroom:
			if ch in character.enemies:
				globalstuff.send_to_char(ch, "%s lunges at you and attacks, remembering your previous encounter." % character.name)
				ch.begincombat(character)
			if "aggro" in character.flags:
				globalstuff.send_to_char(ch, "%s attacks you as immediately." % character.name)
				ch.begincombat(character)
	else:
		globalstuff.send_to_char( ch, "You cannot go that way" )

def CMD_attack(ch, args):
	if args == "":
		globalstuff.send_to_char( ch, "attack what?" )
		return
	words = args.lower()
	if len(words.split()) > 1:
		words = words.split()
	else:
		words = args
	if ch.fightingtarget != None:
		if ch.fightingtarget.name.lower() == args.lower() or args.lower() in ch.fightingtarget.name.lower() or all(word in ch.fightingtarget.name.lower() for word in words):
			globalstuff.send_to_char( ch, "You are already fighting them" )
			return
		elif args.lower() == ch.name or args.lower() in ch.name.lower():
			globalstuff.send_to_char( ch, "You can't attack yourself!" )
			return
		elif args.lower == "none":
			ch.fightingtarget = None
			alreadycooldown = False
			for cooldown in ch.cooldowns:
				if cooldown.name == "attack":
					alreadycooldown = True
			if alreadycooldown == False:
				ch.cooldowns.append(CooldownTimer(3, "attack"))
			globalstuff.send_to_char( ch, "You stop targeting your opponent." )
			return

	character = globalstuff.get_char_by_name(ch.inroom, args)
	if character == None:
		globalstuff.send_to_char(ch, "You don't see a target by that name.")
		return
	if character.name.lower() == args.lower() or args in character.name.lower() or all(word in character.name.lower() for word in words):
		ch.fightingtarget = character
		if character not in ch.fightinglist:
			ch.fightinglist.append(character)
			globalstuff.send_to_char( ch, "You begin fighting %s." % character.name )
			ch.fightingtarget.fightingtarget = ch
		else:
			globalstuff.send_to_char( ch, "You switch your focus to %s." % character.name)
		if character.npc.store != None:
			for npc in ch.fightingtarget.npc.store.npclist:
				if npc.character != character and npc.character not in ch.fightinglist:
					npc.character.fightingtarget = ch
					ch.fightinglist.append(npc.character)
					globalstuff.send_to_char(ch,"%s enters the brawl in defence of the store." % npc.character.name)
		alreadycooldown = False
		for cooldown in ch.cooldowns:
			if cooldown.name == "attack":
				alreadycooldown = True
		if alreadycooldown == False:
			ch.attack()

def CMD_flee(ch,args):
	if ch.fightingtarget == None and ch.fightinglist == []:
		globalstuff.send_to_char(ch,"You are not in a fight")
		return
	if len(ch.fightinglist) > 3:
		globalstuff.send_to_char(ch,"You are fighting too many opponents to flee.")
		return
	fleeroll = random.randrange(1, 6) - len(ch.fightinglist)
	if fleeroll < 1:
		if len(ch.fightinglist) > 1:
			globalstuff.send_to_char(ch,"You fail to flee, and your opponents take advantage of your attempt.")
			for character in ch.fightinglist:
				character.attack()
			return
		else:
			ch.fightinglist[0].attack()
			globalstuff.send_to_char(ch,"You fail to flee, and your opponents take advantage of your attempt.")
			for character in ch.fightinglist:
				character.attack()
			return
	if args.lower().strip() == "north":
		if ch.inroom.exits[0] != None:
			for character in ch.fightinglist:
				character.fightingtarget = None
				character.enemies.append(ch)
			ch.fightingtarget = None
			ch.fightinglist = []
			globalstuff.send_to_char(ch,"You flee to the north! You have lost 1 honor point.")
			globalstuff.send_from_char(ch,"%s flees to the north!" % ch.name)
			ch.inroom.charsinroom.remove(ch)
			ch.inroom = ch.inroom.exits[0]
			ch.inroom.charsinroom.append(ch)
			globalstuff.send_from_char(ch,"%s arrived from the south, having fled a battle.")
			ch.honor -= 1
			CMD_look(ch,"")
			firstattacker = True
			for character in ch.inroom.charsinroom:
				if ch in character.enemies:
					if firstattacker == True:
						globalstuff.send_to_char(ch, "%s lunges at you, remembering your previous encounter." % character.name)
						firstattacker = False
					else:
						CMD_say(character,"You'll pay for your crime!")
					ch.begincombat(character)
				if "aggro" in character.flags:
					globalstuff.send_to_char(ch, "%s beings to attack you immediately." % character.name)
					ch.begincombat(character)
		else:
			globalstuff.send_to_char(ch,"You clumsily attempt to flee to the north, but cannot go that way!\nYour opponents seize the opportunity.")
			for character in ch.fightinglist:
				character.attack()
			return
	elif args.lower().strip() == "east":
		if ch.inroom.exits[1] != None:
			for character in ch.fightinglist:
				character.fightingtarget = None
				character.enemies.append(ch)
			ch.fightingtarget = None
			ch.fightinglist = []
			globalstuff.send_to_char(ch,"You flee to the east! You have lost 1 honor point.")
			globalstuff.send_from_char(ch,"%s flees to the east!" % ch.name)
			ch.inroom.charsinroom.remove(ch)
			ch.inroom = ch.inroom.exits[1]
			ch.inroom.charsinroom.append(ch)
			globalstuff.send_from_char(ch,"%s arrived from the west, having fled a battle.")
			ch.honor -= 1
			CMD_look(ch,"")
			for character in ch.inroom.charsinroom:
				if ch in character.enemies:
					globalstuff.send_to_char(ch, "%s lunges at you and attacks, remembering your previous encounter." % character.name)
					ch.begincombat(character)
				if "aggro" in character.flags:
					globalstuff.send_to_char(ch, "%s attacks you immediately." % character.name)
					ch.begincombat(character)
		else:
			globalstuff.send_to_char(ch,"You clumsily attempt to flee to the east, but cannot go that way!\nYour opponents seize the opportunity.")
			for character in ch.fightinglist:
				character.attack()
	elif args.lower().strip() == "south":
		if ch.inroom.exits[2] != None:
			for character in ch.fightinglist:
				character.fightingtarget = None
				character.enemies.append(ch)
			ch.fightingtarget = None
			ch.fightinglist = []
			globalstuff.send_to_char(ch,"You flee to the south! You have lost 1 honor point.")
			globalstuff.send_from_char(ch,"%s flees to the south!" % ch.name)
			ch.inroom.charsinroom.remove(ch)
			ch.inroom = ch.inroom.exits[2]
			ch.inroom.charsinroom.append(ch)
			globalstuff.send_from_char(ch,"%s arrived from the north, having fled a battle.")
			ch.honor -= 1
			CMD_look(ch,"")
			for character in ch.inroom.charsinroom:
				if ch in character.enemies:
					globalstuff.send_to_char(ch, "%s lunges at you and attacks, remembering your previous encounter." % character.name)
					ch.begincombat(character)
				if "aggro" in character.flags:
					globalstuff.send_to_char(ch, "%s attacks you as immediately." % character.name)
					ch.begincombat(character)
		else:
			globalstuff.send_to_char(ch,"You clumsily attempt to flee to the east, but cannot go that way!\nYour opponents seize the opportunity.")
			for character in ch.fightinglist:
				character.attack()
	elif args.lower().strip() == "west":
		if ch.inroom.exits[3] != None:
			for character in ch.fightinglist:
				character.fightingtarget = None
				character.enemies.append(ch)
			ch.fightingtarget = None
			ch.fightinglist = []
			globalstuff.send_to_char(ch,"You flee to the west! You have lost 1 honor point.")
			globalstuff.send_from_char(ch,"%s flees to the west!" % ch.name)
			ch.inroom.charsinroom.remove(ch)
			ch.inroom = ch.inroom.exits[3]
			ch.inroom.charsinroom.append(ch)
			globalstuff.send_from_char(ch,"%s arrived from the east, having fled a battle.")
			ch.honor -= 1
			CMD_look(ch,"")
			for character in ch.inroom.charsinroom:
				if ch in character.enemies:
					globalstuff.send_to_char(ch, "%s lunges at you and attacks, remembering your previous encounter." % character.name)
					ch.begincombat(character)
				if "aggro" in character.flags:
					globalstuff.send_to_char(ch, "%s attacks you as immediately." % character.name)
					ch.begincombat(character)
		else:
			globalstuff.send_to_char(ch,"You clumsily attempt to flee to the east, but cannot go that way!\nYour opponents seize the opportunity.")
			for character in ch.fightinglist:
				character.attack()
	elif args.strip() == "":
		while True:
			exit = random.randrange(4)
			if ch.inroom.exits[exit] != None:
				if exit == 0:
					CMD_flee(ch,"north")
					return
				elif exit == 1:
					CMD_flee(ch,"east")
					return
				elif exit == 2:
					CMD_flee(ch,"south")
					return
				elif exit == 3:
					CMD_flee(ch,"west")
					return
	else:
		globalstuff.send_to_char(ch,"Flee in which direction? (no arguments for any direction available)")
			
def CMD_south(ch,args):
	if ch.fightingtarget != None or ch.fightinglist != []:
		globalstuff.send_to_char(ch,"You cannot leave while fighting.")
		return
	if ch.dungeon != None:
		if ch.dungeonloc[1] == 0:
			globalstuff.send_to_char(ch, "You cannot go that way.")
			return
		if ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]-1].roomtype == None:
			globalstuff.send_to_char(ch, "You cannot go that way.")
			return
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.remove(ch)
		ch.dungeonloc[1] -= 1
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.append(ch)
		CMD_look(ch,"")
		return
	if ch.inroom.store != None and ch.inroom.store.playerbalance != 0 and ch.inroom.store.playerwarned == True and ch.inroom.store.npclist != []:
		if len(ch.inroom.store.npclist) > 0:
			ch.honor -= 1
			ch.inroom.playerdishonored = True
			if ch.fightinglist == [] and ch.fightingtarget == None:
				ch.begincombat(ch.inroom.store.npclist[0].character)
				globalstuff.send_to_char(ch, "%s shouts 'You won't get away with this!'" % ch.inroom.store.npclist[0].character.name)
			for npc in ch.inroom.store.npclist:
				if npc.character not in ch.fightinglist:
					ch.fightinglist.append(npc.character)
					npc.character.fightingtarget = ch
			return
	elif ch.inroom.store != None and ch.inroom.store.playerbalance != 0 and ch.inroom.store.npclist == []:
		globalstuff.send_to_char(ch,"%s stands in front of your path, blocking you from leaving." % ch.inroom.store.npclist[0].character.name)
		globalstuff.send_to_char(ch,"%s says 'Either pay for those times or put them back, otherwie there will be trouble" % ch.inroom.store.npclist[0].character.name)
		ch.inroom.store.playerwarned = True
		return

	if ch.inroom.exits[2] != None:
		if ch.inroom.store !=  None and ch.inroom.store.npclist == [] and ch.inroom.store.playerbalance > 0:
			ch.inroom.store.playerbalance = 0
			ch.honor -= 1
			globalstuff.send_to_char(ch,"You walk out without paying, leaving the corpses of the store\nworkers to rot. You lose 1 honor point")
			ch.inroom.playerdishonored = True
			globalstuff.send_from_char(ch,"%s walks to the south." % ch.name)
		ch.inroom.charsinroom.remove(ch)
		ch.inroom = ch.inroom.exits[2]
		ch.inroom.charsinroom.append(ch)
		globalstuff.send_from_char(ch,"%s walks in from the north." % ch.name)
		CMD_look(ch,"")
		for character in ch.inroom.charsinroom:
			if ch in character.enemies:
				globalstuff.send_to_char(ch, "%s lunges at you and attacks, remembering your previous encounter." % character.name)
				ch.begincombat(character)
			if "aggro" in character.flags:
				globalstuff.send_to_char(ch, "%s attacks you as immediately." % character.name)
				ch.begincombat(character)
	else:
		globalstuff.send_to_char( ch, "You cannot go that way" )

def CMD_west(ch,args):
	if ch.fightingtarget != None or ch.fightinglist != []:
		globalstuff.send_to_char(ch,"You cannot leave while fighting.")
		return
	if ch.dungeon != None:
		if ch.dungeonloc[0] == 0:
			globalstuff.send_to_char(ch, "You cannot go that way.")
			return
		if ch.dungeon.matrix[ch.dungeonloc[0]-1][ch.dungeonloc[1]].roomtype == None:
			globalstuff.send_to_char(ch, "You cannot go that way.")
			return
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.remove(ch)
		ch.dungeonloc[0] -= 1
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.append(ch)
		CMD_look(ch,"")
		return

	if ch.inroom.store != None and ch.inroom.store.playerbalance != 0 and ch.inroom.store.playerwarned == True and ch.inroom.store.npclist != []:
		if len(ch.inroom.store.npclist) > 0:
			ch.honor -= 1
			ch.inroom.playerdishonored = True
			if ch.fightinglist == [] and ch.fightingtarget == None:
				ch.begincombat(ch.inroom.store.npclist[0].character)
				globalstuff.send_to_char(ch, "%s shouts 'You won't get away with this!'" % ch.inroom.store.npclist[0].character.name)
			for npc in ch.inroom.store.npclist:
				if npc.character not in ch.fightinglist:
					ch.fightinglist.append(npc.character)
					npc.character.fightingtarget = ch
			return
	elif ch.inroom.store != None and ch.inroom.store.playerbalance != 0 and ch.inroom.store.npclist == []:
		globalstuff.send_to_char(ch,"%s stands in front of your path, blocking you from leaving." % ch.inroom.store.npclist[0].character.name)
		globalstuff.send_to_char(ch,"%s says 'Either pay for those times or put them back, otherwie there will be trouble" % ch.inroom.store.npclist[0].character.name)
		ch.inroom.store.playerwarned = True
		return
	if ch.inroom.exits[3] != None:
		if ch.inroom.store !=  None and ch.inroom.store.npclist == [] and ch.inroom.store.playerbalance > 0:
			ch.inroom.store.playerbalance = 0
			ch.honor -= 1
			globalstuff.send_to_char(ch,"You walk out without paying, leaving the corpses of the store\nworkers to rot. You lose 1 honor point")
		globalstuff.send_from_char(ch,"%s walks to the west." % ch.name)
		ch.inroom.charsinroom.remove(ch)
		ch.inroom = ch.inroom.exits[3]
		ch.inroom.charsinroom.append(ch)
		globalstuff.send_from_char(ch,"%s walks in from the east." % ch.name)
		CMD_look(ch,"")
		for character in ch.inroom.charsinroom:
			if ch in character.enemies:
				globalstuff.send_to_char(ch, "%s lunges at you and attacks, remembering your previous encounter." % character.name)
				ch.begincombat(character)
			elif "aggro" in character.flags:
				globalstuff.send_to_char(ch, "%s attacks you as immediately." % character.name)
				ch.begincombat(character)
	else:
		globalstuff.send_to_char( ch, "You cannot go that way" )

def CMD_help(ch,args):
	if args == "":
		globalstuff.send_to_char( ch, "This command will allow you look up other commands in the game. Syntax: 'help <command name>'.\nYou may view a list of commands by typing 'commands'." )
		return
	else:
		for command in globalstuff.commandlist:
			if args.lower() == command.name.lower():
				globalstuff.send_to_char( ch, command.helpinfo )
				return
		globalstuff.send_to_char( ch, "Command not found, use 'commands' to see a list of available commands." )


def CMD_leave(ch,args):
	if ch.dungeon == None:
		globalstuff.send_to_char( ch, "you are not in a dungeon")
	elif ch.dungeonloc[0] == ch.dungeon.start[0] and ch.dungeonloc[1] == ch.dungeon.start[1]:
		ch.dungeon.matrix[ch.dungeonloc[0]][ch.dungeonloc[1]].charsinroom.remove(ch)
		ch.dungeon.entrance.room.charsinroom.append(ch)
		ch.inroom = ch.dungeon.entrance.room
		ch.dungeon = None
		CMD_look(ch,"")
	else:
		globalstuff.send_to_char( ch, "You are not at a dungeon exit, look for a stairwell.")

def CMD_look(ch,args):
	objtypes = globalstuff.ObjTypes()
	if ch.dungeon != None:
		for y in range(ch.dungeonloc[1] + 15, ch.dungeonloc[1] - 15, -1):
			xstring = ""
			for x in range(ch.dungeonloc[0] - 15, ch.dungeonloc[0] + 15):
				if x < 0 or x > ch.dungeon.width or y < 0 or y > ch.dungeon.height:
					xstring = "%s#" % xstring
				elif ch.dungeonloc[0] == x and ch.dungeonloc[1] == y:
					xstring = "%sX" % xstring
				elif x == ch.dungeon.start[0] and y == ch.dungeon.start[1]:
					xstring = "%s@" % xstring
				elif x > 0 and x < ch.dungeon.width and y > 0 and y < ch.dungeon.height and ch.dungeon.matrix[x][y].roomtype != None:
					xstring = "%s " % xstring
				else:
					xstring = "%s#" % xstring
			globalstuff.send_to_char(ch,xstring)
		return
			
	if args.lower() != "" and args.lower().split()[0] == "in" and args.find(' ') != -1:
		container = globalstuff.get_obj_by_name_inv(ch, args.lower().split(' ', 1)[1])
		if container == None:
			container = globalstuff.get_obj_by_name_room(ch.inroom,args.lower().split(' ', 1)[1])
			if container == None:
				globalstuff.send_to_char(ch,"There is nothing by that name to look in.")
				return
		if container.type == objtypes.OBJ_CONTAINER:
			globalstuff.send_to_char(ch, "That container contains:")
			if container.contents == []:
				globalstuff.send_to_char(ch,"Nothing")
			else:
				for content in container.contents:
					if ch.inroom.store != None:
						globalstuff.send_to_char(ch, "<%d silver> %s "%( content.value,content.name))
					else:
						globalstuff.send_to_char(ch, content.name)
		else:
			globalstuff.send_to_char(ch,"That is not a container.")
		return
	elif args.lower() != "" and args.lower().split()[0] == "at":
		if len(args.lower().split()) > 1:
			atargs = args.split(' ', 1)[1]
			item = globalstuff.get_obj_by_name_inv(ch,atargs.lower())
			if item == None:
				item = globalstuff.get_obj_by_name_room(ch.inroom,atargs.lower())
				showstats = True
			if item == None:
				if atargs.find(' ') != -1:
					words = atargs.split()
				else:
					words = [atargs.strip()]
				for roomdetail in ch.inroom.details:
					if atargs.lower().strip() in roomdetail.keywords:
						globalstuff.send_to_char(ch,roomdetail.description)
						return
					elif all(word.lower() in roomdetail.keywords for word in words):
						globalstuff.send_to_char(ch,roomdetail.description)
						return
			if item != None:
				globalstuff.send_to_char( ch, "Name:   %s" % item.name )
				globalstuff.send_to_char( ch, "Descripton: " )
				globalstuff.send_to_char( ch, item.description )
				if item.strength != 0:
					globalstuff.send_to_char( ch, "Strength mod: %d" % item.strength )
				if item.intellect != 0:
					globalstuff.send_to_char( ch, "Intellect mod: %d" % item.intellect )
				if item.charisma != 0:
					globalstuff.send_to_char( ch, "Charisma mod: %d" % item.charisma )
				if item.hp != 0:
					globalstuff.send_to_char( ch, "HP mod:       %d" % item.hp)
				if item.mana != 0:
					globalstuff.send_to_char( ch, "MANA mod:      %d" % item.mana)
				if item.type < 5:
					slotstring = "Wear slot: "
					if item.type == objtypes.OBJ_CHEST:
						slotstring += "Chest"
					elif item.type == objtypes.OBJ_HEAD:
						slotstring += "Head"
					elif item.type == objtypes.OBJ_LEGS:
						slotstring += "Legs"
					elif item.type == objtypes.OBJ_WRIST:
						slotstring +="Wrists"
					elif item.type == objtypes.OBJ_WEAPON:
						slotstring += "Weapon\n"
						slotstring += "Damage: %d - %d" % ( item.mindmg,item.maxdmg )
					globalstuff.send_to_char( ch, slotstring )
				return
	if args.lower() == "north":
		if ch.inroom.exits[0] == None:
			globalstuff.send_to_char( ch, "You cannot look that way, as there is no exit in that direction." )
			return
		globalstuff.send_to_char( ch, ch.inroom.exits[0].name )
		globalstuff.send_to_char( ch, ch.inroom.exits[0].description )
		if ch.inroom.exits[0].dungeonentrance != None:
			globalstuff.send_to_char( ch, ch.inroom.exits[0].dungeonentrance.ldesc)
		if ch.inroom.exits[0].exits == [None,None,None,None] and ch.inroom.exits[0].dungeonentrance == None:
			globalstuff.send_to_char( ch, "There are no exits in this room." )
		else:
			if ch.inroom.exits[0].exits != [None,None,None,None]:
				string1 = "Exits:"
				if ch.inroom.exits[0].exits[0]:
					string1 += " [North]"
				if ch.inroom.exits[0].exits[1]:
					string1 += " [East]"
				if ch.inroom.exits[0].exits[2]:
					string1 += " [South]"
				if ch.inroom.exits[0].exits[3]:
					string1 += " [West]"
				if ch.inroom.exits[0].dungeonentrance != None:
					string1 += " [DUNGEON]"
				globalstuff.send_to_char( ch, string1 )
		if ch.inroom.exits[0].contents != []:
			seenitemprompt = False
			for item in ch.inroom.exits[0].contents:
				if "hidden" not in item.flaglist or item in ch.foundhidden:
					if seenitemprompt == False:
						globalstuff.send_to_char( ch, "The following items are here:" )
						seenitemprompt = True
					globalstuff.send_to_char( ch, item.name )
		if ch.inroom.exits[0].charsinroom != []:
			globalstuff.send_to_char(ch, "The following characters are there:")
			for character in ch.inroom.exits[0].charsinroom:
				if character != ch:
					globalstuff.send_to_char(ch, character.name)
		return
	elif args.lower() == "east":
		if ch.inroom.exits[1] == None:
			globalstuff.send_to_char( ch, "You cannot look that way, as there is no exit in that direction." )
			return
		globalstuff.send_to_char( ch, ch.inroom.exits[1].name )
		globalstuff.send_to_char( ch, ch.inroom.exits[1].description )
		if ch.inroom.exits[1].dungeonentrance != None:
			globalstuff.send_to_char( ch, ch.inroom.exits[1].dungeonentrance.ldesc)
		if ch.inroom.exits[1].exits == [None,None,None,None] and ch.inroom.exits[1].dungeonentrance == None:
			globalstuff.send_to_char( ch, "There are no exits in this room." )
		else:
			if ch.inroom.exits[0].exits != [None,None,None,None]:
				string1 = "Exits:"
				if ch.inroom.exits[1].exits[0]:
					string1 += " [North]"
				if ch.inroom.exits[1].exits[1]:
					string1 += " [East]"
				if ch.inroom.exits[1].exits[2]:
					string1 += " [South]"
				if ch.inroom.exits[1].exits[3]:
					string1 += " [West]"
				if ch.inroom.exits[1].dungeonentrance != None:
					string1 += " [DUNGEON]"
				globalstuff.send_to_char( ch, string1 )
			if ch.inroom.exits[1].contents != []:
				seenitemprompt = False
				for item in ch.inroom.exits[1].contents:
					if "hidden" not in item.flaglist or item in ch.foundhidden:
						if seenitemprompt == False:
							globalstuff.send_to_char( ch, "The following items are here:" )
							seenitemprompt = True
						globalstuff.send_to_char( ch, item.name )
			if ch.inroom.exits[1].charsinroom != []:
				globalstuff.send_to_char(ch, "The following characters are there:")
				for character in ch.inroom.exits[1].charsinroom:
					if character != ch:
						globalstuff.send_to_char(ch, character.name)
			return
	elif args.lower() == "south":
		if ch.inroom.exits[2] == None:
			globalstuff.send_to_char( ch, "You cannot look that way, as there is no exit in that direction." )
			return
		globalstuff.send_to_char( ch, ch.inroom.exits[2].name )
		globalstuff.send_to_char( ch, ch.inroom.exits[2].description )
		if ch.inroom.exits[2].dungeonentrance != None:
			glbobalstuff.send_to_char(ch, ch.inroom.exits[2].dungeonentrance.ldesc)
		if ch.inroom.exits[2].exits == [None,None,None,None] and ch.inroom.exits[2].dungeonentrance == None:
			globalstuff.send_to_char( ch, "There are no exits in this room." )
		else:
			if ch.inroom.exits[0].exits != [None,None,None,None]:
				string1 = "Exits:"
				if ch.inroom.exits[2].exits[0]:
					string1 += " [North]"
				if ch.inroom.exits[2].exits[1]:
					string1 += " [East]"
				if ch.inroom.exits[2].exits[2]:
					string1 += " [South]"
				if ch.inroom.exits[2].exits[3]:
					string1 += " [West]"
				if ch.inroom.exits[2].dungeonentrance != None:
					string1 += " [DUNGEON]"
				globalstuff.send_to_char( ch, string1 )
		if ch.inroom.exits[2].contents != []:
			seenitemprompt = False
			for item in ch.inroom.exits[2].contents:
					if "hidden" not in character or item in ch.foundhidden:
						if seenitemprompt == False:
							globalstuff.send_to_char( ch, "The following items are here:" )
							seenitemprompt = True
						globalstuff.send_to_char( ch, item.name )
		if ch.inroom.exits[2].charsinroom != []:
			globalstuff.send_to_char(ch, "The following characters are there:")
			for character in ch.inroom.exits[2].charsinroom:
				if character != ch:
					globalstuff.send_to_char(ch, character.name)
		return
	elif args.lower() == "west":
		if ch.inroom.exits[3] == None:
			globalstuff.send_to_char( ch, "You cannot look that way, as there is no exit in that direction." )
			return
		globalstuff.send_to_char( ch, ch.inroom.exits[3].name )
		globalstuff.send_to_char( ch, ch.inroom.exits[3].description )
		if ch.inroom.dungeonentrance != None:
			globalstuff.send_from_char(ch, ch.inroom.dungeonentrance.rdesc)

		if ch.inroom.exits[3].exits== [None,None,None,None] and ch.inroom.exits[3].dungeonentrance == None:
			globalstuff.send_to_char( ch,"There are no exits in this room." )
		else:
			if ch.inroom.exits[0].exits != [None,None,None,None]:
				string1 = "Exits:"
				if ch.inroom.exits[3].exits[0]:
					string1 += " [North]"
				if ch.inroom.exits[3].exits[1]:
					string1 += " [East]"
				if ch.inroom.exits[3].exits[2]:
					string1 += " [South]"
				if ch.inroom.exits[3].exits[3]:
					string1 += " [West]"
				if ch.inroom.exits[3].dungeonentrance != None:
					string1 += " [DUNGEON]"
				globalstuff.send_to_char( ch, string1 )

			if ch.inroom.exits[3].contents != []:
				seenitemprompt = False
				for item in ch.inroom.exits[3].contents:
					if "hidden" not in character or item in ch.foundhidden:
						if seenitemprompt == False:
							globalstuff.send_to_char( ch, "The following items are here:" )
							seenitemprompt = True
							globalstuff.send_to_char( ch, item.name )
			if ch.inroom.exits[3].charsinroom != []:
				globalstuff.send_to_char(ch, "The following characters are there:")
				for character in ch.inroom.exits[3].charsinroom:
					if character != ch:
						globalstuff.send_to_char(ch, character.name)
			return
	elif args == "":
		globalstuff.send_to_char( ch, ch.inroom.name )
		globalstuff.send_to_char( ch, ch.inroom.description )
		if ch.inroom.dungeonentrance != None:
			globalstuff.send_to_char(ch, ch.inroom.dungeonentrance.ldesc)
		if ch.inroom.exits == [None,None,None,None] and ch.inroom.dungeonentrance == None:
			globalstuff.send_to_char( ch, "There are no exits in this room." )
		else:
			if ch.inroom.exits != [None,None,None,None]:
				string1 = "Exits:"
				if ch.inroom.exits[0]:
					string1 += " [North]"
				if ch.inroom.exits[1]:
					string1 += " [East]"
				if ch.inroom.exits[2]:
					string1 += " [South]"
				if ch.inroom.exits[3]:
					string1 += " [West]"
				if ch.inroom.dungeonentrance != None:
					string1 += " [DUNGEON]"
				globalstuff.send_to_char( ch, string1 )
			if ch.inroom.contents != []:
				seenitemprompt = False
				for item in ch.inroom.contents:
					if "hidden" not in item.flaglist or item in ch.foundhidden:
						if seenitemprompt == False:
							globalstuff.send_to_char( ch, "The following items are here:" )
							seenitemprompt = True
						globalstuff.send_to_char( ch, item.name )

			if len(ch.inroom.charsinroom) > 1:
				globalstuff.send_to_char( ch, "the following characters are here: " )
				for character in ch.inroom.charsinroom:
					if character != ch:
						globalstuff.send_to_char( ch, character.name )
	else:
		globalstuff.send_to_char(ch,"Look where?")

def CMD_quit(ch,args):
	globalstuff.send_to_char( ch, "Good bye!" )
	exit(0)
