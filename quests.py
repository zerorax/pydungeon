import os
import globalstuff
import objects
import npcs

def load_quests(gamestate):
	filelist = os.listdir("quests/")
	for file in filelist:
		load_quest(gamestate, file)

def load_quest(gamestate, filename):
	file = open("quests/" + filename, "r")
	lines = file.readlines()
	file.close()

	name = None
	questgiver = None
	questmessage = None
	questtarget = None
	keywords = None
	questcount = None
	rewardmessage = None
	experience = None
	silver = None
	honor = None

	for line in lines:
		split = line.split(' ' ,1)
		split[0] = split[0].strip()
		split[1] = split[1].strip()

		if split[0] == "NAME":
			name = split[1]
		elif split[0] == "QUESTGIVER":
			questgiver = split[1]
		elif split[0] == "QUESTMESSAGE":
			questmessage = split[1].replace("!EOL!","\n")
		elif split[0] == "QUESTINFO":
			questinfo = split[1]
		elif split[0] == "QUESTMESSAGE":
			questmessage = split[1]
		elif split[0] == "QUESTTARGET":
			questtarget = split[1]
		elif split[0] == "KEYWORDS":
			keywords = split[1]
		elif split[0] == "GOALCOUNT":
			questcount = split[1]
		elif split[0] == "REWARDMESSAGE":
			rewardmessage = split[1]
		elif split[0] == "EXPERIENCE":
			experience = split[1]
		elif split[0] == "SILVER":
			silver = split[1]
		elif split[0] == "HONOR":
			honor = split[1]
		else:
			print("Unknown field in %s, aborting." % filename)
			exit(1)

	if name == None or questgiver == None or questmessage == None or questtarget == None or keywords == None or questcount == None or rewardmessage == None or experience == None or silver == None or honor == None:
		print("required value missing from %s, aborting." % filename)
		exit(1)
	if questtarget.find(':') != -1:
		split2 = questtarget.split(':',1)
		if split2[0].strip() == "NPC":
			questtargettype = "NPC"
		elif split2[0].strip() == "OBJ":
			questtargettype = "OBJ"
		else:
			print("invalid type for questtarget in %s, aborting." % filename)
			exit(1)
	else:
		print("malformed questtarget entry in %s, aborting." % filename)
		exit(1)
	if questtargettype == "NPC":
		try:
			questtarget = globalstuff.get_char_by_nnum(gamestate,int(split2[1].strip()))
		except:
			questtarget = None
		if questtarget == None:
			print("Error questtarget in %s points to invalid nnum, aborting." % filename)
			exit(1)
	elif questtargettype == "OBJ":
		try:
			questtarget = int(split2[1].strip())
		except:
			print("Quest target OBJ value in %s not an integer, aborting." % filename)
			exit(1)
		questtarget = objects.creat_object(gamestate,questtarget)

	if keywords == None:
		keyswords = []
	elif keywords.find(' ') == -1:
		keywords = [keywords.strip()]
	else:
		keywords = keywords.strip().split()
	try:
		questcount = int(questcount)
	except:
		print("questcount in %s not an integer, aborting." % filename)
		exit(1)

	try:
		experience = int(experience)
	except:
		print("experience entry in %s not an integer, aborting." % filename)
		exit(1)
	try:
		honor = int(honor)
	except:
		print("honor entry in %s not an integer, aborting." % filename)
		exit(1)
	try:
		silver = int(silver)
	except:
		print("silver entry in %s not an integer, aborting." % filename)
		exit(1)
	try:
		questgiver = int(questgiver)
	except:
		print("questgiver in %s not an nnum integer, aborting." % filename)
		exit(1)
	questgiver = globalstuff.get_char_by_nnum(gamestate,questgiver)
	if questgiver == None:
		print("quest giver not found from %s, aborting." % filename)
		exit(1)


	globalstuff.Quest(name,questgiver,questmessage,questinfo,questtarget,keywords,questcount,rewardmessage,experience,silver,honor)
