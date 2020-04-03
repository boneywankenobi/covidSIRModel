# diseaseModel.py
import random
import numpy as np
import math
from enum import Enum
import copy

class Status(Enum):
    notSick = 0
    sickNoSymptoms = 1
    sick = 2
    dead = 3
    recovered = 4

class disease:
    def __init__(self, transmissionProbability, latentTime, mortalityRate, mortalityTime, 
                 recoveryTime, transmissionDistance, contageousTime):    
        self.transmissionProbability = transmissionProbability
        self.latentTime = latentTime
        self.mortalityRate = mortalityRate
        self.mortalityTime = mortalityTime
        self.recoveryTime = recoveryTime
        self.contageousTime = contageousTime
        self.transmissionDistance = transmissionDistance
        self.contractedTimeStep = -1

class person:
    def generateStartingPosition(self):
        self.position = location(random.random(), random.random())

    def __init__(self, movementRate, hygene, tested, socialDistancing, quaranteened, quaranteenComplyRate):
        self.movementRate = movementRate
        self.hygene = hygene
        self.quaranteenComplyRate = quaranteenComplyRate
        self.tested = tested
        self.status = Status.notSick
        self.socialDistancing = socialDistancing
        self.quaranteened = quaranteened
        self.contageous = False
        self.position = np.zeros(2)
        self.removePerson = False
        self.disease = None

    def updatePosition(self, location):
        self.position = location
    
    def getPosition(self):
        return self.position
    
        
class city:
    def __init__(self, gravityWell, quaranteenArea, cityDiameter, travelProbability, 
                  currentGuidance, startingPopulationSize, 
                  quaranteenComplyRate, socialDistanceSize, currentTimestep=0):
        self.gravityWell = gravityWell
        self.quaranteenArea = quaranteenArea
        self.cityDiameter = cityDiameter
        self.travelProbability = travelProbability
        self.currentGuidance = currentGuidance
        self.startingPopulationSize = startingPopulationSize        
        self.quaranteenComplyRate = quaranteenComplyRate
        self.socialDistanceSize= socialDistanceSize
        self.currentTimestep = currentTimestep
        self.totalPopulation = 0
        self.sickNow = 0
        self.sickPresentingSymptoms = 0
        self.recoveredCount = 0
        self.deadCount = 0
        self.totalSick = 0
        self.population = []
        
        
    def iterateTimeCycle(self, newGuidance=None):
        self.currentTimestep += 1
        #Test for proximity
              
        for dude in self.population:
            if dude.contageous and dude.disease.contractedTimeStep != self.currentTimestep:
                for otherDude in self.population:
                    dist = np.linalg.norm(dude.position - otherDude.position)
                    
                    #Propogate new cases
                    if dude.disease.transmissionDistance > dist:                            
                        transmitted = random.random() < (dude.disease.transmissionProbability * otherDude.hygene)
                        if transmitted is True:
                            otherDude.disease = copy.deepcopy(dude.disease)
                            otherDude.disease.contractedTimeStep = self.currentTimestep 
                            self.totalSick += 1
       
        #Move 
        self.sickNow = 0
        self.sickPresentingSymptoms = 0
        
        #Precompute centers for speed
        centers = []
        for dude in self.population:
            centers.append(dude.position)
        for dude in self.population:
            gravityVector = self.getGravityFactor(dude, centers)
            walkAngle = random.random() * 6.28
            walkVector = dude.movementRate * np.asarray([math.cos(walkAngle), math.sin(walkAngle)])
            dude.position += walkVector + gravityVector            
        
            #Upkeep
            #Kill / Recover / Present symptoms
            if dude.disease is not None:
                if self.currentTimestep == 70:
                    print("Current timestep: " , self.currentTimestep , " dude.disease.contractedTimeStep", dude.disease.contractedTimeStep )
                timeSinceContracted = self.currentTimestep - dude.disease.contractedTimeStep  
                if timeSinceContracted < dude.disease.latentTime:
                    dude.status = Status.sickNoSymptoms   
                    self.sickNow += 1
                else:
                    dude.status = Status.sick
                    self.sickNow += 1
                    self.sickPresentingSymptoms += 1
                
                if timeSinceContracted > dude.disease.contageousTime:
                    dude.contageous = True
                
                if timeSinceContracted > dude.disease.mortalityTime:
                    mortalityWindow = dude.disease.recoveryTime - dude.disease.mortalityTime    
                    dead = random.random() < dude.disease.mortalityRate / mortalityWindow
                    if dead:
                        print("He dead")
                        self.deadCount += 1
                        self.population.remove(dude)
                        continue
                if timeSinceContracted > dude.disease.recoveryTime:
                    print("Oh he fine")
                    self.recoveredCount += 1
                    self.population.remove(dude)
                    continue             
    
    def addPerson(self, person):
        self.population.append(person)

    def getGravityFactor(self, person, centers):
        center = person.position
        totalForce = np.zeros(2)
     
        #Wall
        #left
        if person.position[0] < person.movementRate:
            totalForce[0] = person.movementRate
        #right
        if person.position[0] > self.cityDiameter-person.movementRate:
            totalForce[0] = -person.movementRate
        #top
        if person.position[1] < person.movementRate:
            totalForce[1] = person.movementRate
        #bottom
        if person.position[1] > self.cityDiameter-person.movementRate:
            totalForce[1] = -person.movementRate
               
        #Personal Space Gravity
        totalForce += self.socialDistanceSize * self.calculateGravity(center, centers)
        
        return totalForce
    
    def calculateGravity(self, center, centers):
        vdist = center - centers
        
        #+1 needed to stop things less than 1 from blowing up
        ndist = (np.linalg.norm(vdist, axis=1)+1)**3
        vdist = vdist[np.argsort(ndist)[1:10]]
        ndist = ndist[np.argsort(ndist)[1:10]]
        
        gravVec = np.sum(np.divide(vdist, ndist[:,None]), axis=0)
               
        return gravVec

class gravityWell:
    def __init__(self, location, pullProbability, wellDiameter):
        self.location = location
        self.pullProbability = pullProbability
        self.wellDiameter = wellDiameter

class location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class country:
    def __init__(self, cities, guidance):
        self.cities = []
        self.guidance = guidance
    
    def addCity(self, city):
        self.cities.append(city)


class guidance:
    def __init__(self, guidanceGiven, socialDistance, quaranteen, hygene, testingRate):
        self.guidanceGiven = guidanceGiven
        self.socialDistance = socialDistance
        self.quaranteen = quaranteen
        self.hygene = hygene
        self.testingRate = testingRate