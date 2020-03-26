# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 11:11:08 2020

@author: sangmyeong.lee
"""
from QuantLib import *
import numpy as np
import matplotlib.pyplot as plt

def GenerateCorrelatedPaths(processArray, timeGrid, nPaths):
    times = []; [times.append(timeGrid[t]) for t in range(len(timeGrid))]
    generator = UniformRandomGenerator()
    nProcesses = processArray.size()
    nGridSteps = len(times) -1
    nSteps = nGridSteps * nProcesses
    sequenceGenerator = UniformRandomSequenceGenerator(nSteps, generator)
    gaussianSequenceGenerator = GaussianRandomSequenceGenerator(sequenceGenerator)
    multiPathGenerator = GaussianMultiPathGenerator(processArray, times, gaussianSequenceGenerator)
    paths = np.zeros(shape=(nPaths, nProcesses, len(timeGrid)))
    
    #loop throuth number of paths
    for i in range(nPaths):
        multiPath = multiPathGenerator.next().value()
        for j in range(multiPath.assetNumber()):
            path = multiPath[j]
            paths[i,j,:] = np.array([path[k] for k in range(len(path))])
    
    return paths

def StepDownChecker(tenor_years, monitor_months, autocall_barrier, KI, coupon, simulation_numbers, paths):
    import numpy
    #paths are GenerateCorrelatedPaths object
    #define parameters
    monitor_times = int(tenor_years * 12 / monitor_months)    
    
    #results = [simulation_numbers,autocall_times, payoff, worst_performer, KI, global min of underlying]
    results = []
        
    for n in range(simulation_numbers):
        KI_flag = "not KI"
        
        for m in range(monitor_times):
            monitor_in_nSteps = int(( m + 1) * 252 * monitor_months / 12)
            worst_performer = numpy.min(paths[n,:,monitor_in_nSteps])
            min_underlying = numpy.min(paths[n,:,:monitor_in_nSteps+1])        
                       
            if min_underlying < KI:
                KI_flag = "KI"                          
            
            if worst_performer >= autocall_barrier[m]:
                payoff = coupon * (m + 1) * monitor_months / 12
                results.append([n, m + 1, payoff, worst_performer, KI_flag, min_underlying])
                break
            elif m == monitor_times - 1:
                if KI_flag == "KI":
                    payoff = worst_performer / 100 -1
                    results.append([n, m + 1, payoff, worst_performer, KI_flag, min_underlying])
                else:
                    payoff = coupon * (m + 1) * monitor_months / 12
                    results.append([n, m + 1, payoff, worst_performer, KI_flag, min_underlying])
    return results

tenor = 3 #years
monitor = 6 #months
autocall_barrier = [90, 90, 85, 85, 80, 80] #base = 100
underlying = ["KOSPI200", "HSCEI"]
KI = 50 #if no KI, then set KI to 0
coupon = 0.12

process = []
nProcesses = len(underlying)
correlation = 0.25
spot = [100.0, 100.0]
mue = [0.01, 0.01]
sigma = [0.15, 0.15]
[process.append(GeometricBrownianMotionProcess(spot[i], mue[i], sigma[i])) for i in range(nProcesses)]
matrix = [[1.0, correlation], [correlation, 1.0]]

nSteps = tenor * 252
timeGrid = TimeGrid(tenor, nSteps)
nSimulations = 30000

processArray = StochasticProcessArray(process, matrix)
paths = GenerateCorrelatedPaths(processArray, timeGrid, nSimulations)
#paths[number of paths from 0 to nPaths, number of assets from 0, number of steps from 0 to nSteps]

results = StepDownChecker(tenor, monitor, autocall_barrier, KI, coupon, nSimulations, paths)

for i in range(nSimulations):
    if results[i][4] == "KI":
        print(results[i])


     
                
                
             
                













