import GA_test as ga
import numpy as np
import matplotlib.pyplot as mpl
import time
import pandas as pd
start_time_2 = time.clock()

#1.déclaration des constantes

nbParcelle=6
nbCulture = 5
numGeneration=1000
numYear =3
Vculture=['Soja','Blé de force','Orge', 'Maïs','Tournesol']

numMinPaille=200
numMinEnsillage = 250
numSolutionperYear=3

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
optimalSolution = []
optimalSolutionValue = []
repartitionOptimalSolution=[]
repartitionOptimalSolutionValue=[]

if numYear>1:
    fig, ax = mpl.subplots(nrows=numYear, ncols=1,sharex='col')
for yearIndex in range(numYear):
    print("ANNEE N°" + str(yearIndex))

    repartitionCount=0
    xplotList = []
    yplotlist = []
    eliteList = []



    start_time = time.clock()



    if yearIndex==0:
        initRepartition=[MPCn1]
        print("INIT REPARTITION")
        print(initRepartition)
    else:
        initRepartition=optimalSolution
        print("INIT REPARTITION")
        print(initRepartition)
        optimalSolution=[]
        optimalSolutionValue = []



    for repartition in initRepartition:
        generationCount = 0
        print("ANNEE N°" + str(yearIndex) + " REP-" + str(repartitionCount))




        while True:
            fitnessResult = []

            #3.Evaluation de la population

            for individual in initPopulation:
                fitnessResult.append(ga.cal_pop_fitness(nbParcelle=nbParcelle,MPC=individual,
                                                        MPCn1=repartition,
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
            # print("")
            # print("ANNEE N°" + str(yearIndex) + " REP-" + str(repartitionCount) +"-GEN "+str(generationCount))
            # print("#####FITNESS#####")
            # print(fitnessResult)
            # # print("#################")
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
                eliteValue.append(elite[1][0])
                eliteRepartition.append(elite[0])
                initMaxValue=max([elite[1][0],initMaxValue])
                eliteMaxValue.append(initMaxValue)
            yearEliteValue.append(eliteValue)
            yearEliteMaxValue.append(eliteMaxValue)
            distinctElitevalue=list(set(eliteValue))

            #Sécurité en cas de données distinctes insuffisante
            if len(distinctElitevalue)<numSolutionperYear:
                while len(distinctElitevalue)<numSolutionperYear:
                    distinctElitevalue.append(distinctElitevalue[len(distinctElitevalue)])



            for elite in sorted(distinctElitevalue,reverse=True)[:numSolutionperYear]:
                optimalSolution.append(eliteRepartition[eliteValue.index(elite)][0])
                optimalSolutionValue.append(elite)



        else:
            print("IMPOSSIBLE TO CONVERGE")
            print("change constraints")

        repartitionCount+=1

    repartitionOptimalSolution.append(optimalSolution)
    repartitionOptimalSolutionValue.append(optimalSolutionValue)

    print("repartitionOptimalSolutionValue")
    print(repartitionOptimalSolutionValue)
#Création de la matrice des résultats
listMatrix,colMatrix=[],[]

for indexYear in range(numYear):
    LambdaLocal=np.zeros((numSolutionperYear**(indexYear+1),numSolutionperYear**numYear))
    for i in range((numSolutionperYear)**(indexYear+1)):
        for j in range(numSolutionperYear**numYear):
            if i*(numSolutionperYear)**(numYear-(indexYear+1))<=j<=(i+1)*numSolutionperYear**(numYear-(indexYear+1))-1:
                LambdaLocal[i][j]=1

    listMatrix.append(LambdaLocal)

    colMatrix.append(np.matmul(repartitionOptimalSolutionValue[indexYear],listMatrix[indexYear]))

print("debug")
matrixResult=np.transpose(colMatrix)
columnLabel=[]
dfResult=pd.DataFrame(matrixResult)
dfResult['mean'] = dfResult.mean(axis=1)
maxMean=dfResult[dfResult['mean']==dfResult['mean'].max()]
resultList=maxMean.values.tolist()[0]
print(dfResult)
print("RESULT")
print(maxMean.values.tolist())
configResultList,test=[],[]
for indexYear in range(numYear):
    configResultList.append(repartitionOptimalSolution[indexYear][repartitionOptimalSolutionValue[indexYear].index(resultList[indexYear])])
    test.append(repartitionOptimalSolutionValue[indexYear][repartitionOptimalSolutionValue[indexYear].index(resultList[indexYear])])
print(configResultList)
print(test)













