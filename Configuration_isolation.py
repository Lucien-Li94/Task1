
# ========================== Medical Configuration ==========================

medicalAssumptions = {
    'dropletEmissionDoes': 1, # Virus does that a patient can spread in a face to face talk/cough.
    'aerosolEmissionDoes': 0.01, # Virus does that a patient can spread to aerosol per hour.
    # self.halfInfectionDoes and self.quaterInfectionDoes are used for logistic regression
    'halfInfectionDoes': 2, # Receivd virus does that you will get a 50% infection rate (how many times the patient talks/coughs to you).
}

config_isolation = {
    'sign':'۩',
    'enable': True, # whether the settings below are enabled.
    # the behavior configuration of self-isolation and exposure notification
    'realizableStates': ['infection'], # when people get in 'infection' state, the exposure notification will be triggered
    'retrospectivePeriod': 3, # will notify close contacts within 3 days
    'isolationPeriod': 14, # 14 days isolation
    'notificationRate': 1, # 80% notification success ratio
    'agreeIsolationRate': 1, # only 90% people follow the self-isolation rule
    'selfDiscipline': 1, # when people are isolated, they only reduce 90% activates
}

config_preventions = {
    # a person may adopt zero/single/multiple preventions
    'mask': {
        'sign':'M',
        'applicationRatio': 0, # 5% people wearing mask
        'aerosolSpreading': 0.1, # 10% virus spreading to aerosol
        'aerosolReceive': 0.05, # 5% of virus received from aerosol
        'dropletSpreading': 0.1, # 10% of virus spreading via droplet.
        'dropletReceive': 0.05, # 5% of virus received from others droplet.
        'socialDistance': 1, # 1m (default value) is the usuall distance when british talking.
    },
    'socialDistancing': {
        'sign':'D',
        'applicationRatio': 0,
        'aerosolSpreading': 1, # 100% virus spreading to aerosol
        'aerosolReceive': 1, # 100% of virus received from aerosol
        'dropletSpreading': 1, # 100% of virus spreading via droplet.
        'dropletReceive': 1, # 100% of virus received from others droplet.
        'socialDistance': 2, # 2m
    },
    'touchOften': {
        'sign':'ᕗ',
        'applicationRatio': 0, # nobody adopt this method
        'aerosolSpreading': 1, # 100% virus spreading to aerosol
        'aerosolReceive': 1.2, # 120% of virus received from aerosol
        'dropletSpreading': 1, # 100% of virus spreading via droplet.
        'dropletReceive': 1.2, # 120% of virus received from others droplet.
        'socialDistance': 1, 
    }
}

illnessStages = {
    'initStage': 'incubation1',
    'recoveryStage': 'recovery',
    'deadStage': 'dead',

    'stages': {
        'incubation1': { 
            # initial incubation period, which does not spread virus
            'duration': (1, 3), # from 1 to 3 days
            'virusWeight': 0, # no virus spread
            'dropletSpreadingFrequency': 0, # no droplet.
            'nextState': [
                ('incubation2', 1), # 100% go to stage incubation2
            ],
        },
        'incubation2': { 
            # usual incubation period, which does spread virus
            'duration': (2, 5), 
            'virusWeight': 0.3, # 30% capability for virus spreading
            'dropletSpreadingFrequency': 1, # 1 time droplet. per hour
            'nextState': [
                ('asymptomaticInfection', 0.3), # 10% go to stage asymptomatic infection
                ('infection', 0.7), # 90% go to stage infection
            ]
        },
        'asymptomaticInfection': { 
            # initial incubation period, which does spread virus
            'duration': (6, 12), 
            'virusWeight': 0.8,
            'dropletSpreadingFrequency': 10, # 10 times droplet. per hour
            'nextState': [
                ('recovery', 0.99), # 
                ('dead', 0.01), # 
            ]
        },
        'infection': { 
            # initial incubation period, which does spread virus
            'duration': (7, 14), 
            'virusWeight': 1, 
            'dropletSpreadingFrequency': 40, # 40 times droplet. per hour
            'nextState': [
                ('recovery', 0.95), # 
                ('dead', 0.05), # 
            ]
        },
    }
}


# ========================== Social Configuration ==========================

config_places = [
    {
        'type': 'Home',

        'SpaceVolume': 160, # cubic meter -- considering the average sizes and ventilation of the UK homes
        'ContactFrequency': 4, # The number of conversations per person per hour
        'maximumDistanceLimit': 5, # meter
        'capacity': 5, # the number of people that each this kind of place can hold (min, max)
        'number': 400, # the number of homes in total
    },
    {
        'type': 'Market',
        
        'SpaceVolume': 2000, 
        'ContactFrequency': 1, 
        'maximumDistanceLimit': 10,
        'capacity': 100,
        'number': 1,
    },
    {
        'type': 'Transport',
        
        'SpaceVolume': 50, 
        'ContactFrequency': 1, 
        'maximumDistanceLimit': 1,
        'capacity': 20,
        'number': None, # flexible number
    },
    {
        'type': 'Office',
        
        'SpaceVolume': 80, 
        'ContactFrequency': 20, 
        'maximumDistanceLimit': 10,
        'capacity': 30,
        'number': 60,
    },
    {
        'type': 'School',
        
        'SpaceVolume': 80, 
        'ContactFrequency': 10, 
        'maximumDistanceLimit': 2,
        'capacity': 20,
        'number': 25, # 25 classes
    },
    {
        'type': 'Club',
        
        'SpaceVolume': 200, 
        'ContactFrequency': 20, 
        'maximumDistanceLimit': 0.5,
        'capacity': 150,
        'number': None, # flexible number of roomes
    },
]

config_crowd = [
    {
        'type': 'Aged',

        'defaultActivity': 'Home', # the default activity is stay at home.
        'fixedActivity':{
            # 16 hours activity per day
            # the activities that the person must do
            # fixedActivity -- people go to fixed places to do the activity (i.e. a person has a fixed home)
            # 'Home' : 12, # hours
        },
        'flexActivity':{
            # 16 hours activity per day
            # the activities that the person might do if there are free hours
            # flexActivity -- people go to random places to do the activity (i.e. a person can go different clubs)
            'Market': (1, 0.5), # this activity lasts 1 hour, and the probability to do so is 0.5 each day
            'Transport': (1, 0.33),
        },
        'number': 100,
        'patient': 0,
    },
    {
        'type': 'Officer',

        'defaultActivity': 'Home', 
        'fixedActivity':{
            'Office' : (9, 17) # fixed time, 9:00 - 17:00; daytime starts from 9:00
        },
        'flexActivity':{
            'Market': (1, 0.25), #
            'Transport': (1, 0.9), #
            'Club': (2, 0.05), #
        },
        'number': 500, #
        'patient': 1, #
    },
    {
        'type': 'ShopStaff',

        'defaultActivity': 'Home', 
        'fixedActivity':{
            'Market' : 6, # a 6-hour working period
        },
        'flexActivity':{
            'Office': (1, 0.05), # MarketStaff can go to other offices e.g. city council
            'Transport': (1, 0.9), 
            'Club': (2, 0.2), 
        },
        'number': 20,
        'patient': 0,
    },
    {
        'type': 'Student',

        'defaultActivity': 'Home', 
        'fixedActivity':{
            'School' : (9, 17), 
        },
        'flexActivity':{
            'Office': (1, 0.05), 
            'Transport': (1, 0.9), 
            'Club': (4, 0.4), 
        },
        'number': 500,
        'patient': 1,
    },
]

