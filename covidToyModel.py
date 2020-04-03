# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 13:59:55 2020

@author: bsundheimer
"""
from diseaseModel import *
import matplotlib.pyplot as plt

import random
import numpy as np
from enum import Enum
import matplotlib.animation as animation
from celluloid import Camera


timeMultiplier = 24

covid19 = disease(transmissionProbability = 0.02, 
                  latentTime = 7*timeMultiplier, 
                  mortalityRate = 0.032, 
                  recoveryTime = 14*timeMultiplier, 
                  mortalityTime = 8*timeMultiplier, 
                  transmissionDistance = 6,
                  contageousTime = 4*timeMultiplier)

def getNewPerson(isSick, cityDiameter):
    if(isSick):
        defaultPerson = person(movementRate = 2,
                                    hygene = 0.75,                                   
                                    tested = False,
                                    socialDistancing = False,
                                    quaranteened = False,
                                    quaranteenComplyRate = 0.60,)
        defaultPerson.disease = covid19
        defaultPerson.disease.contractedTimeStep = 0
        defaultPerson.status = Status.sickNoSymptoms
        
    else:
        defaultPerson = person(movementRate = 2,
                                    hygene = 0.75,
                                    quaranteenComplyRate = 0.60,
                                    tested = False,
                                    socialDistancing = False,
                                    quaranteened = False)
    defaultPerson.position = np.asarray([random.random() * cityDiameter, random.random() * cityDiameter])

    return defaultPerson


louisville = city(gravityWell = None,
                    quaranteenArea = None,
                    cityDiameter = 100,
                    travelProbability = 0,
                    startingPopulationSize = 500,
                    quaranteenComplyRate = 1.0,
                    currentGuidance = None,
                    socialDistanceSize = 10                                        
                    )

#setup population
for i in range(0, louisville.startingPopulationSize-1):
    louisville.population.append(getNewPerson(False, louisville.cityDiameter))
louisville.population.append(getNewPerson(True, louisville.cityDiameter))

runTime = 100*timeMultiplier
sickNow = np.zeros(runTime)
removed = np.zeros(runTime)
removedPlot = np.zeros(runTime)
susceptible = np.zeros(runTime)
fig = plt.figure()
camera = Camera(fig)

for i in range(0,runTime):

    locxhealthy = []
    locyhealthy = []
    locxsick = []
    locysick = []
    for dude in louisville.population:
        if dude.status == Status.notSick:
            locxhealthy.append(dude.position[0])
            locyhealthy.append(dude.position[1])
        else:
            locxsick.append(dude.position[0])
            locysick.append(dude.position[1])

    
    louisville.iterateTimeCycle()
    sickNow[i] = louisville.sickNow
    removed[i] = louisville.deadCount + louisville.recoveredCount
    susceptible[i] = louisville.startingPopulationSize - sickNow[i] - removed[i]
    removedPlot[i] = louisville.startingPopulationSize - removed[i]
    if i%24==0:
        print("Timestep = ", i)
        #plt.axis([0,100,0,100])
        plt.scatter(locxhealthy, locyhealthy,c='b')
        plt.scatter(locxsick, locysick,c='r')
        plt.show()
    if len(louisville.population) == 0:
        break


#animation = camera.animate(interval=24)
#animation.save('celluloid_minimal.gif', writer = 'imagemagick')

plt.plot(sickNow)
plt.plot(removedPlot)
#plt.plot(susceptible)
plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    