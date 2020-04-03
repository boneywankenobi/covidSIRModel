# diseaseModel.py
import random
import numpy as np
import math
from enum import Enum
import copy
from scipy.spatial import distance_matrix
from scipy.spatial import distance

class Status(Enum):
    notSick = 0
    sickNoSymptoms = 1
    sick = 2
    dead = 3
    recovered = 4

class disease:
    def __init__(self, transmissionProbability, latentTime, mortalityRate, mortalityTime, 
                 recoveryTime, transmissionDistance, contagiousTime):    
        self.transmissionProbability = transmissionProbability
        self.latentTime = latentTime
        self.mortalityRate = mortalityRate
        self.mortalityTime = mortalityTime
        self.recoveryTime = recoveryTime
        self.contagiousTime = contagiousTime
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
        self.contagious = False
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
        
        #Setup - need to get it into a 1x2 np array.... probably a better way to do it
        centers = self.population[0].position

        centers = np.concatenate((np.transpose(centers[:,None]), np.transpose(self.population[0].position[:,None])))
        list_iterator = iter(self.population)
        try:
            next(list_iterator)
            next(list_iterator)
        except:
            return
        for dude in list_iterator:
            centers = np.concatenate((centers, np.transpose(dude.position[:,None])))
        
        normDistMat = distance_matrix(centers, centers)
        normDistMatscaled = (1+normDistMat)**3
        xDistMat = np.divide(np.subtract(centers[:,0,None],np.transpose(centers[:,0,None])),normDistMatscaled)
        yDistMat = np.divide(np.subtract(centers[:,1,None],np.transpose(centers[:,1,None])),normDistMatscaled)
        
        #TODO: Convert rest of logic into distance matrix
        
        #withinInfectionRadius = normDistMat < transmissionDistance
        infected = np.zeros(len(self.population))
        contagious = np.zeros(len(self.population))
        disease = []
        for i in range(len(self.population)):
            infected[i] = self.population[i].disease is not None
            if(self.population[i].disease is not None):                
                infected[i] = 1
                disease = self.population[i].disease
                contagious[i] = self.population[i].contagious
                     
        diseaseDist = 0
        try:
            diseaseDist = disease.transmissionDistance    
        except:
            return
            
        infectionMap = normDistMat < diseaseDist    
        
        exposedPop = np.dot(infectionMap, contagious)
        
        atRiskPop = np.multiply(exposedPop, np.logical_not(infected))
                
        for i in range(len(self.population)):
            if atRiskPop[i]:
                dude = self.population[i]
                transmitted = random.random() < (disease.transmissionProbability * dude.hygene)
                if transmitted is True:
                    dude.disease = copy.deepcopy(disease)
                    dude.disease.contractedTimeStep = self.currentTimestep 
                    self.totalSick += 1
        
        # for dude in self.population:
        #     if dude.contagious and dude.disease.contractedTimeStep != self.currentTimestep:            
        #         for otherDude in self.population:
        #             if otherDude.disease is not None:
        #                 continue
        #             dist = np.linalg.norm(dude.position - otherDude.position)
                    
        #             #Propogate new cases
        #             if dude.disease.transmissionDistance > dist:                            
        #                 transmitted = random.random() < (dude.disease.transmissionProbability * otherDude.hygene)
        #                 if transmitted is True:
        #                     otherDude.disease = copy.deepcopy(dude.disease)
        #                     otherDude.disease.contractedTimeStep = self.currentTimestep 
        #                     self.totalSick += 1
       
        #Move 
        self.sickNow = 0
        self.sickPresentingSymptoms = 0
        i=0
        for dude in self.population:
            gravityVector = self.getGravityFactor(dude, normDistMat[:,i], xDistMat[:,i], yDistMat[:,i])
            walkAngle = random.random() * 6.28
            walkVector = dude.movementRate * np.asarray([math.cos(walkAngle), math.sin(walkAngle)])
            dude.position += walkVector + gravityVector            
        
            #Upkeep
            #Kill / Recover / Present symptoms
            if dude.disease is not None:
 
                timeSinceContracted = self.currentTimestep - dude.disease.contractedTimeStep  
                if timeSinceContracted < dude.disease.latentTime:
                    dude.status = Status.sickNoSymptoms   
                    self.sickNow += 1
                else:
                    dude.status = Status.sick
                    self.sickNow += 1
                    self.sickPresentingSymptoms += 1
                
                if timeSinceContracted > dude.disease.contagiousTime:
                    dude.contagious = True
                
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
            i+=1

    
    def addPerson(self, person):
        self.population.append(person)

    def getGravityFactor(self, person, normDistMat, xDistMat, yDistMat):
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
        totalForce -= self.socialDistanceSize * self.calculateGravity(normDistMat, xDistMat, yDistMat)
        
        return totalForce
    
    def calculateGravity(self, normDistMat, xDistMat, yDistMat):

        
        #+1 needed to stop things less than 1 from blowing up
        
        xargs = xDistMat[np.argsort(normDistMat)[1:10]]
        yargs = yDistMat[np.argsort(normDistMat)[1:10]]
        gravVec = np.zeros(2)
        gravVec[0] = np.sum(xargs,axis=0)
        gravVec[1] = np.sum(yargs,axis=0)
               
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