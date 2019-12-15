

import random
import numpy as np

from deap import base
from deap import creator
from deap import tools


#1. Défintition des paramètres d'entrés
#MPC = np.array([[0,0,0,0,1],
#               [0,0,1,0,0],
#               [1,0,0,0,0],
#               [0,1,0,0,0],
#               [0,0,0,1,0],
#               [1,0,0,0,0]])

MPCn1 = np.array([[0,0,0,0,1],
               [1,0,0,0,0],
               [0,1,0,0,0],
               [1,0,0,0,0],
               [0,0,1,0,0],
               [0,0,0,1,0]])


MPTS=np.array([[1, 0, 0, 0],
               [1, 0, 0, 0],
               [1, 0, 0, 0],
               [0, 0, 0, 1],
               [0, 0, 0, 1],
               [0, 0, 0, 1]])

R1=np.array([[50,15,30,5],
               [15,15,25,5],
               [15,15,25,5],
               [25,10,25,5],
               [15,10,25,5]])

R2=np.array([[50,100,100,95,95],
             [100,30,70,100,100],
             [100,50,50,100,100],
             [100,80,80,80,80],
             [100,95,95,95,95]])

eta=np.array([4,8,7,13,3.4])
surface=np.array([10,10,10,10,10,10])
prixVenteCulture=np.array([350,200,150,150,400])
coutProdCulture=np.array([400,600,400,1200,300])

#2. Défintition paramètres algo évolutionnaire

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
#                      define 'attr_bool' to be an attribute ('gene')
#                      which corresponds to integers sampled uniformly
#                      from the range [0,1] (i.e. 0 or 1 with equal
#                      probability)
toolbox.register("attr_int", np.random.randint, 2, size=(6,5))

# Structure initializers
#                         define 'individual' to be an individual
#                         consisting of 100 'attr_bool' elements ('genes')
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_int,1)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


# the goal ('fitness') function to be maximized
def evalOneMax(individual):
    print("individual")
    print(individual)
    MPC = individual[0]
    eta1 = np.matmul(MPC, eta)
    v = np.zeros(6)

    for i in range(len(MPC)):
        v = v + np.matmul(np.matmul(MPC[i], R1), np.transpose(MPTS[i])) * np.identity(6)[i]

    eta2 = (np.ones(6) - v / 100)

    u = np.zeros(6)
    for i in range(6):
        u = u + np.matmul(np.matmul(MPC[i], R2), np.transpose(MPCn1[i])) * np.identity(6)[i]

    eta3 = (u / 100)

    marBruteParcelle = (surface * (eta1 * eta2 * eta3 * np.matmul(MPC, prixVenteCulture) - np.matmul(MPC, coutProdCulture)))

    return sum(marBruteParcelle),


# ----------
# Operator registration
# ----------
# register the goal / fitness function
toolbox.register("evaluate", evalOneMax)

# register the crossover operator
toolbox.register("mate", tools.cxTwoPoint)

# register a mutation operator with a probability to
# flip each attribute/gene of 0.05
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of three individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selTournament, tournsize=3)


# ----------

def main():



    random.seed(64)

    # create an initial population of 300 individuals (where
    # each individual is a list of integers)
    pop = toolbox.population(n=10)
    print("pop")
    print(pop)

    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual
    CXPB, MUTPB = 0.5, 0.2

    print("Start of evolution")

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    print('###fitnesses###')
    print(fitnesses)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    print("  Evaluated %i individuals" % len(pop))

    # Extracting all the fitnesses of
    print("fits")
    fits = [ind.fitness.values[0] for ind in pop]
    print(fits)
    print('max')
    print(max(fits))

    # Variable keeping track of the number of generations
    g = 0

    # Begin the evolution
    while max(fits) < 100 and g < 1000:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:

            # mutate an individual with probability MUTPB
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))


if __name__ == "__main__":
    main()