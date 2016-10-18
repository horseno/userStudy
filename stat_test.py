import scipy.stats
import numpy as np

#def single_test(X,Y):
#    F = np.var(X) / np.var(Y)
#    alpha = 0.15 #Or whatever you want your alpha to be.
#    p_value = scipy.stats.f.cdf(F, len(X)-1, len(Y)-1)
#    if p_value > alpha:
#        print p_value
#        return False
#    else:
#        print p_value
#        return True

def F_test(arr):
    """return true if the arr passes the F-test, i.e, p-value< alpha
    The seq is divided into three subgroups""" 

    l = len(arr)
    arr = np.array(arr)
    gl = l/3
    X= arr[0:gl]
    Y= arr[gl:2*gl] 
    Z= arr[2*gl:]

    var_of_mean = np.var(np.array([X.mean(),Y.mean(),Z.mean()]))

    xv = np.var(X)
    yv = np.var(Y)
    zv = np.var(Z)

    ratio = var_of_mean/np.array([xv,yv,zv]).mean()
    #print ratio
    return ratio




#for i in range(26):
#    arr1 = arr[i:i+24]
#    #print arr1,i
#    #print len(arr)  
#    print i 
#    ratio = F_test(arr1)
#    if ratio<0.25:
#        print arr[i:i+24].mean()
#        print arr[i:i+24]
#        break#

#print arr[-24:]
#print arr[-24:].mean()
