import globalstuff
import objects
import rooms
import os
import factoids

def load_npcs(gamestate):
	filelist = os.listdir("npcs/")
	for file in filelist:
		load_npc(gamestate, file)

def initspawn(gamestate):
	if len(gamestate.npcprotos) > 0:
		for npcproto in gamestate.npcprotos:
			if npcproto.spawn == True:
				newnpc = globalstuff.NPC(gamestate, npcproto.nnum, npcproto.name, npcproto.charclass, npcproto.strength, npcproto.intellect,npcproto.charisma,npcproto.hp,npcproto.mana,npcproto.experience, npcproto.level, npcproto.rnum, npcproto.spawn, npcproto.respawn, npcproto.respawntime, npcproto.introduction, npcproto.items, npcproto.equipment, npcproto.skills, npcproto.flags, npcproto.factoids, npcproto.store)

def spawn_npc(gamestate,nnum):
	if len(gamestate.npcprotos) > 0:
		for npcproto in gamestate.npcprotos:
			if npcproto.nnum == nnum:
				newnpc = globalstuff.NPC(gamestate, npcproto.nnum, npcproto.name, npcproto.charclass, npcproto.strength, npcproto.intellect,npcproto.charisma,npcproto.hp,npcproto.mana,npcproto.experience, npcproto.level, npcproto.rnum,npcproto.spawn, npcproto.respawn, npcproto.respawntime, npcproto.introduction, npcproto.items, npcproto.equipment, npcproto.skills, npcproto.flags, npcproto.factoids, npcproto.store)
				globalstuff.send_to_room(rooms.get_room_by_num(gamestate,nnum), "%s suddenly appears before you." % newnpc.character.name)
				return newnpc
	print("Error, respawn of npc failed.")
	exit(1)

def load_npc(gamestate, filename):
	file = open("npcs/" + filename, "r")
	lines = file.readlines()
	file.close()
	name = None
	classtype = None
	strength = None
	intellect = None
	charisma = None
	hp = None
	experience = None
	level = None
	rnum = None
	spawn = None
	respawn = None
	respawntime = None
	itemlist = None
	equipmentlist = None
	nnum = None
	introduction = None
	factoidstring = None
	skills = None
	flags = None

	for line in lines:
		if line.find(' ') == -1:
			split = [line.strip()]
		else:
			split = line.split(' ', 1)
			split[0] = split[0].strip()
			split[1] = split[1].strip()
	
		if split[0] == "NAME":
			name = split[1]
		elif split[0] == "CLASS":
			classtype = split[1]
		elif split[0] == "STRENGTH":
			strength = split[1]
		elif split[0] == "INTELLECT":
			intellect = split[1]
		elif split[0] == "CHARISMA":
			charisma = split[1]
		elif split[0] == "HP":
			hp = split[1]
		elif split[0] == "MANA":
			mana = split[1]
		elif split[0] == "FLAGS":
			flags = split[1]
		elif split[0] == "FACTOIDS":
			factoidstring = split[1]
		elif split[0] == "EXPERIENCE":
			experience = split[1]
		elif split[0] == "LEVEL":
			level = split[1]
		elif split[0] == "ROOMNUM":
			rnum = split[1]
		elif split[0] == "SPAWN":
			spawn = split[1]
		elif split[0] == "RESPAWN":
			respawn = split[1]
		elif split[0] == "RESPAWNTIME":
			respawntime = split[1]
		elif split[0] == "NNUM":
			nnum = split[1]
		elif split[0] == "INTRODUCTION":
			introduction = split[1].replace("!EOL!", "\n")
		elif split[0] == "SKILLS":
			skills = split[1]
		elif split[0] == "ITEMS":
			itemlist = []
			if split[1] != "None":
				itemsline = split[1]
				if itemsline.find(',') != -1:
					items = itemsline.split(',')
					for item in items:
						try:
							onum = int(item)
							itemlist.append(globalstuff.create_object(gamestate,onum))
						except:
							print("inventory item in ITEMS field of %s contains non-integer value, aborthing." % filename)
							exit
						#itemlist.append(globalstuff.create_object(gamestate,onum))
		elif line.strip().split(' ',1)[0] == "EQUIPMENT":
			equipmentlist = [None,None,None,None,None]
			equipmentline = line.strip().split(' ', 1)[1] # saved in numbered order as per ObjTypes values
			if equipmentline.find(',') != -1:
				equipmentline = equipmentline.split(',')
				for equnum in range(0,5):
					if equipmentline[equnum].strip() == "None":
						equipmentlist[equnum] = None
					else:
						try:
							onum = int(equipmentline[equnum])
						except:
							print("onum of equipment entry in %s is not None or an integer, aborting." % filename)
							exit(1)
						equipmentlist[equnum] = objects.create_object(gamestate,onum)
			else:
				print("Malformed equipment line in %s, aborting." % filename)
				exit(1)
		else:
			print("Unknown field in NPC file %s, aborting" % filename)
			exit(1)
	if name == None or name == "":
		print("missing name entry in %s, aborting." % filename)
		exit(1)
	if introduction == None:
		print("no introduction found in %s, aborting." % filename)
		exit(1)
	if nnum == None:
		print("no nnum found in %s, aborting" % filename)
		exit(1)
	if classtype == None:
		print("did not find a class type in %s, aborting." % filename)
		exit(1)
	if strength == None:
		print("did not find a strength entry in %s, aborting." % filename)
		exit(1)
	if intellect == None:
		print("did not find a intellect entry in %s, aborting." % filename)
		exit(1)
	if charisma == None:
		print("did not find a charisma entry in %s, aborting" % filename)
		exit(1)
	if hp == None:
		print("did not find a HP entry in %s, aborting" % filename)
		exit(1)
	if experience == None:
		print("did not find an experience entry in %s, aborthing." % filename)
		exit(1)
	if level == None:
		print("did not find a level entry in %s, aborting." % filename)
		exit(1)
	if rnum == None:
		print("did not find a room number entry in %s, aborting." % filename)
		exit(1)
	if respawntime == None:
		print("did not find a respawn time in %s, aborting." % filename)
		exit(1)
	if respawn == None:
		print("did not find a respawn value in %s, aborting." % filename)
		exit(1)
	if spawn == None:
		print("did not find a spawn value in %s, aborting" % filename)
		exit(1)
	if itemlist == None:
		print("did not find an item list in %s, aborting." % filename)
		exit(1)
	if equipmentlist == None:
		print("did not find an equipment list entry in %s, aborting." % filename)
		exit(1)
	if spawn == "True":
		spawn = True
	elif spawn == "False":
		spawn = False
	else:
		print("spawn value in %s is not True or False, aborting." % filename)
		exit()
	if skills != None:
		if skills.find(",") != -1:
			skills = skills.lower().strip().split(",")
		else:
			skills = [skills.lower().strip()]
		for x in range(len(skills)):
			skills[x] = [skills[x],100]
	factoidlist = []
	if flags == None:
		flags = []
	else:
		if flags.find(",") != -1:
			flags = flags.strip().split()
		else:
			flags = [flags.strip()]
	if factoidstring != None:
		if factoidstring.find(',') != -1:
			fnums = factoidstring.split(',')
			for fact in fnums:
				try:
					factoidlist.append(factoids.get_factoid_by_num(gamestate,int(fact)))
				except:
					print("factoid entry malformed or contains non-integer value, aborting.")
					exit(1)
		else:
			if len(factoidstring) == 1:
				try:
					factoidlist = [factoids.get_factoid_by_num(gamestate,int(factoidstring))]
				except:
					print("unknown entry in factoids of npc %s." % filename)
					factoidlist = []

	if respawn.strip() == "True":
		respawn = True
	elif respawn.strip() == "False":
		respawn = False
	else:
		print("respawn value in %s is not a bool, aborting." % filename)
		exit(1)
	try:
		nnum = int(nnum)
	except:
		print("nnum in %s is not an integer, aborting." % filename)
	try:
		experience = int(experience.strip())
	except:
		print("experience value in %s not an integer, aborting." % filename)
		exit(1)
	try:
		level = int(level.lower())
	except:
		print("level value in %s not an integer, aborting." % filename)
	if len(itemlist) > 0:
		for item in itemlist:
			#check if item by that number exists, if not throw an error, otherwise put it in their inventory
			try:
				item = int(item)
			except:
				print("item entry of %s is not an interger, aborting." % filename)
				exit(1)
	try:
		rnum = int(rnum)
	except:
		print("room number in %s is not an integer, aborthing." % filename)
		exit(1)
	try:
		level = int(level)
	except:
		print("level value in %s is not an integer, aborting." % filename)
		exit(1)
	try:
		expereince = int(experience)
	except:
		print("experience value in %s is not an integer, aborting." % filename)
		exit(1)
	try:
		hp = int(hp)
	except:
		print("hp in %s not an integer, aborting" % filesystem)
		exit(1)
	try:
		mana = int(mana)
	except:
		print("mana in %s not an integer, aborting" % filesystem)
		exit(1)
	try:
		respawntime = int(respawntime)
	except:
		print("respawn time is not an integer in %s, aborting." % filename)
	try:
		strength = int(strength)
	except:
		print("strength entry in %s not an integer, aborting." % filename)
		exit(1)
	try:
		intellect = int(intellect)
	except:
		print("intellect entry in %s not an integer, aborting." % filename)
		exit(1)
	try:
		charisma = int(charisma)
	except:
		print("charisma entry in %s not an integer, aborting.")
		exit(1)

	gamestate.npcprotos.append(globalstuff.NPCProto(gamestate, name, nnum, classtype, strength, intellect, charisma, hp, mana, experience, level, rnum, spawn, respawn, respawntime, introduction, itemlist, equipmentlist, skills, flags, factoidlist))
