import globalstuff

def get_factoid_by_num(gamestate,fnum):
	try:
		return gamestate.factoiddict[fnum]
	except:
		return None

def load_factoids(gamestate):
	file = open("factoids.facts", "r")
	lines = file.readlines()
	file.close()

	fnum = 0
	factstarted = False
	for line in lines:
		if factstarted == False:
			split = line.strip().split(' ', 2)
			try:
				fnum = int(split[0])
			except:
				print("fnum in factoids.facts not an integer, aborting.")
				exit(1)
			if fnum not in gamestate.factoiddict:
				gamestate.factoiddict[fnum] = globalstuff.Factoid(fnum,None,None,None)
			if split[1] == "NAME":
				gamestate.factoiddict[fnum].name = split[2].strip()
			elif split[1] == "KEYWORDS":
				if split[2].find(' ') !=  -1:
					gamestate.factoiddict[fnum].keywords = split[2].strip().split(' ')
				else:
					gamestate.factoiddict[fnum].keywords = [split[2].strip()]
			elif split[1] == "FACTOID":
				factstarted = True
				firstline = True
				continue
			else:
				print("Unknown field in factoids.facts, aborting.")
				exit(1)
		else:
			if firstline == True:
				if line.strip() =="!END!":
					fact = ""
					gamestate.factoiddict[fnum].details = fact
					factstarted = False
				else:
					firstline = False
					fact = line.strip()
			else:
				if line.strip() == "!END!":
					factstarted = False
					gamestate.factoiddict[fnum].details = fact
				else:
					firstline = False
					fact = fact + "\n" + line.strip()
