import random
import sys
import os

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

    ##
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Spore")
        self.geneList = []          # genes for our side of the board stored here
        self.geneListEnemy = []     # genes for their side of the board stored here
        self.selectGeneIndex = 0
        self.powerFactor = 3        # used to find weighted fitness
        self.multiplyFactor = 3     # used to find weighted fitness
        self.geneFitness = []       # gamesWon ^ powerFactor + 1
        self.numGenes = 50          # always even
        self.geneLength = 40
        self.geneLengthEnemy = 29
        self.inverseProb = 10        # inverse of probability to mutate
        self.maxInt = 9223372036854775807
        self.gamesPerGene = 100
        self.bestFitnessOfGen = 0
        self.curGameState = None    # holds state related to current gene
        self.gamesLeft = self.gamesPerGene # games left for current gene
        self.initGenes()

    ##
    # initGenes
    # helper for init
    # initializes genes and fitness
    #
    ##
    def initGenes(self):
        # initialized genes and fitness (random, 0)
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

    ##
    # create generation
    # creates next generation based on previous generations genes and fitneesses
    #
    ##
    def createGeneration(self):
        adjustFitness = []  # holds adjusted fitness level (amount of enteries of a gene into the lottery)

        # adjustFitness = fitness^powerFactor + fitness*multiplyFactor + 1
        for fitness in self.geneFitness: adjustFitness.append(pow(fitness,self.powerFactor)+ fitness*self.multiplyFactor + 1)
        totFitness = sum(adjustFitness)
        nextGen = []        # holds next generation genes
        nextGenEnemy = []   # holds next generation genes
        nextFitness = []    # holds next generation fitness (always 0)

        # create pairs of genes (siblings)
        for i in range(0,round(self.numGenes/2)):
            selectedParents = self.parentSelect(totFitness, adjustFitness)  # selects parents based on adjusted fitness
            randOrderInt = random.randint(0,1)  # used to randomize which order the parents are spliced together (maybe unnecessary)

            # create a pair of children
            children = self.createChildren(selectedParents[randOrderInt], selectedParents[1-randOrderInt])
            childrenEnemy = self.createChildrenEnemy(selectedParents[randOrderInt], selectedParents[1-randOrderInt])

            #append to all lists
            nextGen.append(children[0])
            nextGen.append(children[1])
            nextGenEnemy.append(childrenEnemy[0])
            nextGenEnemy.append(childrenEnemy[1])
            nextFitness.append(0)
            nextFitness.append(0)

        # replace instance variables
        self.geneList = nextGen
        self.geneListEnemy = nextGenEnemy
        self.geneFitness = nextFitness

    ##
    # parentSelect
    # selects two parents based on fitnesses versus total fitness
    #
    # Parameters:
    #   totFitness - sum of adjusted fitnesses
    #   adjustFitness - adjusted gross fitnesses of each gene
    #
    # Return:
    # [firstSelectIndex, secondSelectIndex] - index of parents selected
    def parentSelect(self, totFitness, adjustFitness):
        # select first parent
        firstSelectIndex = -1
        # select a random number number to total fitness
        randSelect = random.randint(1, totFitness)
        # pull out the index of fitness that overlaps random select
        for i in range(0, self.numGenes):
            if randSelect <= adjustFitness[i]:
                firstSelectIndex = i
                break
            else:
                randSelect -= adjustFitness[i]

        # select second parent
        # same process but remove first parent from consideration
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

    ##
    # createChildren
    # create children of genes only concerning our side of the board
    #
    # Parameters:
    #   dadIndex, momIndex - indecies of parent genes
    #
    # Returns:
    #   children: list of two child genes
    ##
    def createChildren(self, dadIndex, momIndex):

        sliceInt = random.randint(0, self.geneLength)   # index to slice gene at
        startIndecies = slice(0, sliceInt, 1)   # create start indecies
        endIndicies = slice(sliceInt, self.geneLength, 1)   # create end indecies

        son = self.geneList[dadIndex][startIndecies].copy() # copy dad genes at start indecies
        son.extend(self.geneList[momIndex][endIndicies].copy()) # append mom genes at end indecies

        # randomly mutate one gene
        sonMutator = random.randint(0, self.geneLength*self.inverseProb)
        if sonMutator < self.geneLength:
            son[sonMutator] = random.randint(0,self.maxInt)

        # create daughter (same process, reverse order)
        daughter = self.geneList[momIndex][startIndecies].copy()
        daughter.extend(self.geneList[dadIndex][endIndicies].copy())

        daughterMutator = random.randint(0, self.geneLength*self.inverseProb)
        if daughterMutator < self.geneLength:
            daughter[daughterMutator] = random.randint(0,self.maxInt)
        children = [son, daughter]

        return children

    ##
    # createChildren
    # create children of genes only concerning enemy side of the board
    #
    # Parameters:
    #   dadIndex, momIndex - indecies of parent genes
    #
    # Returns:
    #   children: list of two child genes
    ##
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
            # create am array parallel to selected gene with numbers sorted from highest to lowest
            # example: [20 8 14 2 12] --> [4 1 3 0 2]
            geneIndices = [j[0] for j in sorted(enumerate(self.geneList[self.selectGeneIndex]), key=lambda x:x[1])]
            # move array:
            #   index 0: antihill coords (lowest number in gene)
            #   index 1: tunnel coords (second lowest number in gene)
            #   index 2-10: grass coords (third through eleventh lowest number in genes)
            moves = [(-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1)]
            # place gene in moves appropriately, gene listed from left to right, top to bottom
            for i in range(0, self.geneLength):
                if geneIndices[i] <= 10:
                    moves[geneIndices[i]] = (i%10, round((i-i%10)/10))

            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            # create similar parallel array
            geneIndices = [j[0] for j in sorted(enumerate(self.geneListEnemy[self.selectGeneIndex]), key=lambda x:x[1])]
            # move array:
            #   index 0,1: food coords
            moves = []
            # place gene in moves appropriately, gene listed top to bottom, left to right, skip over booger's used coords
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
        self.curGameState = currentState
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
    # register wins in fitness, decrement games left, move to next gene/generation
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        # count a win
        if hasWon: self.geneFitness[self.selectGeneIndex] += 1

        self.gamesLeft -= 1

        # if we're at the end of a gene's games
        if self.gamesLeft == 0:
            # if this is the best fitness gene so far
            if self.geneFitness[self.selectGeneIndex] >= self.bestFitnessOfGen:
                self.bestFitnessOfGen = self.geneFitness[self.selectGeneIndex]
                #print state to temp.txt
                self.printBestFitness()
            # reset games
            self.gamesLeft = self.gamesPerGene
            # select next gene
            self.selectGeneIndex += 1

        # if we're at the end of a generation
        if self.selectGeneIndex >= self.numGenes:
            # append temp.txt to output file
            self.printGenerationResults()
            self.createGeneration()
            # reset fitness and gene index
            self.bestFitnessOfGen = 0
            self.selectGeneIndex = 0
            # remove temp.txt
            os.remove("temp.txt")
    ##
    # printBestFitness
    # print current saved state
    ##
    def printBestFitness(self):
        f = open("temp.txt", "w+")
        sys.stdout = f
        asciiPrintState(self.curGameState)
        f.close()

    ##
    # printGenerationResults
    # append temp.txt to output file
    ##
    def printGenerationResults(self):
        f = open("schutten19_roux19.txt", "a+")
        f.write(open("temp.txt").read())
        f.close()
