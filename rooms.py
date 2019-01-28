import os
import globalstuff
import objects

def get_room_by_num(gamestate,num):
	for room in gamestate.roomlist:
		if room.rnum == num:
			return room
	print("Error, room %d not found in get_room_by_num, aborting." % num)
	exit(1)

def load_rooms(gamestate):
	filelist = os.listdir("rooms/")
	for file in filelist:
		load_room(gamestate,file)
	# convert exits from integers to pointers to rooms
	for room in gamestate.roomlist:
		for x in range(0,4):
			if room.exits[x] == None:
				pass
			else:
				room.exits[x] = get_room_by_num(gamestate,room.exits[x])
		if room.contents != []:
			for x in range(0, len(room.contents)):
				room.contents[x] = objects.create_object(gamestate,room.contents[x])

def load_room(gamestate, filename):
	file = open("rooms/%s" % filename, "r")
	lines = file.readlines()
	file.close()

	rnum = None
	name = None
	descriptions = None
	exits = None
	contents = None
	usables = []
	details = []

	descstarted = False
	
	for line in lines:
		if descstarted == False:
			if line.find(' ') == -1:
				split = [line.strip()]
			else:
				split = line.strip().split(' ',1)
				split[0] = split[0].strip()
				split[1] = split[1].strip()
			if split[0] == "RNUM":
				rnum = split[1]
			elif split[0] == "NAME":
				name = split[1]
			elif split[0] == "CONTENTS":
				contents = split[1]
			elif split[0] == "DETAIL":
				details.append([split[1].split(':',1)[0],split[1].split(':',1)[1]])
			elif split[0] == "USABLE":
				usables.append([split[1].split(":",1)[0],split[1].split(":",1)[1].split(' '),split[1].split(':',2)[2]])
			elif split[0] == "EXITS":
				if split[1].find(',') == -1:
					print("Malformed EXITS entry in %s, aborting." % filename)
					exit(1)
				else:
					exits = split[1].split(',')
					for x in range(0,4):
						if exits[x].strip() == "None":
							exits[x] = None
						else:
							try:
								exits[x] = int(exits[x])
							except:
								print("exit in %s is not None or an integer, aborting." % filename)
								exit(1)
			elif split[0] == "DESC":
				descstarted = True
				description = "No description in room file."
				firstline = True
				continue
			else:
				print("Unknown entry in %s, aborting" % filename)
				print(split)
				exit(1)
		else:
			if line.strip() == "!ENDDESC!":
				descstarted = False
				continue
			if firstline == True:
				description = line.strip()
				firstline = False
				continue
			else:
				description = description + '\n' + line.strip()
				continue

	if rnum == None:
		print("rnum not found in %s, aborting" % filename)
		exit(1)
	if name == None:
		print("name entry not found in %s, aborting." % filename)
		exit(1)
	if exits == None:
		print("exits entry not found in %s, aborting." % filename)
		exit(1)
	if description == None:
		print("no description found in %s, aborting." % filename)
		exit(1)
	if contents == None:
		print("no room contents entry found in %s, aborting." % filename)
		exit(1)
	if contents == "None":
		contents = []
	else:
		if contents.find(',') == -1:
			try:
				contents = [int(contents)]
			except:
				print("item entry in %s is not an integer, aborting." % filename)
				exit(1)
		else:
			list = contents.split(',')
			for x in range(len(list)):

				try:
					list[x] = int(list[x].strip())
					contents = list
				except:
					print("item entry in %s list not an integer, aborting.")
					exit(1)
	if len(details) > 0:
		for x in range(len(details)):
			details[x] = globalstuff.RoomDetail(details[x][0].split(),details[x][1].strip())
	if len(usables) > 0:
		for x in range(len(usables)):
			usables[x] = globalstuff.RoomUsable(usables[x][0],usables[x][1],usables[x][2])
	try:
		rnum = int(rnum)
	except:
		print("rnum in %s not an integer, aborting." % filename)
		exit(1)

	# we will make the room, and store exits as integers for now, then after loading all
	# rooms we will go back and convert exits to pointers to rooms
	gamestate.roomlist.append(globalstuff.Room(rnum,name,description,contents,exits,details,usables))
