import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import random
import Encounter

class RootDisplay(BoxLayout):


    def __init__(self):
        super(RootDisplay, self).__init__()
        self.listOfPlayers = []

    def add_player(self):
        level = self.player_level.text
        self.listOfPlayers.append(level)
        self.playerList.text = str(self.listOfPlayers)

    def remove_player(self):
        if not len(self.listOfPlayers) == 0:
            self.listOfPlayers.pop()
            self.playerList.text = str(self.listOfPlayers)

    def update_num_monsters(self):
        self.numMonsters.text = "Number of Monsters: " + str(self.slider1.value)

    def update_difficulty(self):
        diff = int(self.slider2.value)
        output = ''
        if diff == 0:
            output = "Easy"
        elif diff == 1:
            output = "Medium"
        elif diff == 2:
            output = "Hard"
        else:
            output = "Deadly"

        self.difficulty.text = "Difficulty: " + output



    def call_encounter_builder(self):
            myEncounter = Encounter.Encounter()
            # levels = ["8", "8", "10", "6"]
            difficulty = 3   # 0-3 Easy, Medium, Hard, Deadly
            size = self.slider1.value          # Exact number of desired monsters
            onlyOfType = []
            output = myEncounter.builder(self.listOfPlayers, int(self.slider2.value), size, onlyOfType)
            self.random_label.text = str(output)

class EncounterBuilder(App):

    def build(self):
        return RootDisplay()


myEncounter = EncounterBuilder()
myEncounter.run()
