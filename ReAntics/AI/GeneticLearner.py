import random
import sys

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Spore")
        self.geneList = []
        self.geneListEnemy = []
        self.selectGeneIndex = 0
        self.powerFactor = 3
        self.multiplyFactor = 3
        self.geneFitness = []        # gamesWon ^ powerFactor + 1
        self.numGenes = 50         # always even
        self.geneLength = 40
        self.geneLengthEnemy = 29
        self.inverseProb = 10        # 1/(.10)
        self.maxInt = 9223372036854775807
        self.gamesPerGene = 40
        self.gamesLeft = self.gamesPerGene
        self.initGenes()

    def initGenes(self):
        for i in range(0, self.numGenes):
            gene = []
            geneEnemy = []
            for j in range(0, self.geneLength):
                gene.append(random.randint(0, self.maxInt))
            for j in range(0, self.geneLengthEnemy):
                geneEnemy.append(random.randint(0, self.maxInt))
            self.geneList.append(gene)
            self.geneListEnemy.append(geneEnemy)
            self.geneFitness.append(0)

        return True

    def createGeneration(self):
        adjustFitness = []
        for fitness in self.geneFitness: adjustFitness.append(pow(fitness,self.powerFactor)+ fitness* + 1)
        totFitness = sum(adjustFitness)
        nextGen = []
        nextGenEnemy = []
        nextFitness = []

        for i in range(0,round(self.numGenes/2)):
            selectedParents = self.parentSelect(totFitness, adjustFitness)
            randOrderInt = random.randint(0,1)
            children = self.createChildren(selectedParents[randOrderInt], selectedParents[1-randOrderInt])
            childrenEnemy = self.createChildrenEnemy(selectedParents[randOrderInt], selectedParents[1-randOrderInt])
            nextGen.append(children[0])
            nextGen.append(children[1])
            nextGenEnemy.append(childrenEnemy[0])
            nextGenEnemy.append(childrenEnemy[1])
            nextFitness.append(0)
            nextFitness.append(0)

        self.geneList = nextGen
        self.geneListEnemy = nextGenEnemy
        self.geneFitness = nextFitness

    def parentSelect(self, totFitness, adjustFitness):
        firstSelectIndex = -1
        randSelect = random.randint(1, totFitness)
        for i in range(0, self.numGenes):
            if randSelect <= adjustFitness[i]:
                firstSelectIndex = i
                break
            else:
                randSelect -= adjustFitness[i]

        secondSelectIndex = -1
        totFitness = totFitness - adjustFitness[firstSelectIndex]
        randSelect = random.randint(0, totFitness)
        for i in range(0, self.numGenes):
            if i != firstSelectIndex:
                if randSelect <= adjustFitness[i]:
                    secondSelectIndex = i
                    break
                else:
                    randSelect -= adjustFitness[i]

        return [firstSelectIndex, secondSelectIndex]

    def createChildren(self, dadIndex, momIndex):
        sliceInt = random.randint(0, self.geneLength)
        startIndecies = slice(0, sliceInt, 1)
        endIndicies = slice(sliceInt, self.geneLength, 1)
        son = self.geneList[dadIndex][startIndecies].copy()
        son.extend(self.geneList[momIndex][endIndicies].copy())
        sonMutator = random.randint(0, self.geneLength*self.inverseProb)
        if sonMutator < self.geneLength:
            son[sonMutator] = random.randint(0,self.maxInt)
        daughter = self.geneList[momIndex][startIndecies].copy()
        daughter.extend(self.geneList[dadIndex][endIndicies].copy())
        daughterMutator = random.randint(0, self.geneLength*self.inverseProb)
        if daughterMutator < self.geneLength:
            daughter[daughterMutator] = random.randint(0,self.maxInt)
        children = [son, daughter]
        return children

    def createChildrenEnemy(self, dadIndex, momIndex):
        sliceInt = random.randint(0, self.geneLengthEnemy)
        startIndecies = slice(0, sliceInt, 1)
        endIndicies = slice(sliceInt, self.geneLengthEnemy, 1)
        son = self.geneListEnemy[dadIndex][startIndecies].copy()
        son.extend(self.geneListEnemy[momIndex][endIndicies].copy())
        sonMutator = random.randint(0, self.geneLengthEnemy*self.inverseProb)
        if sonMutator < self.geneLengthEnemy:
            son[sonMutator] = random.randint(0,self.maxInt)
        daughter = self.geneListEnemy[momIndex][startIndecies].copy()
        daughter.extend(self.geneListEnemy[dadIndex][endIndicies].copy())
        daughterMutator = random.randint(0, self.geneLengthEnemy*self.inverseProb)
        if daughterMutator < self.geneLengthEnemy:
            daughter[daughterMutator] = random.randint(0,self.maxInt)
        children = [son, daughter]
        return children

    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            geneIndices = [j[0] for j in sorted(enumerate(self.geneList[self.selectGeneIndex]), key=lambda x:x[1])]
            moves = [(-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1)]
            for i in range(0, self.geneLength):
                if geneIndices[i] <= 10:
                    moves[geneIndices[i]] = (i%10, round((i-i%10)/10))

            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            geneIndices = [j[0] for j in sorted(enumerate(self.geneListEnemy[self.selectGeneIndex]), key=lambda x:x[1])]
            moves = []
            for i in range(0, self.geneLengthEnemy):
                if geneIndices[i] <= 1:
                    if i < 9:
                        moves.append((i,6))
                    elif i < 17:
                        moves.append((i-9,7))
                    elif i < 21:
                        moves.append((i-17,8))
                    elif i < 23:
                        moves.append((i-16,8))
                    else:
                        moves.append((i-23,9))
            return moves     #temporary hard code food placement
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0, len(moves) - 1)];

        # don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0, len(moves) - 1)];

        return selectedMove

    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    # registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        if hasWon: self.geneFitness[self.selectGeneIndex] += 1

        self.gamesLeft -= 1
        if self.gamesLeft == 0:
            self.gamesLeft = self.gamesPerGene
            self.selectGeneIndex += 1

        if self.selectGeneIndex >= self.numGenes:
            self.printGenerationResults()
            self.createGeneration()
            self.selectGeneIndex = 0

    def printGenerationResults(self):
        maxFitness = max(self.geneFitness)
        indexOfMax = -1
        for i in range(0,self.numGenes):
            if self.geneFitness[i] == maxFitness:
                indexOfMax = i
                break
        print("Fitness of best gene: " + str(maxFitness))
        print("Gene:" + str([j[0] for j in sorted(enumerate(self.geneList[indexOfMax]), key=lambda x:x[1])]))
        print("GeneEnemy:" + str([j[0] for j in sorted(enumerate(self.geneListEnemy[indexOfMax]), key=lambda x:x[1])]))