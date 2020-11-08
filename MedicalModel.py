import random
import math
sigmoid = lambda x: 1 / (1 + math.exp(-x))

class MedicalEstimationModel():
    def __init__(self, medicalAssumptions, illnessStages, config_preventions):
        self.illnessStages = illnessStages['stages']
        self.config_preventions = config_preventions
        self.dropletEmissionDoes = medicalAssumptions['dropletEmissionDoes']
        self.aerosolEmissionDoes = medicalAssumptions['aerosolEmissionDoes']
        self.halfInfectionDoes = medicalAssumptions['halfInfectionDoes']

        self.healthStage = ''
        self.initIllnessStage = illnessStages['initStage']
        self.deadStage = illnessStages['deadStage']
        self.recoveryStage = illnessStages['recoveryStage']
        self.riskStages = [stageName for stageName, config in self.illnessStages.items() if config['virusWeight']>0]
    
    def aerosolSpreadingDoes(self, healthStage, preventions):
        virusDoes = self.aerosolEmissionDoes 
        virusDoes *= self.illnessStages[healthStage]['virusWeight'] 
        virusDoes *= self.preventionBias(preventions, 'aerosolSpreading')
        return virusDoes
    def aerosolReceiveDoes(self, aerosolVirousUnit, preventions):
        return aerosolVirousUnit * self.preventionBias(preventions, 'aerosolReceive')
    def dropletReceiveDoes(self, patientHealthStage, patientPreventions, recipientPreventions, placeMaximumDistanceLimit):
        socialDistance = max([self.config_preventions[prevention]['socialDistance'] for prevention in patientPreventions+recipientPreventions], default=1)
        realDistance = min(socialDistance,placeMaximumDistanceLimit)
        virusDoes = self.dropletEmissionDoes 
        virusDoes *= self.illnessStages[patientHealthStage]['virusWeight']
        virusDoes *= self.preventionBias(recipientPreventions, 'dropletSpreading')
        virusDoes *= self.dropletVirusWeight(realDistance)
        virusDoes *= self.preventionBias(recipientPreventions, 'dropletReceive')
        return virusDoes

    def preventionBias(self, preventions, actionType):
        # actionType = aerosolSpreading|aerosolReceive|dropletSpreading|dropletReceive
        virusDoes = 1
        for preventionType in preventions:
            virusDoes *= self.config_preventions[preventionType][actionType]
        return virusDoes

    def infectionProbability(self, virusDoes):
        # the infection rate function is based on the paper:
        # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1690885/  (Figure 1 and Eq 3.4)
        k = 5 # k measures the slope of the sigmoidal curve at halfInfectionDoes
        b = math.pow(virusDoes/self.halfInfectionDoes, k)
        infectionRate = b / (1+b)
        return infectionRate
    
    def dropletVirusWeight(self, distance):
        # the weight of virus does via droplet spreading depends on various situations. see: https://doi.org/10.1016/j.buildenv.2015.06.018
        # here we adopt a sigmoidal function, such that dropletVirusDoes(0)=1, dropletVirusDoes(2)=0.05
        # that is to say, when the distance = 2m, only 5% virus can be passed from the spreader to receiver. 
        b = math.pow(distance,4)
        return 1 - b/(1+b)
    
    def changeStage(self, illnessStage, illnessStage_course, virusDoes):
        # for non-illness stages
        if illnessStage==self.recoveryStage:
            # recovered people cannot be infected
            return illnessStage, illnessStage_course+1, ''
        if illnessStage==self.deadStage:
            return illnessStage, illnessStage_course+1, ''
        if illnessStage==self.healthStage:
            # check if a health person get sack
            getSick = random.random() < self.infectionProbability(virusDoes)
            if getSick:
                return self.initIllnessStage, 0, 'NewCase'
            else:
                return self.healthStage, illnessStage_course+1, ''

        # for illness stages:
        currentStageConfig = self.illnessStages[illnessStage]
        if illnessStage_course >= currentStageConfig['duration'][0]:
            probabilityToChangeStage = 1 / (currentStageConfig['duration'][1]-illnessStage_course)
            changeTonextStateNow = random.random() < probabilityToChangeStage
            if changeTonextStateNow:
                nextProssibleStageNames = [stage[0] for stage in currentStageConfig['nextState']]
                nextProssibleStageWeights = [stage[1] for stage in currentStageConfig['nextState']]
                nextState = random.choices(nextProssibleStageNames,nextProssibleStageWeights,k=1)[0]
                if nextState==self.deadStage:
                    reportTag = 'Dead'
                elif nextState==self.recoveryStage:
                    reportTag = 'Recovered'
                else:
                    reportTag = ''
                return nextState, 0, reportTag
        return illnessStage, illnessStage_course+1, ''


