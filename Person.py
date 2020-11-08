import random
import itertools

class Person():
    def __init__(self, config, illnessStage, preventions, agreeIcolation, selfDiscipline):
        self.type = config['type']
        self.defaultActivity = config['defaultActivity']
        self.fixedActivity = list(config['fixedActivity'].items())
        self.fixedActivity.sort(key=lambda a: isinstance(a[1], tuple), reverse=True) # make sure the fix-term activities are in front
        self.flexActivity = list(config['flexActivity'].items())
        self.illnessStage = illnessStage
        self.illnessStage_course = 0
        self.preventions = preventions
        self.agreeIcolation = agreeIcolation
        self.selfDiscipline = selfDiscipline
        self.closeContacts = []
        self.linkedPlace = {}
        self.currentPlace = None
        self.receivedVirousDoes = 0
        self.reportTag = ''
        self.inIsolation = -1 # -1 means not in isolation

    def emptySchedule(self):
        self.schedule = [(self.defaultActivity,'fixed')] * 16 # 16 hours active hours per day

    def newSchedule(self):
        schedule = [None] * 16 # 16 hours active hours per day

        # step 1: add fixed activities in the schedule
        for activityType, time in self.fixedActivity:
            if isinstance(time, tuple):
                startTime = time[0] - 9 # the start time of a day is 9
                endTime = time[1] - 9
            else:
                startTime = self.getFreeSlotId(schedule, time)
                endTime = startTime + time
            schedule[startTime:endTime] = [(activityType,'fixed')] * (endTime-startTime)

        # step 2: add flex activities in the schedule
        random.shuffle(self.flexActivity)
        for activityType, (duration, probability) in self.flexActivity:
            if random.random()<probability:
                # do the activity
                slotId = self.getFreeSlotId(schedule, duration)
                if slotId is not None:
                    schedule[slotId:slotId+duration] = [(activityType,'flex')] * duration

        # step 3: fill remaining slots with the defaultActivity
        schedule = [activity if activity is not None else (self.defaultActivity,'fixed') for activity in schedule]
        self.schedule = schedule

        # step 4: rewrite the schedule if being in isolation
        if self.agreeIcolation and self.inIsolation >= 0:
            self.schedule = [activity if random.random()>self.selfDiscipline else (None,'isolating') for activity in schedule]
            pass


    def getFreeSlotId(self, schedule, duration):
        # find a random free slot in the given schedule.
        # if the schedule is full, just return the input schedule.
        freeSlots = []
        for hourId in range(len(schedule)-duration):
            # find the first availabe timeslot
            if not any(schedule[hourId:hourId+duration]):
                freeSlots.append(hourId)
        if len(freeSlots)==0:
            return None # no availabe time slot
        slotId = 0
        # randomly skip few slots (to simulate people may have a rest before next activity)
        for _ in range(len(freeSlots)-1):
            if random.random()<0.7:
                break
            slotId += 1
        return freeSlots[slotId]

    def fixedActivityTypes(self):
        return [activity for activity,_ in self.fixedActivity]

    def __repr__(self):
        return f"{self.type}:"