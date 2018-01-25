import os
from numpy import savetxt, array
from random import random
import matplotlib.pyplot as plt


#Save two-columns (voltage, current) matrix in a txt and save plot in png
def SaveIV(IVdata, name, notes): 
    
    folder = "Meas"
    if not os.path.exists(folder):
        os.makedirs(folder)
   
    matrixdata=[]            
    for i in range(IVdata.Count):
        volt = IVdata.Items[i].XValue
        curr = IVdata.Items[i].YValues[0]
        matrixdata.append([volt,curr])    
      
    
    rndm = str(int(random()*1000000))
    
    savetxt(str(folder + '/'+ name + '_' + rndm + '.dat'), array(matrixdata), delimiter=',', header = " Voltage (V), Current (mA), "+ notes, newline=os.linesep)
    voltcurr=array(matrixdata)
    
    plt.plot(voltcurr[:,0], voltcurr[:,1], color='r')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (mA)')
    plt.grid(b=False, which='major', color='b', linestyle='--')
    plt.title(notes)
    plt.savefig(str(folder + '/'+ name + '_' + rndm + '.png'))