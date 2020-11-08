import os
import re
from Person import Person

class Displayer():
    def __init__(self, simulator, medicalModel, config_isolation, config_preventions, log=None, showDetails=False):
        self.simulator = simulator
        self.medicalModel = medicalModel
        self.isolationTag = config_isolation['sign']
        self.preventions = dict((preventionName,config['sign']) for preventionName,config in config_preventions.items())
        self.illnessStages = {
            'healthy': colourText('● healthy', 'White'), 
            'init': colourText('● incubation', 'Yellow'), 
            'sick': colourText('● sick', 'Red'),
            'recovered': colourText('● recovered', 'Cyan'),
            'dead': colourText('● dead', 'DarkGray'),
        }
        self.log = log
        if self.log is not None:
            with open(self.log, 'a') as f:
                heads = 'day', 'population', 'dailyCase', 'dailyDead', 'totalCase', 'totalDead', 'recovered', 'currentPaitent', 'isolation'
                f.write('\n'+'\t'.join(heads)+'\n')
        self.showDetails = showDetails
        self.columnWidth = 16
        self.width = self.columnWidth * 20
        self.totalCase = sum([1 if person.illnessStage==self.medicalModel.initIllnessStage else 0 for person in self.simulator.population])
        self.totalDead = 0
        self.recovered = 0
        self.population = len(simulator.population)

    def update(self):
        peopleState, dailyCase, dailyDead, currentPaitent, isolation = self.renderPeopleState()
        statistics = dailyCase, dailyDead, self.totalCase, self.totalDead, self.recovered, currentPaitent, isolation
        if self.log is not None:
            with open(self.log, 'a') as f:
                f.write(f'{self.simulator.day}\t{self.population}\t')
                f.write('\t'.join([str(data) for data in statistics])+'\n')
        clearScreen()
        print(makeBar('=', self.width), flush=False)
        self.printLegend()
        print(makeBar('-', self.width), flush=False)
        self.printStatistics(*statistics)
        print(makeBar('-', self.width), flush=False)
        # print details
        if self.showDetails:
            buffer = []
            columnNumber = self.width//self.columnWidth
            for index, personStateText in enumerate(peopleState):
                buffer.append(personStateText+'|')
                if index % columnNumber == columnNumber-1:
                    buffer.append('\n')
            print(''.join(buffer).strip(), flush=False)
            print(makeBar('=', self.width), flush=True)
    
    def renderPeopleState(self):
        peopleState = []
        dailyCase = 0
        totalDead = 0
        recovered = 0
        currentPaitent = 0
        isolation = 0
        for person in self.simulator.population:
            isNewCase = False
            if person.illnessStage==self.medicalModel.healthStage:
                healthStateColour = 'White'
            elif person.illnessStage==self.medicalModel.initIllnessStage:
                healthStateColour = 'Yellow'
                if person.illnessStage_course == 0:
                    isNewCase = True
                    dailyCase += 1
            elif person.illnessStage==self.medicalModel.recoveryStage:
                healthStateColour = 'Cyan'
                recovered += 1
            elif person.illnessStage==self.medicalModel.deadStage:
                healthStateColour = 'DarkGray'
                if person.illnessStage_course == 0:
                    totalDead += 1
            else: # riskStages
                healthStateColour = 'Red'
                currentPaitent += 1
            preventionSigns = [self.preventions[prevention] for prevention in person.preventions]
            personType = colourText(person.type, background='Magenta') if isNewCase else person.type
            sign = '●'
            if self.simulator.enableIsolation and person.inIsolation>=0:
                sign = self.isolationTag
                isolation += 1
                personType = colourText(personType, "Black", background='LightGray')
            stageText = colourText(f' {sign} ', healthStateColour)+personType
            preventionText = colourText(''.join(preventionSigns), "White")
            combinedText = stageText+makeBar(' ',self.columnWidth-getTextLength(stageText)-getTextLength(preventionText)-1)+preventionText
            peopleState.append(combinedText)
        dailyDead = totalDead - self.totalDead
        self.totalDead = totalDead
        self.totalCase +=  dailyCase
        self.recovered = recovered
        return peopleState, dailyCase, dailyDead, currentPaitent, isolation

    def printStatistics(self, dailyCase, dailyDead, totalCase, totalDead, recovered, currentPaitent, isolation):
        statistics = f"Day: {self.simulator.day}   "
        statistics += f"Population: {self.population}   " + "|   "
        statistics += f"Daily Case: {dailyCase}   "
        statistics += f"Daily Dead: {dailyDead}   "
        statistics += f"Total Case: {totalCase}   "
        statistics += f"Total Dead: {totalDead}   " + "|   "
        statistics += f"Recovered: {recovered}   "
        statistics += f"Current Paitent: {currentPaitent}   "
        statistics += f"Isolation: {isolation}   "
        print(statistics)

    def printLegend(self):
        legends = self.illnessStages.values()
        preventions = [f'{preventionName}: {colourText(sign, "White")}' for preventionName,sign in self.preventions.items()]
        text = 'Health State:  '+'    '.join(legends)+'   '+colourText('Daily Case', background='Magenta')+'   '
        text += f'{colourText(f"{self.isolationTag} isolation", "Black", background="LightGray")}   ' + '|   '
        text += 'Preventions:  '+'  '.join(preventions)+'   '
        textLengt = getTextLength(text)
        print(text,makeBar(' ', self.width-textLengt-1),'|',sep='')
        
    
def makeBar(sign, length):
    return ''.join([sign]*length)
    
def getTextLength(text):
    plainText = re.sub(r"\033\[[0-9;]*m",'',text)
    return len(plainText)

def colourText(text, colour='Default', style='Bold', background='Default'):
    styleColour = {
        'Bold': "1",
        'Dim': "2",
        'Underlined': "4",
        'Blink': "5",
        'Reverse': "7",
        'Hidden': "8",

        'ResetBold': "21",
        'ResetDim': "22",
        'ResetUnderlined': "24",
        'ResetBlink': "25",
        'ResetReverse': "27",
        'ResetHidden': "28",
    }[style]
    colourCode = {
        'Default': "39",
        'Black': "30",
        'Red': "31",
        'Green': "32",
        'Yellow': "33",
        'Blue': "34",
        'Magenta': "35",
        'Cyan': "36",
        'LightGray': "37",
        'DarkGray': "90",
        'LightRed': "91",
        'LightGreen': "92",
        'LightYellow': "93",
        'LightBlue': "94",
        'LightMagenta': "95",
        'LightCyan': "96",
        'White': "97",
    }[colour]
    backgroundCode = {
        'Default': "49",
        'Black': "40",
        'Red': "41",
        'Green': "42",
        'Yellow': "43",
        'Blue': "44",
        'Magenta': "45",
        'Cyan': "46",
        'LightGray': "47",
        'DarkGray': "100",
        'LightRed': "101",
        'LightGreen': "102",
        'LightYellow': "103",
        'LightBlue': "104",
        'LightMagenta': "105",
        'LightCyan': "106",
        'White': "107",
    }[background]
    return f"\033[{styleColour};{colourCode};{backgroundCode}m{text}\033[0m"

def clearScreen():
    os.system('clear')



# ========================== Platform compatibility for Windows ==========================
import sys
platform = sys.platform
# windows cannot colour the texts in terminals; also, windows uses cls indtead of clear

if platform=='win32': 
    def colourText_win(text, colour='Default', style='Bold', background='Default'):
        return text
    colourText = colourText_win
    def clearScreenWin():
        os.system('cls')
    clearScreen = clearScreenWin