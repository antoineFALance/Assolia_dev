import numpy as np

Vculture=['Soja','Blé de force','Orge', 'Maïs','Tournesol']
parcelle=np.array([1,0,0,0,0,0])
nbCulture = 5
nbParcelle = len(parcelle)


MPC = np.array([[ 0.,  0.,  0.,  0.,  1.],
       [ 0.,  0.,  0.,  0.,  1.],
       [ 0.,  0.,  0.,  0.,  1.],
       [ 0.,  1.,  0.,  0.,  0.],
       [ 0.,  1.,  0.,  0.,  0.],
       [ 0.,  0.,  0.,  1.,  0.]])

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

MPCn1 =np.array([[ 0.,  1.,  0.,  0.,  0.],
       [ 0.,  1.,  0.,  0.,  0.],
       [ 0.,  1.,  0.,  0.,  0.],
       [ 0.,  0.,  0.,  1.,  0.],
       [ 0.,  0.,  0.,  0.,  1.],
       [ 0.,  1.,  0.,  0.,  0.]])

MPTS=np.array([[1, 0, 0, 0],
               [1, 0, 0, 0],
               [1, 0, 0, 0],
               [0, 0, 0, 1],
               [0, 0, 0, 1],
               [0, 0, 0, 1]])
print(np.transpose(MPTS))

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

surface=np.array([10,10,10,20,20,20])
prixVenteCulture=np.array([350,200,150,150,400])
coutProdCulture=np.array([400,600,400,1200,300])

eta=np.array([4,8,7,13,3.4])
# etaPaille=np.array([0,5.44,4.76,0,0])
# etaEnsillage=np.array([0,0,0,18.525,0])

eta1=np.matmul(MPC,eta)

v = np.zeros(6)

for i in range(len(MPC)):

    v=v+np.matmul(np.matmul(MPC[i],R1),np.transpose(MPTS[i]))*np.identity(6)[i]

eta2=(np.ones(6)-v/100)

u=np.zeros(6)
for i in range(6):

    u=u+np.matmul(np.matmul(R2,MPC[i]),MPCn1[i])*np.identity(6)[i]



eta3=(u/100)

print("surface")
print(surface)
print('rendement')


print(eta)
print("eta1")
print(eta1)
print("eta2")
print(eta2)
print("eta3")
print(eta3)
print(eta1*eta2*eta3)
print("PV")
print(np.matmul(MPC,prixVenteCulture))
print('cout')
print(np.matmul(MPC,coutProdCulture))
print("etaPaille")
etaPaille=np.matmul(np.matmul(MPC, lambdaPaille),eta)
etaEnsillage=np.matmul(np.matmul(MPC, lambdaEnsilage),eta)




#Calcul MB
print("MB parcelle")
# marBruteParcelle=(surface*(eta1*eta2*eta3*np.matmul(MPC,prixVenteCulture)-np.matmul(MPC,coutProdCulture)))
# print(marBruteParcelle)
marBruteParcelle_Excel = surface*eta3*(eta1*eta2*np.matmul(MPC,prixVenteCulture)-np.matmul(MPC,coutProdCulture))
print(marBruteParcelle_Excel)

print("MB")
# print(marBruteParcelle)
#print(sum(marBruteParcelle))
print(sum(marBruteParcelle_Excel))
# qtePaille = surface * np.matmul(MPC,etaPaille)
# qteEnsillage = surface*np.matmul(MPC,etaEnsillage)
qtePaille=0.8*surface*etaPaille*eta2*eta3
qteEnsillage=1.5*surface*etaEnsillage*eta2*eta3

print(sum(qtePaille))
print(sum(qteEnsillage))

