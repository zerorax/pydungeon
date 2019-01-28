import globalstuff
import os

def get_skill_by_name(skillname):
	if len(globalstuff.skilllist) > 0:
		for skill in globalstuff.skilllist:
			if skill.name == skillname.lower().strip():
				return skill
	return None

def load_skills():
	filelist = os.listdir("skills/")
	for file in filelist:
		load_skill(file)

def load_skill(skillname):
	file = open("skills/" + skillname, "r")
	lines = file.readlines()
	file.close()
	codestarted = False
	code = None
	name = None
	cooldown = None
	classtype = None
	helptext = None
	needstarget = None
	skilltype = None

	for line in lines:
		if line.find(" ") == -1:
			split = [line.strip()]
		else:
			split = line.split(' ',1)
			split[0] = split[0].strip()
			split[1] = split[1].strip()
		if codestarted == False:
			if split[0] == "NAME":
				name = split[1]
			elif split[0] == "COOLDOWN":
				cooldown = split[1]
			elif split[0] == "CLASS":
				classtype = split[1]
			elif split[0] == "HELPTEXT":
				helptext = split[1].replace("!EOL!", "\n")
			elif split[0] == "NEEDSTARGET":
				needstarget = split[1]
			elif split[0] == "TYPE":
				skilltype = split[1]
			elif split[0] == "CODE":
				codestarted = True
				code = ""
				continue
		else:
			code = code + "\n" + line
	if code != None and name != None and cooldown != None and classtype != None and helptext != None and needstarget != None and skilltype != None:
		if code == "":
			print("No code in loaded skill, aborting.")
			exit(1)
		if name == "":
			print("No name in loaded skill, aborting.")
			exit(1)
		else:
			name = name.strip()
		if cooldown != "":
			try:
				cooldown = int(cooldown)
			except:
				print("Cooldown value in loaded skill was not an integer, aborting.")
				exit(1)
		if classtype != "":
			classtype = classtype.strip()
			if classtype != "warrior" and classtype != "mage" and classtype != "rogue":
				print("unknown class type in loaded skill, aborting")
				exit(1)
		else:
			print("No class type in loaded skill, aborting.")
			exit(1)
		if helptext == "":
			print("No help text in loaded skill, aborting.")
			exit(1)
		try:
			needstarget = bool(needstarget.strip())
		except:
			print("failed to convert needstarget to boolean, aborting")
			exit(1)
		if skilltype.strip() != "skill" and skilltype.strip() != "spell":
			print("skilltype of loaded skill is not skill or spell, aborting")
			exit(1)
			
		globalstuff.skilllist.append(globalstuff.Skill(name, skilltype, cooldown, classtype, helptext, code, needstarget))
	else:
		print("Error, skill %s could not be loaded from file %s.skill" %(skillname, skillname))
	
