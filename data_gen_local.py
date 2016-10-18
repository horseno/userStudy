import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
import math 
import seaborn as sns



def raw_data(mean,std,N):
    """generate 100 samples within 2 stds from mean"""
    x=[]
    for i in range(N):
        xi = np.random.normal(mean,std,1)[0]
        while ((xi>mean+2*std) or (xi<mean-2*std)):
            xi = np.random.normal(mean,std,1)[0]
        x.append(xi)
    return np.array(x)

def gen_y(x,y,r):
    ## from Rensink's paper, not really working for now...
    lam =( r- math.sqrt(r**2- r**4) )/ (2*r*r -1)
    yy = []
    for ind,xi in enumerate(x):
        temp = (lam *xi + (1-lam)*y[ind] )/math.sqrt(lam*lam +(1-lam)*(1-lam))
        yy.append(temp) 
    return yy

def gen_y_2(x,y,r):
    ## from Harrison's paper 
    r_z = pearsonr(x,y)[0]
    lam =( (r_z -1)*(r**2 +r_z) + math.sqrt((r**2)*(r_z**2-1)*(r**2-1)) )/( (r_z-1)*(2*r**2+r_z -1) )
    yy = []
    for ind,xi in enumerate(x):
        temp = (lam *xi + (1-lam)*y[ind] )/math.sqrt(lam*lam +(1-lam)*(1-lam))
        yy.append(temp) 
    return yy

def data_gen(r,N):
    """Generating N samples with pearsonr r. Using Lane Harrison's method with iteration
    mean set to 0.5, std set to 0.2."""
    MARGIN = 0.0001
    x = raw_data(0.5,0.2,N)
    y = raw_data(0.5,0.2,N) 

    tempy = gen_y_2(x,y,r)
    currentR = pearsonr(x,tempy)[0]
    while (abs(currentR-r)>MARGIN):
        tempy= gen_y_2(x,tempy,r)
        currentR = pearsonr(x,tempy)[0]
    return x,tempy 
    
def scatterPlot(r1,r2,N):
    """return the scatterplot of a given correlation, sample size N"""
    x1,y1 = data_gen(r1,N)
    x2,y2 = data_gen(r2,N)
    print max(x1), max(y1)
    print max(x2), max(y2)
    fig = plt.figure(figsize=(11,5))

    ax1 = fig.add_subplot(121)
    ax1.axis('equal')
    ax1.scatter(x1,y1)    
    #plt.title(str(r1))

    ax2 = fig.add_subplot(122)
    ax2.scatter(x2,y2)
    ax2.axis('equal')  
    #plt.title(str(r2))


    ax1.set_xlim([0,1])
    ax2.set_xlim([0,1])
    ax1.set_ylim([0,1])
    ax2.set_ylim([0,1])
    plt.show()
    return fig
#####

def logNorm(num,maxValue):
    return np.sign(num)*math.log(abs(num)+1)/math.log(maxValue+1)
def linear(num,maxValue):
    return num/float(maxValue)

def getBinned(r,N,domain,transFunc):
    """get a binned data(histogram) with correlation r and sample size N"""
    x, y = data_gen(r,N)
    assert len(x) == len(y),"x and y needed to be of the same length"
    arr,xedges,yedges = np.histogram2d(x,y,bins=[domain,domain])
    arr = np.rot90(arr)
    arr = arr.astype('float')
    maxValue = arr.max()
    #apply transform 
    transFunc = np.vectorize(transFunc)
    arr = transFunc(arr,maxValue)

    return arr

def binnedScatterPlot(r1,r2,N,domain,transFunc):
    """return the scatterplot of a given correlation"""
    arr1 = getBinned(r1,N,domain,logNorm)
    arr2 = getBinned(r2,N,domain,logNorm)

    fig = plt.figure(figsize=(11,5))

    ax1 = fig.add_subplot(121)

    sns.heatmap(arr1, square = True,center =0,vmax =1,xticklabels= False,yticklabels=False,cbar=False,\
                      linewidths=0.0,ax= ax1)
    ax1.set_title("r = "+str(r1))
    ax2 = fig.add_subplot(122)
     
    sns.heatmap(arr2, square = True,center =0,vmax =1,xticklabels= False,yticklabels=False,cbar=False,\
                      linewidths=0.0,ax= ax2)
    ax2.set_title("r = "+str(r2))

    plt.show()
    fig.savefig("70_100")
    return fig

#scatterPlot(0.8,0.5,100)
#binned(0.8,10000,100,logNorm)
binnedScatterPlot(0.7,1,500,50,logNorm)