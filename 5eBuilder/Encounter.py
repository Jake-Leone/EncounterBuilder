import csv
import random
import itertools


class Encounter:

    def __init__(self):
        self.monsters = {}
        self.names = []
        self.playerxp = {}
        self.xpvalues = []  # list of tuples of the form (xp, list of monsters of that xp value)
        self.xps = []  # list of xps that are in xpvalues
        # Read in monster data from csv file
        with open('ids.csv', newline='') as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                # Modify data before creating an entry in monsters
                name = row[0]
                size = row[1]
                type = row[2]
                tags = row[3]
                alignment = row[4]
                # Parse alignment information
                if alignment == '':
                    alignment = "N"
                if "Any evil" in alignment or "Any non-good" in alignment:
                    alignment = "AE"
                elif "Any good" in alignment or "Any non-evil" in alignment:
                    alignment = "AG"
                elif "Unaligned" in alignment:
                    alignment = "N"
                elif "Any" in alignment:
                    alignment = "N"
                elif "or" in alignment:
                    alignment = "N"
                # print(alignment)
                challenge = row[5]
                experience = row[6]
                source = row[7]

                # Create monster entry
                self.names.append(name)
                self.monsters[name] = {}
                self.monsters[name]["size"] = size
                self.monsters[name]["type"] = type
                self.monsters[name]["tags"] = tags
                self.monsters[name]["alignment"] = alignment
                self.monsters[name]["challenge"] = challenge
                self.monsters[name]["experience"] = experience
                self.monsters[name]["source"] = source

                inserted = False
                for value in self.xpvalues:
                    if value[0] == int(experience):
                        value[1].append(name)
                        inserted = True
                if not inserted:
                    self.xpvalues.append((int(experience), [name]))

            for value in self.xpvalues:
                self.xps.append(value[0])
            # print(self.xps)
            # print(self.xpvalues)
            # print(self.monsters[self.names[0]])

        # Import WOTC data on challenge rating experience limits based on player levels
        with open('playerxp.csv', newline='') as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                level = row[0]
                easy = row[1]
                medium = row[2]
                hard = row[3]
                deadly = row[4]
                self.playerxp[level] = {}
                self.playerxp[level][0] = easy
                self.playerxp[level][1] = medium
                self.playerxp[level][2] = hard
                self.playerxp[level][3] = deadly
        # print(self.playerxp['1'])

        return

    # Produce a subset of potential monsters limited to a list of types (ex. Humanoids, Dragons, etc.)
    def getAvailableMonsters(self, types):
        available_monsters = {}
        for key in self.monsters.keys():
            if self.monsters[key]["type"] in types:
                available_monsters[key] = self.monsters[key]
        return available_monsters

    def getXPValues(self, monsters):
        xp_values = [] # List of tuples of the form (xp, list of monster names of that xp value)

        for key in monsters.keys():
            mob = monsters[key]

            inserted = False
            for value in xp_values:
                if value[0] == int(mob["experience"]):
                    value[1].append(key)
                    inserted = True
            if not inserted:
                xp_values.append((int(mob["experience"]), [key]))

        return xp_values


    def builder(self, levels, difficulty, size, types):

        # Limit monsters to just those of certain types
        print("CREATING AN ENCOUNTER")
        print("PLAYER LEVELS: " + str(levels))
        print("---------------------\n\n")

        if len(types) == 0:
            available_monsters = self.monsters
        else:
            available_monsters = self.getAvailableMonsters(types)

        if len(available_monsters) == 0:
            print("THERE ARE NO MONSTERS OF THE SELECTED TYPES")
            return

        xp_values = self.getXPValues(available_monsters)
        xps = []
        for value in xp_values:
            xps.append(value[0])


        #Calculate the xp thresholds for this encounter
        minimumThreshold = 0
        maximumThreshold = 0
        for lev in levels:
            minimumThreshold = minimumThreshold + int(self.playerxp[lev][difficulty])

            upDifficulty = difficulty + 1

            if upDifficulty < 4:
                maximumThreshold = maximumThreshold + int(self.playerxp[lev][upDifficulty])
            else:
                maximumThreshold = minimumThreshold * 2 # Arbitrarily set cap of deadly encounters to twice the floor.
                # We don't want our level 2 party fighting an Ancient Red Dragon
        print("MINIMUM XP TOTAL: " + str(minimumThreshold))
        print("MAXIMUM XP TOTAL: " + str(maximumThreshold))


        xpList = self.newEncounter(minimumThreshold, maximumThreshold, size, xps)
        if xpList is not None:
            officialMonsters = []
            for value in xpList:
                candidates = []
                for lists in xp_values:
                    if lists[0] == value:
                        candidates = lists[1]
                        # Weight chances so that monsters already in the encounter are likely to repeat
                        groups = []

                        for candidate in candidates:
                            if candidate in officialMonsters:
                                groups.append(candidate)

                        if len(groups) == 0:
                            officialMonsters.append(random.choice(candidates))
                        else:
                            roll = random.randint(1, 11)
                            if roll < 9:
                                officialMonsters.append(random.choice(groups))
                            else:
                                officialMonsters.append(random.choice(candidates))

            print(officialMonsters)
            return officialMonsters



    def newEncounter(self, lowerBound, upperBound, numMonsters, xps):
        values = xps.copy()
        currentUpper = upperBound

        foundEncounter = False

        currentTotalXP = 0
        currentEncounter = []
        while not foundEncounter:
            #print("Current Encounter: " + str(currentEncounter))
            #print("Current Total XP: " + str(currentTotalXP))
            # Remove all monsters that would put us over upperBound if they were added
            i = 0
            #print(values)
            while i < len(values):
                adjustedValue = values[i] * self.calculate_modifer(numMonsters)
                if values[i] == 0 or (adjustedValue + currentTotalXP) > upperBound or (adjustedValue + currentTotalXP + (numMonsters - (len(currentEncounter) + 1)) * values[0] * self.calculate_modifer(numMonsters)) > upperBound:
                    # Remove 0 xp mobs
                    # Remove mobs who would immediately put us over the limit
                    # Remove mobs who would practically put us over the limit since choosing the
                    # lowest possible value each time after this would put us over the limit
                    values.pop(i)
                    i = i - 1
                i = i + 1
            #print(values)
            #print()
            if len(values) == 0:
                print("EXCEEDED MAXIMUM LIMIT")
                return None

            # If one monster left to add. Let's make sure we meet the min and max requirements
            if len(currentEncounter) == numMonsters-1:
                i = 0
                while i < len(values):
                    if values[i] * self.calculate_modifer(numMonsters) + currentTotalXP < lowerBound:
                        values.pop(i)
                        i = i - 1
                    i = i + 1
                if len(values) == 0:
                    print("DID NOT MEET MINIMUM REQUIREMENTS")
                    return None
                else:
                    currPick = random.choice(values)
                    currentEncounter.append(currPick)
                    currentTotalXP = currentTotalXP + currPick * self.calculate_modifer(numMonsters)
                    foundEncounter = True
                    break
            else:
                # 2 or more monsters left to add
                currPick = random.choice(values)
                if currPick * self.calculate_modifer(numMonsters) + currentTotalXP:
                    currentTotalXP = currentTotalXP + currPick * self.calculate_modifer(numMonsters)
                    currentEncounter.append(currPick)

                    currentUpper = currentUpper - currPick * self.calculate_modifer(numMonsters)

                else:
                    continue
        print(currentEncounter)
        return currentEncounter

    # isPractical simply looks to see in O(1) time if there is a way to beat the lowerBound and a way to
    # stay under the upperBound.
    # Note: The function is useful to weed out defunct cases; however, it does not guarantee there is a
    # path to meet lowerBound <= total <= upperBound
    def isPractical(self, currentTotal, value, values, currentPosition, numMonsters, lowerBound, upperBound):
        if currentTotal + (value + (values[0] * (numMonsters-(currentPosition-1)))) * self.calculate_modifer(numMonsters) > upperBound:
            return False
        elif currentTotal + (value + (values[len(values)-1] * (numMonsters-(currentPosition-1)))) * self.calculate_modifer(numMonsters) < lowerBound:
            return False
        return True

    def calculate_modifer(self, size):
        if size == 1:
            return 1
        elif size == 2:
            return 1.5
        elif size < 7:
            return 2
        elif size < 11:
            return 2.5
        elif size < 15:
            return 3
        else:
            return 4

'''
myEncounter = Encounter()
levels = ["8", "8", "10", "6"]
difficulty = 3   # 0-3 Easy, Medium, Hard, Deadly
size = 3          # Exact number of desired monsters
onlyOfType = ["Undead", "Construct"]
# myEncounter.craft_encounter(levels, difficulty, size)
myEncounter.builder(levels, difficulty, size, onlyOfType)'''
