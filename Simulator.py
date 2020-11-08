import math
import random
import itertools

from Person import Person
from Place import Place

from MedicalModel import MedicalEstimationModel

class Simulator():
    def __init__(self, config_places, config_crowd, config_isolation, config_preventions, medicalModel):
        self.config_places = config_places
        self.config_crowd = config_crowd
        self.config_isolation = dict(config_isolation.items())
        self.enableIsolation = self.config_isolation['enable']
        if not self.enableIsolation:
            self.config_isolation['agreeIsolationRate'] = 0
        self.config_preventions = config_preventions
        self.medicalModel = medicalModel
        self.flexPlaces = {}
        self.day = 0

        # step 1: create citizens
        self.crowd = []
        for config in config_crowd:
            for i in range(config['number']):
                healthStage = self.medicalModel.initIllnessStage if i < config['patient'] else self.medicalModel.healthStage
                prevention = [preventionType for preventionType, config in config_preventions.items() if random.random() < config['applicationRatio']]
                newPerson = Person(config, healthStage, prevention, random.random()<config_isolation['agreeIsolationRate'], config_isolation['selfDiscipline']) 
                self.crowd.append(newPerson)
        self.population = self.crowd.copy()
        random.shuffle(self.crowd)

        # step 2: create (fixed) locations
        self.fixedPlaces = {}
        for config in config_places:
            if config['number'] is None: continue
            self.fixedPlaces[config['type']] = [ Place(config) for i in range(config['number']) ]
        
        # step 3: randomly link people with fixed locations according to the 'fixedActivity'
        allPossibleDefaultPlaceTypes = [person.defaultActivity for person in self.crowd]
        allPossibleFixedPlaceTypes = itertools.chain(*[person.fixedActivityTypes() for person in self.crowd], allPossibleDefaultPlaceTypes)
        allPossibleFixedPlaceTypes = set(allPossibleFixedPlaceTypes)
        for placeType in allPossibleFixedPlaceTypes:
            people = [person for person in self.crowd if placeType in person.fixedActivityTypes() or placeType==person.defaultActivity]
            places = [place for place in self.fixedPlaces[placeType]]
            # randomly link the remaining people with places
            allocation = self.randomlyAllocate(people, places)
            for place,person in allocation:
                person.linkedPlace[placeType] = place
                place.linkedPeople.append(person)
    
    def randomlyAllocate(self, people, places, ignoreCapasity=False):
        # random allocate places for people according to the place capacity
        places = [(place, []) for place in places]
        availablePlaces = [place for place in places if place[0].freePosition()>0 and not ignoreCapasity]
        for person in people:
            assert len(availablePlaces) > 0, f"No enough places."
            pickedPlace = random.choice(availablePlaces)
            placeItem, mappingPeople = pickedPlace
            mappingPeople.append(person)
            if len(mappingPeople) >= placeItem.freePosition() and not ignoreCapasity:
                # remove the full place
                availablePlaces.remove(pickedPlace)
        allocation = [[(place,person) for person in mappingPeople] for place, mappingPeople in places]
        return itertools.chain(*allocation)

    def runADay(self):
        random.shuffle(self.crowd)
        for person in self.crowd:
            person.newSchedule()
            person.closeContacts = [[]]+person.closeContacts[:self.config_isolation['retrospectivePeriod']-1] # the first item of person.closeContacts records the last day info
        for hourId in range(16): # 16 hours for activities per day
            self.movePeople(hourId)
            allPlaces = itertools.chain(*self.fixedPlaces.values(), *self.flexPlaces.values())
            for place in allPlaces:
                self.virousSpread(place)
        # adjudgement!
        for person in self.crowd:
            newStage, newStage_course, reportTag = self.medicalModel.changeStage(person.illnessStage, person.illnessStage_course, person.receivedVirousDoes)
            person.illnessStage = newStage
            person.illnessStage_course = newStage_course
            person.receivedVirousDoes = 0
            person.reportTag = reportTag
            if person.inIsolation >= 0:
                person.inIsolation += 1
            if person.inIsolation >= self.config_isolation['isolationPeriod'] and person.illnessStage not in self.medicalModel.riskStages:
                person.inIsolation = -1 
            if newStage in self.config_isolation['realizableStates']:
                # this person just realizes the inflection, trigger the exposure notification!
                exposuredPeople = set(itertools.chain(*itertools.chain(*person.closeContacts)))
                notificationRate = self.config_isolation['notificationRate']
                for exposuredPerson in exposuredPeople:
                    if random.random() < notificationRate:
                        exposuredPerson.inIsolation = 0 # the first day of isolation
                
        # remove corpses
        self.crowd = [person for person in self.crowd if person.illnessStage!=self.medicalModel.deadStage]
        self.day += 1

    def movePeople(self, hourId):
        flexPlaceBuffers = {}
        for person in self.crowd:
            if hourId>0 and person.schedule[hourId] == person.schedule[hourId-1]:
                continue # don't need to move the person
            if person.currentPlace is not None:
                person.currentPlace.removePerson(person)
            activity, type = person.schedule[hourId]
            if type=='isolating':
                person.currentPlace = None
            elif type=='fixed':
                newPlace = person.linkedPlace[activity]
                newPlace.addPerson(person)
                person.currentPlace = newPlace
            else: # type==flex
                buffer = flexPlaceBuffers.setdefault(activity,[])
                buffer.append(person)
        pass
        for placeType, people in flexPlaceBuffers.items():
            if placeType in self.fixedPlaces:
                # if people visit a fixed place as a flex activity, just put them in existing fixed places. (ignore the place capacity)
                currentPlaces = self.fixedPlaces[placeType]
                allocation = self.randomlyAllocate(people, currentPlaces)
            else:
                # people visit flex places
                currentPlaces = self.flexPlaces.setdefault(placeType, [])
                # remore the empty places
                currentPlaces = [place for place in currentPlaces if len(place.currentPeople)==0]
                self.flexPlaces[placeType] = currentPlaces
                placeConfig = [placeConfig for placeConfig in self.config_places if placeConfig['type']==placeType][0]
                singleCapacity = placeConfig['capacity']
                currentPopulation = sum( [len(place.currentPeople) for place in currentPlaces] ) + len(people)
                number_newPlaceRequired = math.ceil(currentPopulation / (singleCapacity*0.75)) - len(currentPlaces)
                if number_newPlaceRequired > 0:
                    # create new places
                    currentPlaces += [Place(placeConfig) for _ in range(number_newPlaceRequired)]
                allocation = self.randomlyAllocate(people, currentPlaces)
            for place,person in allocation:
                place.addPerson(person)
                person.currentPlace = place
                
    def virousSpread(self, place):
        people = list(place.currentPeople)
        # aerosol spreading
        riskPeople = [person for person in people if person.illnessStage in self.medicalModel.riskStages]
        aerosolVirousDoes = sum(self.medicalModel.aerosolSpreadingDoes(person.illnessStage, person.preventions) for person in riskPeople)
        aerosolVirousUnit = aerosolVirousDoes / place.SpaceVolume
        for person in people:
            person.receivedVirousDoes += self.medicalModel.aerosolReceiveDoes(aerosolVirousUnit, person.preventions)
        # face to face spreadig
        for riskPerson in riskPeople:
            for _ in range(place.ContactFrequency):
                targetPerson = random.choice(people)
                dropletVirousDoes = self.medicalModel.dropletReceiveDoes(riskPerson.illnessStage, riskPerson.preventions, targetPerson.preventions, place.maximumDistanceLimit)
                targetPerson.receivedVirousDoes += dropletVirousDoes
        # record close contacts
        for person in people:
            person.closeContacts[0].append(people) # the first item of person.closeContacts records the last day info
            pass

