import time

from MedicalModel import MedicalEstimationModel
from Simulator import Simulator
from Displayer import Displayer


# from Configuration_baseline import * # baseline settings
# from Configuration_2m import * # 2m social distance only 
# from Configuration_mask import * # mask only 
# from Configuration_isolation import * # isolation only (almost ideal situation)
from Configuration_reallife import * # mask only 

medicalModel = MedicalEstimationModel(medicalAssumptions, illnessStages, config_preventions)
city = Simulator(config_places, config_crowd, config_isolation, config_preventions, medicalModel)
    
displayer = Displayer(city, medicalModel, config_isolation, config_preventions, log="log.txt", showDetails=True)

for epoch in range(365):
    city.runADay()
    time.sleep(1)
    displayer.update()

pass
