import numpy
from itertools import combinations

def generateIndividual(nbCulture,nbParcelle,numMinPaille,numMinEnsillage,surface,etaPaille,etaEnsillage):
    # matrix = numpy.zeros((nbParcelle, nbCulture))
    # matrix_1 = numpy.zeros((nbParcelle,nbCulture))
    #
    # for i in range(nbParcelle):
    #     matrix_1[i][numpy.random.random_integers(0,4)]=1
    #
    # for i in range(numpy.random.random_integers(0,20)):
    #     matrix=numpy.random.permutation(matrix_1)
    #     matrix_1=matrix
    #
    # return matrix

    count=0
    while True:
        matrix=numpy.zeros((nbParcelle,nbCulture))
        matrix_1 = numpy.zeros((nbParcelle,nbCulture))

        for i in range(nbParcelle):
            matrix_1[i][numpy.random.random_integers(0,4)]=1

        for i in range(numpy.random.random_integers(0,20)):
            matrix=numpy.random.permutation(matrix_1)
            matrix_1=matrix

        qtePaille = surface * numpy.matmul(matrix, etaPaille)
        qteEnsillage = surface * numpy.matmul(matrix, etaEnsillage)


        if sum(qtePaille) >= numMinPaille and sum(qteEnsillage) >= numMinEnsillage:
            return matrix

        count+=1
        if count>1000:
            return matrix



def cal_pop_fitness(MPC,MPCn1,MPTS,R1,R2,eta,etaPaille,etaEnsillage,surface,prixVenteCulture,coutProdCulture,nbParcelle,numMinPaille,numMinEnsillage):

    eta1 = numpy.matmul(MPC, eta)
    v = numpy.zeros(nbParcelle)

    for i in range(len(MPC)):
        v = v + numpy.matmul(numpy.matmul(MPC[i], R1), numpy.transpose(MPTS[i])) * numpy.identity(nbParcelle)[i]

    eta2 = (numpy.ones(nbParcelle) - v / 100)

    u = numpy.zeros(nbParcelle)
    for i in range(nbParcelle):
        u = u+numpy.matmul(numpy.matmul(R2,MPC[i]),MPCn1[i])*numpy.identity(6)[i]

    eta3 = (u / 100)

    # Calcul MB
    marBruteParcelle = (surface * (eta1 * eta2 * eta3 * numpy.matmul(MPC, prixVenteCulture) - numpy.matmul(MPC, coutProdCulture)))
    qtePaille = surface * numpy.matmul(MPC,etaPaille)
    qteEnsillage = surface*numpy.matmul(MPC,etaEnsillage)
    if sum(qteEnsillage)<numMinEnsillage or sum(qtePaille)<numMinPaille:
         fitness=0
    else:
         fitness = sum(marBruteParcelle)
    return fitness



def selectElite(pop,fitness):
    parentValue=sorted(fitness,reverse=True)[0:1]
    indexParent=[]
    for parent in parentValue:
        indexParent.append(fitness.index(parent))
    parents=[]
    for index in indexParent:
        parents.append(pop[index])
    return [parents,parentValue]

def select_mating_pool(pop, fitness, num_parents):
    # parentValue=sorted(fitness,reverse=True)[0:num_parents]
    # indexParent=[]
    # for parent in parentValue:
    #     indexParent.append(fitness.index(parent))
    # parents=[]
    # for index in indexParent:
    #     parents.append(pop[index])
    # return parents

    # lowIndex,upperIndex,breederList=[],[],[]
    # cumulativeFitness = numpy.cumsum(fitness)
    # totalSumFitness = int(numpy.sum(fitness))
    # for nbBreeder in range(num_parents):
    #     criteriaLevel = numpy.random.randint(0, totalSumFitness)
    #     for i in range(len(cumulativeFitness)):
    #         if i==0:
    #             lowIndex.append(0)
    #             upperIndex.append(int(cumulativeFitness[i]))
    #         else:
    #             lowIndex.append(int(upperIndex[i-1])+1)
    #             upperIndex.append(int(cumulativeFitness[i]))
    #
    #         if lowIndex[i]<= criteriaLevel<=upperIndex[i]:
    #             breederList.append(pop[i])
    #             break

    sumFitness = numpy.sum(fitness)
    weights = numpy.array(fitness/sumFitness)
    breederList=[]
    for nbBreeder in range(num_parents):
        breederIndex=numpy.random.choice(len(pop),size=1,replace=False,p=weights)
        breederList.append(pop[breederIndex[0]])
    return breederList





def crossover(parentList, offspring_size,nbParcelle,nbCulture,surface,numMinEnsillage,numMinPaille,etaPaille,etaEnsillage):

    selectedBreederList=parentList
    parentCombination =[]
    offSpring=[]

    Combination=combinations(selectedBreederList, 2)
    for i in list(Combination):
        parentCombination.append(i)
    for combi in parentCombination:
        indexSplit=numpy.random.randint(0,nbParcelle)
        if numpy.all(combi[0])!=numpy.all(combi[1]):

            offSpringA = numpy.vstack((combi[0][0:indexSplit,:],combi[1][indexSplit:nbParcelle,:]))
            offSpringB = numpy.vstack((combi[1][0:indexSplit, :],combi[0][indexSplit:nbParcelle, :]))
        else :
            offSpringA= generateIndividual(nbCulture=nbCulture,
                                                surface=surface,
                                                nbParcelle=nbParcelle,
                                                numMinEnsillage=numMinEnsillage,
                                                numMinPaille=numMinPaille,
                                                etaPaille=etaPaille,
                                                etaEnsillage=etaEnsillage)

            offSpringB= generateIndividual(nbCulture=nbCulture,
                                                surface=surface,
                                                nbParcelle=nbParcelle,
                                                numMinEnsillage=numMinEnsillage,
                                                numMinPaille=numMinPaille,
                                                etaPaille=etaPaille,
                                                etaEnsillage=etaEnsillage)

        offSpring.append(offSpringA)
        offSpring.append(offSpringB)


    return offSpring



def mutation(offspringList,nbParcelle,nbCulture):
    # Mutation changes a single gene in each offspring randomly.

    mutatedOffSpring=[]

    for offspring in offspringList:

        offSpringIndex=numpy.random.randint(0,nbParcelle)
        geneIndex=numpy.random.randint(0,nbCulture)
        mutatedRow=numpy.zeros(nbCulture)
        mutatedRow[geneIndex]=1
        offspring[offSpringIndex,:]=mutatedRow

        mutatedOffSpring.append(offspring)

    return mutatedOffSpring
