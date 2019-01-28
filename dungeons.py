import random
import rooms

class DungeonRoom(object):
	def __init__(self):
		self.contents = []
		self.flags = []
		self.charsinroom = []
		self.usables = []
		self.roomdetails = []
		self.roomtype = None
		self.cavenum = None
		self.cavelocations = []

class Cave(object):
	def __init__(self,cavenum,roomlist):
		self.cavenum = cavenum
		self.roomlist = roomlist

	def get_westmost(self):
		westmost = self.roomlist[0]
		for room in self.roomlist:
			if room[0] < westmost[0]:
				westmost = room
		return westmost

	def get_eastmost(self):
		eastmost = self.roomlist[0]
		for room in self.roomlist:
			if room[0] > eastmost[0]:
				eastmost = room
		return eastmost

	def get_northmost(self):
		northmost = self.roomlist[0]
		for room in self.roomlist:
			if room[1] > northmost[1]:
				northmost = room
		return northmost

	def get_southmost(self):
		southmost = self.roomlist[0]
		for room in self.roomlist:
			if room[1] < southmost[1]:
				southmost = room
		return southmost

class DungeonEntrance(object):
	def __init__(self, room, dungeon, rdesc = None, ldesc = None):
		self.room = room
		self.dungeon = dungeon
		self.rdesc = rdesc
		self.ldesc = ldesc

class Dungeon(object):
	def __init__(self,gamestate,height,width,cavenum,rnum,rdesc,ldesc):
		self.matrix = []
		self.height = height
		self.width = width
		self.caves = []
		self.cavelocations = []
		for x in range(width):
			self.matrix.append([])
			for y in range(height):
				self.matrix.append([])
				self.matrix[x].append(DungeonRoom())
		caves_fit = False
		while caves_fit == False:
			self.cavelocations = []
			self.caves = []
			while self.cavelocations == [] or None in self.cavelocations:
				spawn = self.spawn_caves(cavenum)
				if spawn == 0:
					caves_fit = True
					break
				else:
					self.caves = []
					self.cavelocations = []
					continue
			if caves_fit == True:
				break

		self.start = self.caves[0].roomlist[random.randrange(len(self.caves[0].roomlist))]
		room = rooms.get_room_by_num(gamestate,rnum)
		self.entrance = DungeonEntrance(room,self,rdesc,ldesc)
		room.dungeonentrance = self.entrance

	def test_cave_spread(self):
		for location in range(len(self.cavelocations)):
			for location2 in range(len(self.cavelocations)):
				if location != location2:
					if self.cavelocations[location] != None and self.cavelocations[location2] != None:
						if self.cavelocations[location][0] > self.cavelocations[location2][0]:
							if self.cavelocations[location][1] > self.cavelocations[location2][1]:
								if self.cavelocations[location][0]-self.cavelocations[location2][0] <= 12 and self.cavelocations[location][1]-self.cavelocations[location2][1] <= 12:
									self.cavelocations[location] = None
							elif self.cavelocations[location][1] < self.cavelocations[location2][1]:
								if self.cavelocations[location2][0]-self.cavelocations[location][0] <= 12 and self.cavelocations[location2][1]-self.cavelocations[location][1] <= 12:
									self.cavelocations[location] = None
							else: #cave location is same as location2
								self.cavelocations[location] = None
						elif self.cavelocations[location][0] < self.cavelocations[location2][0]:
							if self.cavelocations[location][1] > self.cavelocations[location2][1]:
								if self.cavelocations[location2][0]-self.cavelocations[location][0] <= 12 and self.cavelocations[location][1]-self.cavelocations[location2][1] <= 12:
									self.cavelocations[location] = None
							elif self.cavelocations[location][1] < self.cavelocations[location2][1]:
								if self.cavelocations[location][0]-self.cavelocations[location2][0] <= 12 and self.cavelocations[location2][1]-self.cavelocations[location][1] <= 12:
									self.cavelocations[location] = None
							else: #cave location is same as location2
								self.cavelocations[location] = None

		if None in self.cavelocations:
			return(1)
		return(0)
			
	def grow_caves(self):
		random.seed()
		for cavenum,cave in enumerate(self.cavelocations):
			size = random.randrange(40,65)
			room = [cave[0],cave[1]]
			self.matrix[cave[0]][cave[1]].roomtype = "cave"
			self.matrix[cave[0]][cave[1]].cavenum = cavenum
			roomlist = []
			roomlist.append([cave[0],cave[1]])
			roomcount = 1
			for tries in range(15):
				while roomcount <= size:
					direction = random.randrange(0,4)
					if self.matrix[room[0]][room[1]].roomtype == "cave":
						if direction == 0:
							if room[1]+2 <= self.height-1:
								if (self.matrix[room[0]][room[1]+2].cavenum == None or self.matrix[room[0]][room[1]+2].cavenum == cavenum):
									if self.matrix[room[0]][room[1]+1].roomtype == None:
										self.matrix[room[0]][room[1]+1].roomtype = "cave"
										self.matrix[room[0]][room[1]+1].cavenum = cavenum
										roomlist.append([room[0],room[1]+1])
										roomcount += 1
						elif direction == 1:
							if room[0]+2 <= self.width-1:
								if (self.matrix[room[0]+2][room[1]].cavenum == None or self.matrix[room[0]+2][room[1]].cavenum == cavenum):
									if self.matrix[room[0]+1][room[1]].roomtype == None:
										self.matrix[room[0]+1][room[1]].roomtype = "cave"
										self.matrix[room[0]+1][room[1]].cavenum = cavenum
										roomlist.append([room[0]+1,room[1]])
										roomcount += 1
						elif direction == 2:
							if room[1]-2 >= 0:
								if (self.matrix[room[0]][room[1-2]].cavenum == None or self.matrix[room[0]][room[1-2]].cavenum == cavenum):
									if self.matrix[room[0]][room[1]-1].roomtype == None:
										self.matrix[room[0]][room[1]-1].roomtype = "cave"
										self.matrix[room[0]][room[1]-1].cavenum = cavenum
										roomlist.append([room[0],room[1]-1])
										roomcount += 1
						elif direction == 3:
							if room[0]-2 >= 0:
								if(self.matrix[room[0]-2][room[1]].cavenum == None or self.matrix[room[0]-2][room[1]].cavenum == cavenum):
									if self.matrix[room[0]-1][room[1]].roomtype == None:
										self.matrix[room[0]-1][room[1]].roomtype = "cave"
										self.matrix[room[0]-1][room[1]].cavenum = cavenum
										roomlist.append([room[0]-1,room[1]])
										roomcount += 1
					seed = random.randrange(0,roomcount)
					room = roomlist[seed]

				for x in range(1, self.width-1):
					for y in range(1, self.height-1):
						if self.matrix[x][y].roomtype == None and sum(self.matrix[x+a][y+b].cavenum == cavenum for (a,b) in [(0,1), (0, -1), (1, 0), (-1, 0)]) >= 3:
							self.matrix[x][y].roomtype = "cave"
							self.matrix[x][y].cavenum = cavenum
							roomlist.append([x,y])
				self.caves.append(Cave(cavenum,roomlist))
				if roomcount >= size:
					break
				continue
		print(self.caves)
		return

	def spawn_caves(self,numcaves):
		random.seed()
		for cnum in range(numcaves):
			x = random.randrange(0,self.width)
			y = random.randrange(0,self.height)
			self.cavelocations.append([x,y])
		spread = self.test_cave_spread()
		if spread == 0:
			self.grow_caves()
		else:
			return(1)

		print(self.caves)
		for x in range(numcaves-1):
			self.link_caves(self.caves[x],self.caves[x+1])
		return(0)

	def link_caves(self,cave1,cave2):
		tunnelstart = None

		if cave1.get_westmost()[0] < cave2.get_eastmost()[0]:
			xdir = "east"
			xstart = cave1.get_eastmost()
			xend = cave2.get_westmost()
		elif cave1.get_eastmost()[0] > cave2.get_westmost()[0]:
			xdir = "west"
			xstart = cave1.get_westmost()
			xend = cave2.get_eastmost()
		elif cave1.get_westmost()[0] > cave2.get_eastmost()[0] and cave1.get_eastmost()[0] < cave2.get_westmost()[0]:
			tunnelstart = "y"
			xdir = "none"
			xstart = cave1.get_westmost()[0]
			xend = cave2.get_eastmost()[0]
		else:
			tunnelstart = "y"
			xdir = "none"
			xstart = None
			xend = None
		if cave1.get_northmost()[1] < cave2.get_southmost()[1]:
			ydir = "north"
			ystart = cave1.get_northmost()
			yend = cave2.get_southmost()
		elif cave1.get_northmost()[1] > cave2.get_southmost()[1]:
			ydir = "south"
			ystart = cave1.get_southmost()
			yend = cave2.get_northmost()
		elif cave1.get_northmost()[1] > cave2.get_southmost()[1] and cave1.get_northmost()[1] < cave2.get_southmost()[1]:
			tunnelstart = "x"
			ydir = "south"
			ystart = cave1.get_southmost()
			yend = cave2.get_northmost()
		else:
			tunnelstart = "x"
			ydir = "none"
			ystart = None
			yend = None
			ylength = 0
		ycount = 0
		xcount = 0
		xlength = 0
		ylength = 0
		if tunnelstart == "x":
			currentroom = xstart
			if xdir == "east":
				xlength = xend[0] - xstart[0]
				# this nest block deals with a bug where we sometimes get negative east values... cheap hack
				if xlength < 0:
					xlength = xlength * -1
					xdir = "west"
			elif xdir == "west":
				xlength = xstart[0] - xend[0]
			else:
				xlength = 0
			if ydir == "north":
				ylength = xend[1] - xstart[1]
			elif ydir == "south":
				ylength = xstart[1] - xend[1]
				if ylength < 0:
					ylength = ylength * -1
					ydir = "north"
			else:
				ylength = 0	
		elif tunnelstart == "y":
			currentroom = ystart
			if xdir == "east":
				xlength = yend[0] - ystart[0]
				# this nest block deals with a bug where we sometimes get negative east values... cheap hack
				if xlength < 0:
					xlength = xlength * -1
					xdir = "west"
			elif xdir == "west":
				xlength = ystart[0] - yend[0]
			else:
				xlength = 0
			if ydir == "north":
				ylength = yend[1] - ystart[1]
			elif ydir == "south":
				ylength = ystart[1] - yend[1]
				if ylength < 0:
					ylength = ylength * -1
					ydir = "north"
			else:
				ylength = 0
		else:
			cave1xory = random.randrange(2)
			if cave1xory == 0:
				currentroom = xstart
				if xdir == "east":
					# this next block deals with a bug where we sometimes get negative east values... cheap hack
					xlength = xend[0] - xstart[0]
					if xlength < 0:
						xlength = xlength * -1
						xdir = "west"
				elif xdir == "west":
					xlength = xstart[0] - xend[0]
				else:
					xlength = 0
				if ydir == "north":
					ylength = xend[1] - xstart[1]
				elif ydir == "south":
					ylength = xstart[1] - xend[1]
					if ylength < 0:
						ylength = ylength * -1
						ydir = "north"
				else:
					ylength = 0

			else:
				currentroom = ystart
				if xdir == "east":
					# this next block deals with a bug where we sometimes get negative east values... cheap hack
					xlength = yend[0] - ystart[0]
					if xlength < 0:
						xlength = xlength * -1
						xdir = "west"
				elif xdir == "west":
					xlength = ystart[0] - yend[0]
				else:
					xlength = 0
				if ydir == "north":
					ylength = yend[1] - ystart[1]
				elif ydir == "south":
					ylength = ystart[1] - yend[1]
					if ylength < 0:
						ylength = ylength * -1
						ydir = "north"
				else:
					ylength = 0

		while xcount < xlength and ycount < ylength:
			xory = random.randrange(0,2)
			if xory == 0:
				if xdir == "east":
					xcount += 1
					if self.matrix[currentroom[0]+1][currentroom[1]].roomtype != "cave":
						self.matrix[currentroom[0]+1][currentroom[1]].roomtype = "tunnel"
					currentroom = [currentroom[0]+1,currentroom[1]]
				elif xdir == "west":
					xcount += 1
					if self.matrix[currentroom[0]-1][currentroom[1]].roomtype != "cave":
						self.matrix[currentroom[0]-1][currentroom[1]].roomtype = "tunnel"
					currentroom = [currentroom[0]-1,currentroom[1]]
			elif xory == 1:
				if ydir == "north":
					ycount += 1
					if self.matrix[currentroom[0]][currentroom[1]+1].roomtype != "cave":
						self.matrix[currentroom[0]][currentroom[1]+1].roomtype = "tunnel"
					currentroom = [currentroom[0],currentroom[1]+1]
				elif ydir == "south":
					ycount += 1
					if self.matrix[currentroom[0]][currentroom[1]-1].roomtype != "cave":
						self.matrix[currentroom[0]][currentroom[1]-1].roomtype = "tunnel"
					currentroom = [currentroom[0],currentroom[1]-1]
		while xcount < xlength:
			if xdir == "east":
				xcount += 1
				if self.matrix[currentroom[0]+1][currentroom[1]].roomtype != "cave":
					self.matrix[currentroom[0]+1][currentroom[1]].roomtype = "tunnel"
				currentroom = [currentroom[0]+1,currentroom[1]]
			elif xdir == "west":
				xcount += 1
				if self.matrix[currentroom[0]-1][currentroom[1]].roomtype != "cave":
					self.matrix[currentroom[0]-1][currentroom[1]].roomtype = "tunnel"
				currentroom = [currentroom[0]-1,currentroom[1]]
		while ycount < ylength:
			if ydir == "north":
				ycount += 1
				if self.matrix[currentroom[0]][currentroom[1]+1].roomtype != "cave":
					self.matrix[currentroom[0]][currentroom[1]+1].roomtype = "tunnel"
				currentroom = [currentroom[0],currentroom[1]+1]
			elif ydir == "south":
				ycount += 1
				if self.matrix[currentroom[0]][currentroom[1]-1].roomtype != "cave":
					self.matrix[currentroom[0]][currentroom[1]-1].roomtype = "tunnel"
				currentroom = [currentroom[0],currentroom[1]-1]
