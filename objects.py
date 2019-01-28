import os
import globalstuff
import rooms

def get_object_by_num(gamestate,num):
	for objproto in gamestate.objectprotos:
		if objproto.onum == num:
			return objproto
	print("Error, objproto %d not found in get_room_by_num, aborting." % num)
	exit(1)

def get_obj_by_name_room(room,objname):
	for item in room.contents:
		if item.name.lower() == objname.lower():
			return item
	for item in room.contents:
		if objname.lower() in item.name.lower():
			return item
	if objname.find(' ') == -1:
		words = [objname]
	else:
		words = objname.split()
	for item in room.contents:
		if all(word.lower() in item.name.lower() for word in words):
			return item
	return None

def create_object(gamestate,onum):
	objproto = get_object_by_num(gamestate,onum)
	newobject = globalstuff.Object(gamestate,objproto.onum, objproto.type, objproto.name, objproto.description, objproto.weight, objproto.strength, objproto.intellect, objproto.charisma, objproto.hp, objproto.mana, objproto.mindmg,objproto.maxdmg, objproto.value, objproto.flaglist)
	return newobject

def load_objects(gamestate):
	filelist = os.listdir("objects/")
	for file in filelist:
		load_object(gamestate,file)

def load_object(gamestate,filename):
	file = open("objects/" + filename, "r")
	lines = file.readlines()
	file.close()

	onum = None
	name = None
	desc = None
	type = None
	strength = None
	charisma = None
	intellect = None
	hp = None
	mana = None
	damage = None
	flaglist = None
	value = None
	weight = None

	for line in lines:
		if line.find(' ') != -1:
			split = line.strip().split(' ', 1)
			split[0] = split[0].strip()
			split[1] = split[1].strip()
		else:
			split = [line.strip()]
		if split[0] == "ONUM":
			onum = split[1]
		elif split[0].strip() == "NAME":
			name = split[1]
		elif split[0] == "DESC":
			desc = split[1].replace("!EOL!", "\n")
		elif split[0] == "WEIGHT":
			weight = split[1]
		elif split[0] == "VALUE":
			value = split[1]
		elif split[0].strip() == "TYPE":
			itemtype = split[1]
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
		elif split[0] == "DAMAGE":
			damage = split[1]
		elif split[0] == "FLAGS":
			flaglist = split[1]
		else:
			print("Unknown field in object file %s, aborting." % filename)

			exit(1)
	if onum == None:
		print("no onum found in %s, aborting" % filename)
		exit(1)
	if name == None:
		print("no name found in %s, aborting" % filename)
		exit(1)
	if desc == None:
		print("no description found in %s, aborting." % filename)
		exit(1)
	if weight == None:
		print("no weight entry found in %s, aborting." % filename)
		exit(1)
	if itemtype == None:
		print("no type found in %s, aborting" % filename)
		exit(1)
	if strength == None:
		print("no strength entry found in %s, aborting." % filename)
		exit(1)
	if intellect == None:
		print("no intellect entry found in %s, aborting" % filename)
		exit(1)
	if charisma == None:
		print("no charisma entry found in %s, aborting." % filename)
		exit(1)
	if hp == None:
		print("no hp entry found in %s, aborting." % filename)
		exit(1)
	if mana == None:
		print("no mana entry found in %s, aborting." % filename)
		exit(1)
	if damage == None:
		print("no damage entry found in %s, aborting." % filename)
		exit(1)
	if value == None:
		value = 0
	else:
		try:
			value = int(value)
		except:
			print("value entry in %s not an integer, aborting." % filename)
			exit(1)
	try:
		weight = float(weight)
	except:
		print("weight value in %s not a floating point, aborting" % filename)
		exit(1)
	try:
		hp = int(hp)
	except:
		print("hp entry in %s not an integer, aborting." % filename)
		exit(1)
	try:
		mana = int(mana)
	except:
		print("mana entry in %s not an integer, aborting." % filename)
		exit(1)
	try:
		onum = int(onum)
	except:
		print("onum of %s not an integer" % filename)
		exit(1)
	try:
		itemtype = int(itemtype)
	except:
		print("object type in %s not an integer, aborting" % filename)
		exit(1)
	try:
		strength = int(strength)
	except:
		print("strength entry in %s is not an integer, aborting" % filename)
		exit(1)
	try:
		intellect = int(intellect)
	except:
		print("intellect entry in %s not an integer, aborting" % filename)
		exit(1)
	try:
		charisma = int(charisma)
	except:
		print("charisma entry in %s not an integer, aborting." % filename)
		exit(1)
	if damage.find('-') != -1:
		dmgsplit = damage.split('-')
		try:
			mindmg = int(dmgsplit[0])
			maxdmg = int(dmgsplit[1])
		except:
			print("invalid damage entry in %s, aborting." % filename)
			exit(1)
	elif damage == "None":
		mindmg = 0
		maxdmg = 0
	else:
		print("malformed damage entry in %s, aborting." % filename)
		exit(1)
	if flaglist == "None":
		flaglist = []
	elif flaglist.find(',') == -1:
		flaglist = [flaglist.strip()]
	else:
		flaglist = flaglist.split(',')


	gamestate.objectprotos.append(globalstuff.ObjectProto(onum,itemtype,name,desc,weight,strength,intellect,charisma,hp,mana,mindmg,maxdmg,value,flaglist))
	
