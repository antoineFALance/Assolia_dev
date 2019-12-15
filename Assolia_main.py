import GA_test as ga
import numpy as np
import matplotlib.pyplot as mpl
import time
start_time_2 = time.clock()



#0.Fonctions



#1.déclaration des constantes

nbParcelle=6
nbCulture = 5
numGeneration=10000
numYear =5

numMinPaille=200
numMinEnsillage = 250

MPCn1 = np.array([[0,0,0,0,1],
               [0,1,0,0,0],
               [0,0,1,0,0],
               [1,0,0,0,0],
               [1,0,0,0,0],
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

etaPaille=np.array([0,5.44,4.76,0,0])
etaEnsillage=np.array([0,0,0,18.525,0])

surface=np.array([10,10,10,20,20,20])

prixVenteCulture=np.array([350,200,150,150,400])
coutProdCulture=np.array([400,600,400,1200,300])

eta=np.array([4,8,7,13,3.4])

popSize=10
numParentMating=int(popSize/2)
offspringSize=int(popSize/2)

#2.Génération de la population
initPopulation = []
for individual in range(popSize):
    initPopulation.append(ga.generateIndividual(nbCulture=nbCulture,
                                                surface=surface,
                                                nbParcelle=nbParcelle,
                                                numMinEnsillage=numMinEnsillage,
                                                numMinPaille=numMinPaille,
                                                etaPaille=etaPaille,
                                                etaEnsillage=etaEnsillage))

# print("####INIT POP")
# print(initPopulation)


yearSolution =[]
yearExecutionTime=[]
yearEliteValue,yearEliteMaxValue=[],[]
initRepartition=MPCn1
repartitionN1=[MPCn1]
fig, ax = mpl.subplots(nrows=numYear, ncols=1,sharex='col')
for yearIndex in range(numYear):
    generationCount = 0
    xplotList = []
    yplotlist = []
    eliteList = []
    start_time = time.clock()

    print("ANNEE N°"+str(yearIndex))

    while True:
        fitnessResult = []

        #3.Evaluation de la population

        for individual in initPopulation:
            fitnessResult.append(ga.cal_pop_fitness(nbParcelle=nbParcelle,MPC=individual,
                                                    MPCn1=initRepartition,
                                                    R1=R1,R2=R2,MPTS=MPTS,
                                                    eta=eta,
                                                    etaPaille=etaPaille,
                                                    etaEnsillage=etaEnsillage,
                                                    numMinPaille=numMinPaille,
                                                    numMinEnsillage=numMinEnsillage,
                                                    surface=surface,
                                                    prixVenteCulture=prixVenteCulture,
                                                    coutProdCulture=coutProdCulture))

        eliteList.append(ga.selectElite(initPopulation,fitnessResult))

        xplotList.append(generationCount)
        yplotlist.append(ga.selectElite(initPopulation,fitnessResult)[1])
        print("ANNEE "+str(yearIndex)+"-GENERATION N°"+str(generationCount))
        print("#####FITNESS#####")
        print(fitnessResult)
        # print("#################")
        if sum(fitnessResult)==0:
            breakFlag=0
            break

        if generationCount>numGeneration:
            breakFlag=2
            break

        #4.Génération des parents
        parent=ga.select_mating_pool(initPopulation,fitnessResult,numParentMating)
        # print("####PARENT####")
        # print(parent)

        #5.Génération des descendants
        #5.1-Crossover
        offSpring=ga.crossover(parent,
                               offspringSize,
                               nbParcelle=nbParcelle,
                               nbCulture=nbCulture,
                               numMinEnsillage=numMinEnsillage,
                               numMinPaille=numMinPaille,
                               etaPaille=etaPaille,
                               etaEnsillage=etaEnsillage,
                               surface=surface
                               )
        # print("####OFFSPRING####")
        # print(offSpring)
        #5.2 - Mutation
        mutatedOffSpring=ga.mutation(offspringList=offSpring,nbParcelle=nbParcelle,nbCulture=nbCulture)
        # print("####MUTATION####")
        # print(mutatedOffSpring)

        newPopulation=parent[:2]+mutatedOffSpring
        initPopulation=newPopulation[:popSize]
        generationCount+=1



    if breakFlag==1 or breakFlag==2:
        eliteValue=[]
        eliteRepartition=[]
        eliteMaxValue=[]
        initMaxValue=0

        for elite in eliteList:
            eliteValue.append(elite[1])
            eliteRepartition.append(elite[0])
            initMaxValue=max([elite[1][0],initMaxValue])
            eliteMaxValue.append(initMaxValue)
        yearEliteValue.append(eliteValue)
        yearEliteMaxValue.append(eliteMaxValue)
        optimalSolution=eliteRepartition[eliteValue.index(max(eliteValue))][0]
        yearSolution.append(optimalSolution)
        initRepartition=optimalSolution
        repartitionN1.append(optimalSolution)
        yearExecutionTime.append(time.clock() - start_time)
        print("OPTIMAL SOLUTION")
        print(optimalSolution)


    else:
        print("IMPOSSIBLE TO CONVERGE")
        print("change constraints")

for indexYear in range(numYear):
    qtePaille = surface * np.matmul(yearSolution[indexYear], etaPaille)
    qteEnsillage = surface * np.matmul(yearSolution[indexYear], etaEnsillage)
    marBruteParcelle = ga.cal_pop_fitness(nbParcelle=nbParcelle, MPC=yearSolution[indexYear],
                                          MPCn1=repartitionN1[indexYear],
                                          R1=R1, R2=R2, MPTS=MPTS,
                                          eta=eta,
                                          etaPaille=etaPaille,
                                          etaEnsillage=etaEnsillage,
                                          numMinPaille=numMinPaille,
                                          numMinEnsillage=numMinEnsillage,
                                          surface=surface,
                                          prixVenteCulture=prixVenteCulture,
                                          coutProdCulture=coutProdCulture)
    print("ANNEE n°"+str(indexYear))
    print("##############")
    print("REPARTITION OPTIMALE")
    print(yearSolution[indexYear])
    print("TOTAL MARGE")
    print(marBruteParcelle)
    print("QTE PAILLE")
    print(sum(qtePaille))
    print("QTE ENSILLAGE")
    print(sum(qteEnsillage))
    print("TEMPS EXECUTION")
    print(str(yearExecutionTime[indexYear])+" seconds")
    print(time.strftime('%H:%M:%S',time.gmtime(yearExecutionTime[indexYear])))
    print(time.clock() - start_time_2)
    #print(time.clock() - start_time, "seconds")

    ax[indexYear].plot(range(len(yearEliteValue[indexYear])),yearEliteValue[indexYear],range(len(yearEliteMaxValue[indexYear])),yearEliteMaxValue[indexYear])  # row=0, col=0
    ax[indexYear].set_xlabel('ITERATION')
    ax[indexYear].set_ylabel('MARGE BRUTE')

    # mpl.plot(range(len(eliteValue)),eliteValue,range(len(eliteMaxValue)), eliteMaxValue)

mpl.show()