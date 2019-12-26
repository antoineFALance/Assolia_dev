import GA_test as ga
import numpy as np
import matplotlib.pyplot as mpl
import time
start_time_2 = time.clock()

#1.déclaration des constantes

nbParcelle=6
nbCulture = 5
numGeneration=10000
numYear =3
Vculture=['Soja','Blé de force','Orge', 'Maïs','Tournesol']

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



# etaPaille=np.matmul(np.array([0,6.4,5.6,0,0]))
# etaEnsillage=np.array([0,0,0,19.5,0])

surface=np.array([10,10,10,20,20,20])

prixVenteCulture=np.array([350,200,150,150,400])
coutProdCulture=np.array([400,600,400,1200,300])

eta=np.array([4,8,7,13,3.4])

#Construction matrice Lambda paille
indexCulturePaille=[]
for culture in Vculture:
    if culture=='Blé de force' or culture =='Orge':
        indexCulturePaille.append(Vculture.index(culture))
lambdaPaille=np.zeros((nbCulture,nbCulture))
for index in indexCulturePaille:
    lambdaPaille[index][index]=1


#Construction matrice Lambda ensilage
indexCultureEnsilage=[]
for culture in Vculture:
    if culture=='Maïs':
        indexCultureEnsilage.append(Vculture.index(culture))
lambdaEnsilage=np.zeros((nbCulture,nbCulture))
for index in indexCultureEnsilage:
    lambdaEnsilage[index][index]=1



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
                                                eta=eta,
                                                lambdaPaille=lambdaPaille,
                                                lambdaEnsilage=lambdaEnsilage,
                                                R1=R1,
                                                R2=R2,
                                                MPTS=MPTS,
                                                MPCn1=MPCn1))
yearSolution =[]
yearExecutionTime=[]
yearEliteValue,yearEliteMaxValue=[],[]
initRepartition=MPCn1
repartitionN1=[MPCn1]
if numYear>1:
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
                                                    lambdaPaille=lambdaPaille,
                                                    lambdaEnsillage=lambdaEnsilage,
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
                               lambdaPaille=lambdaPaille,
                               lambdaEnsillage=lambdaEnsilage,
                               eta=eta,
                               surface=surface,
                               R1=R1,
                               R2=R2,
                               MPTS=MPTS,
                               MPCn1=MPCn1
                               )

        #5.2 - Mutation
        mutatedOffSpring=ga.mutation(offspringList=offSpring,nbParcelle=nbParcelle,nbCulture=nbCulture)
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
        # print("OPTIMAL SOLUTION")
        # print(optimalSolution)
    else:
        print("IMPOSSIBLE TO CONVERGE")
        print("change constraints")

for indexYear in range(numYear):
    etaPaille = np.matmul(np.matmul(yearSolution[indexYear], lambdaPaille), eta)
    etaEnsillage = np.matmul(np.matmul(yearSolution[indexYear], lambdaEnsilage), eta)

    v = np.zeros(nbParcelle)
    for i in range(len(yearSolution[indexYear])):
        v = v + np.matmul(np.matmul(yearSolution[indexYear][i], R1), np.transpose(MPTS[i])) * np.identity(nbParcelle)[i]

    eta2 = (np.ones(nbParcelle) - v / 100)

    u = np.zeros(nbParcelle)
    for i in range(nbParcelle):
        u = u+np.matmul(np.matmul(R2,yearSolution[indexYear][i]),MPCn1[i])*np.identity(6)[i]
    eta3 = (u / 100)

    qtePaille = surface * etaPaille*eta2*eta3*0.8
    qteEnsillage = surface *etaEnsillage*eta2*eta3*1.5

    marBruteParcelle = ga.cal_pop_fitness(nbParcelle=nbParcelle, MPC=yearSolution[indexYear],
                                          MPCn1=repartitionN1[indexYear],
                                          R1=R1, R2=R2, MPTS=MPTS,
                                          eta=eta,
                                          lambdaPaille=lambdaPaille,
                                          lambdaEnsillage=lambdaEnsilage,
                                          numMinPaille=numMinPaille,
                                          numMinEnsillage=numMinEnsillage,
                                          surface=surface,
                                          prixVenteCulture=prixVenteCulture,
                                          coutProdCulture=coutProdCulture)
    print("Marge brute par parcelle")
    Mb=ga.margeBruteParcelle(nbParcelle=nbParcelle, MPC=yearSolution[indexYear],
                                          MPCn1=repartitionN1[indexYear],
                                          R1=R1, R2=R2, MPTS=MPTS,
                                          eta=eta,
                                          surface=surface,
                                          prixVenteCulture=prixVenteCulture,
                                          coutProdCulture=coutProdCulture)



    print("ANNEE n°"+str(indexYear))
    print("##############")
    print("REPARTITION OPTIMALE")
    print(yearSolution[indexYear])
    print("REPARTITION N-1")
    print(repartitionN1[indexYear])
    print("TOTAL MARGE")
    print(Mb)
    print(marBruteParcelle)
    print("QTE PAILLE")
    print(qtePaille)
    print(sum(qtePaille))
    print("QTE ENSILLAGE")
    print(qteEnsillage)
    print(sum(qteEnsillage))
    print("TEMPS EXECUTION")
    print(str(yearExecutionTime[indexYear])+" seconds")
    print(time.strftime('%H:%M:%S',time.gmtime(yearExecutionTime[indexYear])))
    print(time.clock() - start_time_2)
    if numYear>1:
        ax[indexYear].plot(range(len(yearEliteValue[indexYear])),yearEliteValue[indexYear],range(len(yearEliteMaxValue[indexYear])),yearEliteMaxValue[indexYear])  # row=0, col=0
        ax[indexYear].set_xlabel('ITERATION')
        ax[indexYear].set_ylabel('MARGE BRUTE')
    else:
        mpl.plot(range(len(yearEliteValue[indexYear])),yearEliteValue[indexYear],range(len(yearEliteMaxValue[indexYear])),yearEliteMaxValue[indexYear])


mpl.show()