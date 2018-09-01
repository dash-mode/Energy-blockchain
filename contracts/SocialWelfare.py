import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

############################### constants ###############################
n = 0.8
t = 1
l1 = 0.01
l2 = 0.015
p = 0.9
r_min = 1
min_cv = 5
max_cv = 18
min_dv = 5
max_dv = 20

############################### variables ###############################
num_CV = 8
num_DV = 8

phev = np.ones(2*num_CV*num_DV)
cv_bid = np.random.randint(10, 50, num_CV**2)
dv_bid = np.random.randint(50, 100, num_DV**2)
price_vectors = np.concatenate((cv_bid, dv_bid))
initial_bid = [price_vectors[0:num_CV*num_DV], price_vectors[num_CV*num_DV:]]
sto_n = np.array([
        np.random.randint(10, 50, num_CV), 
        np.random.randint(50, 100, num_DV)
        ])

############################### variables for iterative double auction ###############################
e = 0.0001
flag = True
trigger = False
change = False
t = 0

############################### objective 1 ###############################

def objective_1(phev, price_vectors) :
    s = 0
    a = phev.reshape(2, num_CV * num_DV)
    e = np.array([a[0].reshape(num_CV, num_DV), a[1].reshape(num_CV, num_DV)])
    o = price_vectors.reshape(2, num_CV * num_DV)
    p = np.array([o[0].reshape(num_CV, num_DV), o[1].reshape(num_CV, num_DV)])
    for i in range(num_CV) :
        for j in range(num_DV) :
            s += (p[0][i][j] * np.log(e[0][i][j]) - p[1][j][i] * e[1][j][i])
    return -1.0 * s

def constraint_1(x) :
    def constraint1_1(phev) :
        a = phev.reshape(2, num_CV * num_DV)
        e = np.array([a[0].reshape(num_CV, num_DV), a[1].reshape(num_CV, num_DV)])
        return n*sum(e[0][x]) - min_cv
    return constraint1_1
    
def constraint_2(x) :
    def constraint1_2(phev) :
        a = phev.reshape(2, num_CV * num_DV)
        e = np.array([a[0].reshape(num_CV, num_DV), a[1].reshape(num_CV, num_DV)])
        return max_cv - n*sum(e[0][x])
    return constraint1_2 

def constraint_3(x) :
    def constraint1_3(phev) :
        a = phev.reshape(2, num_CV * num_DV)
        e = np.array([a[0].reshape(num_CV, num_DV), a[1].reshape(num_CV, num_DV)])
        return max_dv - sum(e[1][x])
    return constraint1_3

def constraint_4(x, y) :
    def constraint1_4(phev) :
        a = phev.reshape(2, num_CV * num_DV)
        e = np.array([a[0].reshape(num_CV, num_DV), a[1].reshape(num_CV, num_DV)])
        return p*e[1][y][x] - e[0][x][y]
    return constraint1_4

def constraint_5(x, y) :
    def constraint1_5(phev) :
        a = phev.reshape(2, num_CV * num_DV)
        e = np.array([a[0].reshape(num_CV, num_DV), a[1].reshape(num_CV, num_DV)])
        return e[0][x][y]
    return constraint1_5  

c = []
for i in range(num_CV) :
    c.append({'type' : 'ineq', 'fun': constraint_1(i)})
for i in range(num_CV) : 
    c.append({'type' : 'ineq', 'fun': constraint_2(i)})
for i in range(num_DV) :
    c.append({'type' : 'ineq', 'fun': constraint_3(i)})
for i in range(num_CV) :
    for j in range(num_DV) :
        c.append({'type' : 'eq', 'fun': constraint_4(i, j)})
for i in range(num_CV) :
    for j in range(num_DV) :
        c.append({'type' : 'ineq', 'fun': constraint_5(i, j)}) 

############################### objective 2 ###############################

def objective_2_EB(EB, CV, i) :
    e = CV.reshape(num_CV, num_DV)
    p = EB
    return -1.0 * ((t/sto_n[0][i]) * np.log(n*sum(e[i]) - min_cv + 1) - sum(p))

def objective_2_ES(ES, DV, i) :
    e = DV.reshape(num_CV, num_DV)
    p = ES
    return -1.0 * ((sum(a**2 for a in p)/(4*l1) + r_min) - (l1*sum(d**2 for d in e[i]) + l2*sum(e[i])))

def constraint_EB(i) :
    def constraint_2_EB(EB) :
        return EB[i] - initial_bid[0][i]
    return constraint_2_EB

def constraint_ES(i) :
    def constraint_2_ES(ES) :
        return initial_bid[1][i] - ES[i]
    return constraint_2_ES

c_EB = []
for i in range(num_DV) :
    c_EB.append({'type' : 'ineq', 'fun': constraint_EB(i)})

c_ES = []
for i in range(num_CV) :
    c_ES.append({'type' : 'ineq', 'fun': constraint_ES(i)})

############################### double auction ###############################

while flag and not trigger :
    phev = minimize(objective_1, phev, args = (price_vectors,), method='SLSQP', constraints=c).x

    EB = []
    ES = []
    CV = phev[0:num_CV*num_DV]
    DV = phev[num_DV*num_CV:]
    e = CV.reshape(num_CV, num_DV)
    f = DV.reshape(num_CV, num_DV)
    
    for i in range(num_CV) :
        a = minimize(objective_2_EB, e[i], args =(CV, i,), method='SLSQP', constraints=c_EB).x
        EB.append(a)
    
    for i in range(num_DV) :
        b = minimize(objective_2_ES, f[i], args =(DV, i,), method='SLSQP', constraints=c_ES).x
        ES.append(b)

    RDB = price_vectors[0:num_CV*num_DV].reshape(num_CV, num_DV)
    RDS = price_vectors[num_CV*num_DV:2*num_CV*num_DV].reshape(num_CV, num_DV)

    if (np.all((EB - RDB)/EB < e) and np.all((ES - RDS)/ES < e)) :
        flag = False

    price_vectors = np.concatenate((np.reshape(EB, num_CV*num_DV), np.reshape(ES, num_CV*num_DV)), axis = 0)
    t+=1
    print(t)
   
print()
print()

############################### result ###############################

print("Energy Matrix of CVs : ")
for i in range(0, num_CV*num_DV, num_CV) :
    print(phev[i:i+num_DV])
print()
print()
print("Energy Matrix of DVs : ")
for i in range(num_CV*num_DV, 2*num_CV*num_DV, num_DV) :
    print(phev[i:i+num_CV])
print()
print()

print("Price Matrix (this is what DVs will receive from CVs): ")
for i in range(num_CV*num_DV, 2*num_CV*num_DV, num_DV) :
    print(price_vectors[i:i+num_CV])
print()
print()
print()
print()
############################### Graph plot ###############################

colors = ['red', 'black', 'blue', 'green', 'yellow', 'orange', 'pink', 'brown']

for (i,j) in zip(range(0, num_CV*num_DV, num_CV), range(num_CV)) :
    x = phev[i:i+num_DV]
    y = np.arange(num_CV)
    plt.plot(x, y, 'ro', color = colors[j])
plt.title('CV')
plt.show()

for (i,j) in zip(range(num_CV*num_DV, 2*num_CV*num_DV, num_DV), range(num_CV)) :
    x = phev[i:i+num_DV]
    y = np.arange(num_DV)
    plt.plot(x, y, 'ro', color = colors[j])
plt.title('DV')
plt.show()

for (i,j) in zip(range(num_CV*num_DV, 2*num_CV*num_DV, num_DV), range(num_CV)) :
    x = price_vectors[i:i+num_DV]
    y = np.arange(num_DV)
    plt.plot(x, y, 'ro', color = colors[j])
plt.title('Price')
plt.show()

############################## Transaction Example ###############################

import time
from web3 import Web3, HTTPProvider
import contract_abi

contract_address     = Web3.toChecksumAddress('0x9ac6f75bd5d591b300631b556ea3a70610d38cc7')

input(wallet_private_key)
input(wallet_address)

w3 = Web3(HTTPProvider("https://ropsten.infura.io/"))

contract = w3.eth.contract(address = contract_address, abi = contract_abi.abi)

def send_token_to_address(address, amount):
    nonce = w3.eth.getTransactionCount(wallet_address)

    txn_dict = contract.functions.transfer(address, amount).buildTransaction({
            'gas': 2000000,
            'gasPrice': w3.toWei('40', 'gwei'),
            'nonce': nonce,
            'chainId': 3
    })

    signed_txn = w3.eth.account.signTransaction(txn_dict, wallet_private_key)

    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    txn_receipt = None

    count = 0
    while txn_receipt is None and (count < 30):

        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)

        print(txn_receipt)

        time.sleep(10)


    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    return {'status': 'added', 'txn_receipt': txn_receipt}

if __name__ == '__main__' :
    input(address_1)
    input(address_2)
    send_token_to_address(Web3.toChecksumAddress(address_1), int(price_vectors[num_CV*num_DV]))
    send_token_to_address(Web3.toChecksumAddress(address_2), int(price_vectors[num_CV*num_DV + num_CV]))

