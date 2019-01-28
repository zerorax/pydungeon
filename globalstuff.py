import commands
import random
import npcs
import rooms
import objects
from time import time
from collections import OrderedDict

def get_char_by_nnum(gamestate,nnum):
	for character in gamestate.charlist:
		if character.npc != None and character.npc.nnum == nnum:
			return character
	return None

def transport_character(ch,rnum=None,room=None):
	if room == None and rnum == None:
		print("ERROR transport_character called with no \"to\" variable.")
		return
	if rnum != None and rooms.get_room_by_num(ch.gamestate,rnum) == None:
		print("Error, rnum in transport_character invalid.")
		return
	send_from_char(ch,"%s disappears in a puff of smoke." % ch.name)
	ch.inroom.charsinroom.remove(ch)
	if rnum == None and room != None:
		send_to_room(room,"%s appears in a puff of smoke." % ch.name)
		room.charsinroom.append(ch)
		send_to_char(ch,"You have be transported to another location!")
		commands.CMD_look(ch,"")
	elif rnum != None and room == None:
		room = rooms.get_room_by_num(ch.gamestate,tornum)
		send_to_room(room, "%s appears in a puff of smoke." % ch.name)
		room.charsinroom.append(ch)
		send_to_char(ch,"You have be transported to another location!")
		commands.CMD_look(ch,"")

def strip_generic_words(wordlist):
	syntaxwords = ["the","a","who","where","when","that","is","of","if","what","why"]
	newwordlist = []
	for word in wordlist:
		if word.lower() not in syntaxwords:
			newwordlist.append(word)
	return newwordlist

def get_npc_by_num(gamestate,nnum):
	if len(gamestate.npclist) > 0:
		for npc in gamestate.npclist:
			if npc.nnum == nnum:
				return npc
	return None

class Factoid(object):
	def __init__(self,name,num,keywords,details):
		self.num = num
		self.name = name
		self.keywords = keywords
		self.details = details

class RoomUsable(object):
	def __init__(self,name,keywords,code):
		self.name = name
		self.keywords = keywords
		self.code = code

	def beused(self,ch):
		exec(self.code)

class RoomDetail(object):
	def __init__(self,keywords,description):
		self.keywords = keywords
		self.description = description

#find a character by name in a room
def get_obj_by_name_room(room,objname):
	if len(room.contents) > 0 and objname != "":
		for item in room.contents:
			if item.name.lower() == objname.lower():
				return item
		for item in room.contents:
			if objname.lower() in item.name.lower():
				return item
		if objname.find(' ') != -1:
			words = objname.lower().split()
		else:
			words = [objname.lower()]
		for item in room.contents:
			if all(word.strip().lower() in item.name.lower() for word in words):
				return item
	return None

def get_obj_by_name_inv(ch, objname):
	if ch.inventory != [] and objname != "":
		for item in ch.inventory:
			if item.name.lower() == objname.lower():
				return item
		for item in ch.inventory:
			if objname.lower().strip() in item.name.lower():
				return item
		if objname.find(' ') != -1:
			words = [objname.lower().strip()]
		else:
			words = objname.lower().split()
		for item in ch.inventory:
			if all(word in item.name.lower() for word in words):
				return item
	return None

def get_obj_by_name_container(container, objname):
	if container.contents != []:
		for item in container.contents:
			if objname.lower() == item.name.lower():
				return item
		if objname.find(' ') == -1:
			words = [objname.lower()]
		else:
			words = objname.lower().split()
		for item in container.contents:
			if objname.lower() in item.name.lower():
				return item
		for item in container.contents:
			if all(word.lower() in item.name.lower() for word in words):
				return item
	return None

def get_char_by_name(room,charactername):
	for character in room.charsinroom:
		if character.name.lower() == charactername.lower():
			return character
	if charactername.find(' ') == -1:
		words = [charactername.strip().lower()]
	else:
		words = charactername.lower().split()
	for character in room.charsinroom:
		if charactername.lower() in character.name.lower():
			return character
	for character in room.charsinroom:
		if all(word in character.name.lower() for word in words ):
			return character		
	return None

def get_char_by_nnum(gamestate,nnum):
	for character in gamestate.charlist:
		if character.npc != None and character.npc.nnum == nnum:
			return character
	return None

#we use this instead of print so that we can send text to npc's and in the future they will have
#scripted reactions
def send_to_char(ch, text):
	if ch.npc == None:
		print(text)
		if text.find("!SELFNAME!") != -1:
			text = text.replace("!SELFNAME!", ch.name)
	else:
		ch.npc.process_text(text)

def send_to_room(room,message):
	if room.charsinroom != []:
		for character in room.charsinroom:
			if character.sleeping == False:
				send_to_char(character,message)

def send_from_char(ch,message):
	if ch.inroom.charsinroom != []:
		for character in ch.inroom.charsinroom:
			if character != ch:
				send_to_char(character,message)

#do some little bit of processing to allow for scripted code to be executed that isn't hard coded into the game
#at a later time, skills will we stored outside the source in files containing both their code, and the data related to the skill
#such as it's name and usage and help info
def process_skill_code(text,args):
	if text.find("!SELF!") != -1:
		text = text.replace("!SELF!", "ch")
		text = text.replace("!ARGS!", args)
		return text

#store game state variables here, things that aren't tracked anywhere specific and would otherwise be globals
class GameState(object):
	def __init__(self):
		self.roomlist = []
		self.npcprotos = []
		self.objectprotos = []
		self.charlist = []
		self.respawntimers = []
		self.playerchar = None
		self.storelist = []
		self.decaytimers = []
		self.factoiddict = OrderedDict()
		self.npclist = []
		self.running = True
		self.dungeons = []

# we create an instance of this when we need to know item slot numbers, better than globals
class ObjTypes(object):
	def __init__(self):
		self.OBJ_WEAPON = 0
		self.OBJ_CHEST = 1	
		self.OBJ_HEAD = 2
		self.OBJ_WRIST = 3
		self.OBJ_LEGS = 4
		self.OBJ_CONTAINER = 5
		self.OBJ_ITEM = 6

objtypes = ObjTypes()

class ObjectProto(object):
	def __init__(self, onum, type, name, description, weight, strength, intellect, charisma, hp, mana, mindmg, maxdmg, value,flaglist):
		self.onum = onum
		self.type = type
		self.name = name
		self.value = value
		self.description = description
		self.strength = strength
		self.intellect = intellect
		self.charisma = charisma
		self.mindmg = mindmg
		self.maxdmg = maxdmg
		self.flaglist = flaglist
		self.weight = weight
		self.hp = hp
		self.mana = mana

#the Object class, used to represent items and other things in the game
class Object(object):
	def __init__(self, gamestate, number, type, name, description, weight, strength, intellect, charisma, hp, mana, mindmg,maxdmg, value,flaglist):
		self.number = number
		self.type = type
		self.name = name
		self.description = description
		if self.type == objtypes.OBJ_CONTAINER:
			self.contents = []
		self.strength = strength
		self.intellect = intellect
		self.charisma = charisma
		if self.type == objtypes.OBJ_WEAPON:
			self.mindmg = mindmg
			self.maxdmg = maxdmg
		self.flaglist = flaglist
		self.value = value
		self.weight = weight
		self.hp = hp
		self.mana = mana
		self.flaglist = flaglist
#the class of our classes
class ClassType(object):
	def __init__(self, name, strength, intellect, charisma, hp, mana):
		self.name = name
		self.strength = strength
		self.intellect = intellect
		self.charisma = charisma
		self.hp = hp
		self.mana = mana

#this class is used to keep track of commands, I thought a list of these would be more elegant than
#multiple dictionaries or a dictionary of lists or something like that
class CommandObj(object):
	def __init__(self, name, function, helpinfo,whileasleep = True):
		self.function = function
		self.name = name
		self.helpinfo = helpinfo
		self.whileasleep = whileasleep

class Store(object):
	def __init__(self, gamestate, npclist, itemtypes, room, money, items):
		self.npclist = []
		if len(npclist) > 0:
			for npc in npclist:
				newnpc = npcs.spawn_npc(gamestate, npc)
				newnpc.store = self
				self.npclist.append(newnpc)
		self.itemtypes = itemtypes
		self.room = rooms.get_room_by_num(gamestate,room)
		if self.room == None:
			print("room in store entry not found")
			exit(1)
		self.room.contents.append(objects.create_object(gamestate,3))
		container = objects.get_obj_by_name_room(self.room,"shelves")
		if container == None:
			print("shelves container not in store, aborting.")
			exit(1)
		if items != None and len(items)>0:
			for item in items:
				container.contents.append(objects.create_object(gamestate,item))
		self.room.store = self
		self.money = money
		self.playerbalance = 0
		self.playerwarned = False
		self.playerdishonored = False
		self.playertook = []

#our room class. Rooms are places the character can be. The will see the people and things there after reading a short room description
class Room(object):
	def __init__(self,number,name,description,contents,exits,details,usables):
		self.rnum = number
		self.name = name
		self.description = description
		self.exits = exits	# Should be a list, [0]=North,[1]=East,[2]=South,[3]=West
		self.contents = contents	# items in this room(on the floor)
		self.charsinroom = [] # list of characters in the room
		self.store = None
		self.details = details
		self.usables = usables
		self.dungeonentrance = None
		

class Skill(object):
	def __init__(self, name, type, cooldown, classtype, helptext, code, needstarget=True):
		self.name = name
		self.cooldown = cooldown
		self.code = code
		self.classtype = classtype
		self.helptext = helptext
		self.needstarget = needstarget
		self.type = type

	def callskill(self,ch,args):
		newcode = process_skill_code(self.code, args)
		exec(newcode)
		return (self.name,self.cooldown)

class TimeLimitedAffect(object):
	def __init__(self, length, strength, intellect, charisma, hp, mana, wearofftext):
		self.endtime = time()+length
		self.strength = strength
		self.intellect = intellect
		self.charisma = charisma
		self.hp = hp
		self.mana = mana
		self.wearofftext = wearofftext

class CooldownTimer(object):
	def __init__(self, length, name):
		self.endtime = time()+length
		self.name = name

class DecayTimer(object):
	def __init__(self, length, obj, inlist, msgtarget):
		self.endtime = time()+length
		self.obj = obj
		self.inlist = inlist
		self.msgtarget = msgtarget

class Quest(object):
	def __init__(self,name,questgiver,questmessage,questinfo,questtarget,questkeywords,questcount,rewardmessage,experience,silver,honor):
		self.name = name
		self.questmessage = questmessage
		self.questinfo = questinfo
		self.questkeywords = questkeywords
		self.rewardmessage = rewardmessage
		self.experience = experience
		self.silver = silver
		self.honor = honor
		self.questgiver = questgiver
		questgiver.questlist.append(self)
		self.questtarget = questtarget
		self.questcount = questcount
		self.queststarted = False

class NPCProto(object):
	def __init__(self, gamestate, name, nnum, charclass, strength, intellect, charisma, hp, mana, experience, level, rnum, spawn, respawn, respawntime, introduction, items, equipment, skills, flags, factoidlist):
		self.name = name
		self.nnum = nnum
		self.spawn = spawn
		self.charclass = charclass
		self.strength = strength
		self.intellect = intellect
		self.charisma = charisma
		self.hp = hp
		self.mana = mana
		self.experience = experience
		self.level = level
		self.rnum = rnum
		self.items = items
		self.equipment = equipment
		self.respawn = respawn
		self.respawntime = respawntime
		self.store = None
		self.introduction = introduction
		self.factoids = factoidlist
		self.skills = skills
		self.flags = flags

class NPC(object):
	def __init__(self, gamestate, nnum, name, charclass, strength, intellect, charisma, hp, mana, experience, level, rnum, spawn, respawn, respawntime, introduction, items, equipment, skills, flags, factoidlist, store = None):
		self.character = Character(gamestate, name, charclass, strength, intellect, charisma,  rnum)
		self.gamestate = gamestate
		self.respawn = respawn
		self.respawntime = respawntime
		self.nnum = nnum
		self.rnum = rnum
		self.character.hp = hp
		self.character.hpmax = hp
		self.character.mana = mana
		self.character.manamax = mana
		self.character.equipment = equipment
		self.character.inventory = items
		self.character.experience = experience
		self.character.level = level
		self.character.npc = self
		self.store = store
		self.metplayer = False
		self.introduction = introduction
		self.factoids = factoidlist
		self.character.skills = skills
		self.character.flags = flags
		self.spawn = spawn
		gamestate.npclist.append(self)


	def process_text(self, text):
		pass # we will put in response scriping here eventually

class Character(object):
	def __init__(self, gamestate, name, charclass, strength, intellect, charisma, rnum = 0, npc = None, respawn = False, respawntime = None):
		self.gamestate = gamestate
		self.name = name
		self.charclass = charclass
		self.strength = strength
		self.intellect = intellect
		self.sleeping = False
		self.hp = classdict[charclass].hp
		self.mana = classdict[charclass].mana
		self.hpmax = self.hp
		self.manamax = self.mana
		self.charisma = charisma
		self.level = 1
		self.experience = 0
		self.inventory = []
		self.equipment = [None,None,None,None,None]
		self.inroom = rooms.get_room_by_num(gamestate,rnum)
		self.inroom.charsinroom.append(self)
		self.respawn = respawn
		self.respawntime = respawntime
		self.cooldowns = []
		self.timelimitedaffects = []
		self.fightinglist = []
		self.questlist = []
		self.fightingtarget = None
		self.npc = npc
		gamestate.charlist.append(self)
		self.statpoints = 0
		self.skillpoints = 0
		self.honor = 0
		self.skills = []
		self.flags = []
		self.enemies = []
		gamestate.charlist.append(self)
		self.foundhidden = []
		self.dungeon = None
		self.dungeonloc = [None,None]

	def max_hp(self):
		hpbonus = 0
		for slot in self.equipment:
			if slot != None:
				hpbonus += slot.hp
		if self.timelimitedaffects != []:
			for affect in self.timelimitedaffects:
				hpbonus += affect.hp
		return self.hpmax + hpbonus

	def max_mana(self):
		manabonus = 0
		for slot in self.equipment:
			if slot != None:
				manabonus += slot.mana
		if self.timelimitedaffects != []:
			for affect in self.timelimitedaffects:
				manabonus += affect.mana
		return self.manamax + manabonus

	def maxweight(self):
		if self.strength * 10 < 70:
			return 70
		return self.strength * 10

	def get_weight(self):
		weight = 0
		if self.inventory != []:
			for item in self.inventory:
				weight = weight + item.weight
		for item in self.equipment:
			if item != None:
				weight = weight + item.weight
		return weight

	def do_damage(self,target,amount):
		target.hp -= amount
		if target.hp < 1:
			target.die(self.name)
			send_to_char(self, "You have killed your target")
			#TODO add diminishing returns on experience from lower level npc's
			if self.level > target.level:
				self.experience += int(self.fightingtarget.experience - (self.level - target.level * .2))
				exp = int(self.fightingtarget.experience - (self.level - target.level * .2))
			elif self.level < target.level:
				self.experience += int(self.fightingtarget.experience * (fightingtarget.level - self.level * .2))
				exp = int(self.fightingtarget.experience * (fightingtarget.level - self.level * .2))
			else:
				self.experience += self.fightingtarget.experience
				exp = self.fightingtarget.experience
			send_to_char(self, "You have gained %d experience!" % exp)
			self.checklevelup()
			self.fightingtarget = None
			if self.fightinglist != []:
				send_to_char(self, "You switch your focus to %s and begin attacking." % self.fightinglist[0].name)
				self.fightingtarget = self.fightinglist[0]
			return

	def show_prompt(self):
		send_to_char(self,"%d hp | %d mana> " % (self.hp,self.mana))

	def fight(self):
		stoppedfighting = False
		if self.fightinglist == []:
			stoppedfighting = True
		elif self.fightingtarget != None:
			send_to_char(self,"")
			self.attack()
		elif self.fightinglist != []:
			send_to_char(self, "You are in a fight but don't have a target!")
		if len(self.fightinglist) > 0:
			for attacker in self.fightinglist:
				attacker.attack()
		if stoppedfighting == False:
			self.show_prompt()


	def die(self, killername):
		if self.npc == None:
			commands.CMD_score(self,"")
			print("You have died, the game will now exit.")
			self.gamestate.running = False
			exit(0)
		if self.fightingtarget.questlist != []:
			for quest in self.fightingtarget.questlist:
				if quest.questtarget == self:
					quest.questcount -= 1
		send_to_char(self, "You have been killed by %s." % killername)
		send_to_char(self.fightingtarget, "You have killed %s." % self.name)
		if self.npc.respawn == True:
			self.gamestate.respawntimers.append(CooldownTimer(self.npc.respawntime*60,self.npc.nnum))
		self.inroom.charsinroom.remove(self)
		self.gamestate.charlist.remove(self)
		#we don't keep fightinglist in npc's rigth now, so if they are an npc we'll get an error with this next line
		if self.fightingtarget.npc == None: # the character that killed us is a player, so they have a list of targets they are fighting
			self.fightingtarget.fightinglist.remove(self)
		self.fightingtarget = None
		#create the corpse
		corpse = Object(self.gamestate, 0, objtypes.OBJ_CONTAINER, "the corpse of %s" % self.name, "the dead corpse of %s" % self.name, 75, 0, 0, 0, 0, 0, 0, 0, 0,flaglist = ["nopickup", "decomposing", "noputin"])
		#Add items to the corpse that it is carrying
		if self.equipment[objtypes.OBJ_CHEST] != None:
			corpse.contents.append(self.equipment[objtypes.OBJ_CHEST])
		if self.equipment[objtypes.OBJ_HEAD] != None:
			corpse.contents.append(self.equipment[objtypes.OBJ_HEAD])
		if self.equipment[objtypes.OBJ_WRIST] != None:
			corpse.contents.append(self.equipment[objtypes.OBJ_WRIST])
		if self.equipment[objtypes.OBJ_LEGS] != None:
			corpse.contents.append(self.equipment[objtypes.OBJ_LEGS])
		if self.equipment[objtypes.OBJ_WEAPON] != None:
			corpse.contents.append(self.equipment[objtypes.OBJ_WEAPON])
		if self.inventory != []:
			for item in self.inventory:
				corpse.contents.append(item)
		self.inroom.contents.append(corpse)
		if self.npc.store != None:
			self.npc.store.npclist.remove(self.npc)
		self.gamestate.charlist.remove(self)
		self.gamestate.npclist.remove(self.npc)
		self.gamestate.decaytimers.append(DecayTimer(120,corpse,self.inroom.contents,self.inroom))
		return

	def checklevelup(self):
		if self.experience >= self.getnextlevelexp() and self.level < 10:
			self.level += 1
			send_to_char(self, "You have reached level %d. Congrats!" % self.level)
			self.hpmax += 10
			self.hp = self.max_hp()
			self.manamax += 10
			self.mana = self.max_mana()
			send_to_char(self,"Your max mana and hp have been increased by 10, and they\nhave been restored to full.")
			self.strength += 1
			self.intellect += 1
			self.charisma += 1
			self.statpoints += 2
			self.skillpoints += 1
			send_to_char(self,"Your base stats have been increased by 1, and you have\nreceived 2 stat points and 1 skill point.")
		return

	def getnextlevelexp(self):
		nextlevelgoal = 100
		if self.level > 9:
			return 0
		else:
			for level in range(1,10+1):
				if level < self.level:
					nextlevelgoal += nextlevelgoal * 1.3
					nextlevelgoal = int(nextlevelgoal)
				else:
					return nextlevelgoal

	def getdmg(self):
		mindmg = 0
		maxdmg = 3
		#calculate weapon damage mod
		if self.equipment[objtypes.OBJ_WEAPON] != None:
			mindmg += self.equipment[objtypes.OBJ_WEAPON].mindmg
			maxdmg += self.equipment[objtypes.OBJ_WEAPON].maxdmg
		#add half a damage for every strength point above class norm(TODO: make different classes have different bonuses from stats and base damage/damage modifier)
		if self.charclass == "warrior": #warrior
			dmgmod = (self.getstrength() - classdict[self.charclass].strength) * 0.7 #warriors are good at using their strength
			dmgmod = dmgmod + (self.getintellect() - classdict[self.charclass].intellect) * 0.2 #warriors use intellect to deal more dangerous blows
		elif self.charclass == "mage": #mage
			dmgmod = (self.getstrength() - classdict[self.charclass].strength) * 0.3 #mages don't learn in their training how to use their strength well
			dmgmod = dmgmod + (self.getintellect() - classdict[self.charclass].intellect) * 0.3 #mages can make better strikes because of their superior intellect
		elif self.charclass == "rogue": #rogue
			dmgmod = (self.getstrength() - classdict[self.charclass].strength) * 0.6 #rogues are efficient strikers and are able to make more deadly strikes
			dmgmod = dmgmod + (self.getintellect() - classdict[self.charclass].intellect) * 0.5 # rogues are deadly like assassins, using their knowledge to deal deadly strikes to their opponents
		else:
			dmgmod = 0
		dmgmod = int(dmgmod)
		#calculate damage
		dmg =  random.randrange(mindmg+dmgmod,maxdmg+dmgmod+1)
		if dmg < 1:	#minimum damage is 1 for any attack, even a bitch slap hurts right?
			dmg = 1
		return dmg

	def begincombat(self, target):
		if target not in self.fightinglist and target != None:
			self.fightinglist.append(target)
		elif self.fightingtarget == target:
			#send_to_char(self, "You are already fighting that target.")
			return
		if self.fightingtarget != target:
			self.fightingtarget = target
			send_to_char( self, "You begin fighting %s." % target.name )
		else:
			send_to_char(self, "You are alredy targeting them")
			return
		self.fightingtarget.fightingtarget = self
		if target.npc != None and target.npc.store != None:
			if len(target.npc.store.npclist) > 0:
				for shopkeep in target.npc.store.npclist:
					if shopkeep != target.npc:
						if shopkeep.character not in self.fightinglist:
							self.fightinglist.append(shopkeep.character)
							shopkeep.character.fightingtarget = self
							send_to_char(self, "%s joins the battle in defence of the store!" % shopkeep.character.name )
		alreadyattacking = False

		for cooldown in self.cooldowns:
			if cooldown.name == "attack":
				alreadyattacking = True
		if alreadyattacking == False:
			self.cooldowns.append(CooldownTimer(3, "attack"))
			return
		return

	def attack(self):
		if self.fightingtarget != None:
			dmg = self.getdmg()
			send_to_char(self, "You do %d damage to %s." %(dmg, self.fightingtarget.name))
			send_to_char(self.fightingtarget, "%s does %d damage to you." % (self.name, dmg))
			self.do_damage(self.fightingtarget,dmg)
			self.cooldowns.append(CooldownTimer(3, "attack"))

	def rerollstats(self):
		random.seed()
		self.strength = random.randrange(classdict[self.charclass].strength - 2, classdict[self.charclass].strength + 3)
		self.intellect = random.randrange(classdict[self.charclass].intellect - 2, classdict[self.charclass].intellect + 3)
		self.charisma = random.randrange(classdict[self.charclass].charisma - 2, classdict[self.charclass].charisma + 3)
		return

	def getstrength(self):
		strbonus = 0
		for slot in self.equipment:
			if slot != None:
				strbonus += slot.strength
		if self.timelimitedaffects != []:
			for affect in self.timelimitedaffects:
				strbonus += affect.strength
		return self.strength + strbonus

	def getintellect(self):
		intelbonus = 0
		for slot in self.equipment:
			if slot != None:
				intelbonus += slot.intellect
		if self.timelimitedaffects != []:
			for affect in self.timelimitedaffects:
				intelbonus += affect.intellect
		return self.intellect + intelbonus

	def getcharisma(self):
		chabonus = 0
		for slot in self.equipment:
			if slot != None:
				chabonus = slot.charisma
		if self.timelimitedaffects != []:
			for affect in self.timelimitedaffects:
				chabonusbonus += affect.charisma
		return self.charisma + chabonus

classdict = { "warrior" : ClassType("warrior",  10, 5, 5, 100, 15), "mage" : ClassType("mage", 5, 10, 5, 75, 100), "rogue" : ClassType("rogue", 6, 8, 10, 80,75) }

skilllist = []
commandaliasdict = OrderedDict()
commandaliasdict["n"] = ["north",commands.CMD_north,False]
commandaliasdict["s"] = ["south",commands.CMD_south,False]
commandaliasdict["e"] = ["east",commands.CMD_east,False]
commandaliasdict["w"] = ["west",commands.CMD_west,False]
commandaliasdict["equ"] = ["equipment",commands.CMD_equipment,True]
commandaliasdict["inv"] = ["inventory",commands.CMD_inventory,True]
commandaliasdict["kill"] = ["attack",commands.CMD_attack,False]
commandaliasdict["exit"] = ["quit",commands.CMD_quit,True]
commandaliasdict["wear"] = ["equip",commands.CMD_equip,False]
commandaliasdict["wield"] = ["equip",commands.CMD_equip,False]
commandaliasdict["pull"] = ["use",commands.CMD_use,False]
commandaliasdict["push"] = ["use",commands.CMD_use,False]
commandaliasdict["touch"] = ["use",commands.CMD_use,False]

commandlist = [ CommandObj("help", commands.CMD_help, "Display the help menu."), \
CommandObj("alias", commands.CMD_alias,"Display a list of command shortcuts which"), \
CommandObj("look", commands.CMD_look, "View the room you are in and the things within it.\nYou may use the look command with a direction to see what's in an adjancent room\nSyntax: 'look <direction>'.\nYou may also look at an item in your inventory or on the ground in the room you are in using\nSyntax 'loot at <item name>.\nFurthermore, you may look inside objects which are containers(including corpses) by using the syntax 'look in <container name>", False), \
CommandObj("quit", commands.CMD_quit, "Exit the game."), \
CommandObj("balance", commands.CMD_balance, "Show your balance of coins, and if you are in a store, the amount you owe."), \
CommandObj("sell", commands.CMD_sell, "sell an item to the store you are in",False), \
CommandObj("pay", commands.CMD_pay, "Pay the merchant at the store you are at.",False), \
CommandObj("attack", commands.CMD_attack, "Attack an npc in the room you are in. Syntax: 'attack <character name>'. using attack when you are already fighting will switch your target,\nbut your previous target will continue attacking you.",False), \
CommandObj("north", commands.CMD_north, "Move north, if the room you are in has an exit to the north.",False), \
CommandObj("east", commands.CMD_east, "Move east, if the room you are in has an exit to the east.",False), \
CommandObj("south",commands.CMD_south, "Move south, if the room you are in has an exit to the south.",False), \
CommandObj("west", commands.CMD_west, "Move west, the the room you are in has an exit to the west.",False), \
CommandObj("inventory", commands.CMD_inventory, "See a list of the items you are carrying."), \
CommandObj("equip", commands.CMD_equip, "Equip an item from your inventory. Syntax: 'equip <item name>'.",False), \
CommandObj("equipment", commands.CMD_equipment, "This command shows you the equipment you are currently using."),\
CommandObj("put", commands.CMD_put, "Use this command to put something in a container. Syntax: 'put <item> in <container name>'.",False), \
CommandObj("remove", commands.CMD_remove, "Remove an item you are using. Syntax: 'remove <item name>'.",False), \
CommandObj("commands", commands.CMD_commands, "List all available commands to the user."), \
CommandObj("drop", commands.CMD_drop, "Drop an item in your inventory onto the ground in the room you are in.\nSyntax: 'drop <item name>'.",False), \
CommandObj("get", commands.CMD_get, "Pick up an item from the room you are in. Syntax: 'get <item name>'.\nYou may also get an item from a container in your inventory or on the ground.\nSyntax 'get <item name> from <container name>'.",False), \
CommandObj("cast", commands.CMD_cast, "Cast a spell, syntax: 'cast <spell name> [<target>]'.",False), \
CommandObj("score", commands.CMD_score, "Show you your character information and current score/stats."), \
CommandObj("loot", commands.CMD_loot, "Loot the contents of a corpse or container on the floor.\nSyntax: 'loot <object name>",False), \
CommandObj("sleep", commands.CMD_sleep, "Go to sleep. Sleeping helps you restore health and mana faster."), \
CommandObj("wake", commands.CMD_wake, "Wake up from being asleep."), \
CommandObj("boost", commands.CMD_boost, "increase your strength, charisma, or intellect by spending 1 stat point."),
CommandObj("say", commands.CMD_say, "send a message to characters in the room. eventually they will respond to certain triggers.",False), \
CommandObj("talk", commands.CMD_talk, "talk to an npc. talking to npc's can give you quests or information relevant to the storyline",False), \
CommandObj("ask", commands.CMD_ask, "Ask a question to an NPC regarding something they may know about such as a quest or story detail.",False), \
CommandObj("quests", commands.CMD_quests, "Display a list of quests you are currently on."), \
CommandObj("give", commands.CMD_give, "Give an item to another character.", False), \
CommandObj("learn", commands.CMD_learn, "Learn a skill from a skill trainer. Syntax: 'learn <skill> from <character name>'.",False), \
CommandObj("buy", commands.CMD_buy, "Purchase an item from a store. Store items are kept in the shelves.",False), \
CommandObj("skills", commands.CMD_skills, "Show a list of skills and spells you have learned."), \
CommandObj("flee", commands.CMD_flee, "Flee a fight. You may specify a direction or just flee in any direction available.", False), \
CommandObj("search", commands.CMD_search, "Search the room you are in for hidden objects", False), \
CommandObj("use", commands.CMD_use, "Use an object in the room you are in. These objects are found by reading room descriptions,\nThey do not appear in the list of items on the ground.", False), \
CommandObj("enter",commands.CMD_enter, "Enter a dungeon or catacomb if there is an entrance in the room you are in.", False ), \
CommandObj("leave",commands.CMD_leave, "Leave a dungeon. you must be standing at the exit marked by the @ symbol.", False ) ]
