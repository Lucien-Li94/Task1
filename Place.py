class Place():
    def __init__(self, config):
        self.type = config['type']
        self.SpaceVolume = config['SpaceVolume']
        self.ContactFrequency = config['ContactFrequency']
        self.maximumDistanceLimit = config['maximumDistanceLimit']
        self.capacity = config['capacity']
        self.currentPeople = []
        self.linkedPeople = []
    
    def addPerson(self, person):
        self.currentPeople.append(person)
    
    def removePerson(self, person):
        self.currentPeople.remove(person)
    
    def freePosition(self):
        return self.capacity - len(self.currentPeople)

    def __repr__(self):
        return self.type