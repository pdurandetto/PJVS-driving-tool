from math import sin, pi, asin
from numpy import arange

import Settings
PJVS_bit_exp = Settings.NJJ_SUBSECTIONS_EXPONENTS #list of exponents of the binary array
single_jj_off_index = Settings.NOT_BIASED_SINGLE_JUNCTION_POS        


        
#Calcola il Sampling Rate e la tensione di ogni giunzione. IN: frequenza RF in GHz, frequenza del segnale da generare in Hz e il numero di punti;
#OUT: array, dove in [0] c'e' il sampling rate e in [1] la tensione

#it evaluates the lsb voltage and the maximum voltage by knowing KJ, the microwave frequency and the number of channels
def Eval_Parameters(freq_RF, nch):
    
    Kj = 483597.8525*10**9 #Costante di Josephson

    one_jj_volt = (freq_RF*10**9)/Kj #single junction voltage drop
    
    if nch!=0:
        maxvoltage =  one_jj_volt * ((2**(nch-1)-1)) # n_ch-1 are the actual bits, since one of the two single junctions are not biased
    else:
        maxvoltage = 0
        
    pars = [one_jj_volt, maxvoltage]
    return(pars)




#It quantizes the voltage required according to the parameters and calculates the voltages that each channel has to provide
#input: voltage value to convert, single junction voltage (LSB), resistance, bias current, number of subsections
#output: array containing the voltage required on each channel
def CalcQuantumVolt(Vx, Vlsb, R, I_bias, n_subsections): #Ibias in A
        
    bit = n_subsections-1 # because the chip has two single junctions, only one is used
    Vmax = Vlsb*(2**bit-1) #Vmax full-scale value, i.e. max voltage achievable with the array
    
    if abs(Vx) > Vmax:   
        if Vx > 0 :
            Vx = Vmax
        else:
            Vx= -Vmax

    n_lsb = abs(round(Vx/Vlsb))  #number of lsb closest to Vx, discretization  
    Vquantum = n_lsb*Vlsb #closest quantum voltage    
    n_bin = bit*[0]
    
    for n in range(bit-1,-1,-1):  #it converts the number into a binary array
        n_bin[n] = n_lsb % 2
        n_lsb = int(n_lsb/2)
    
    swap_bits = SwapBits(n_bin) #it swaps the binary array according to the array structure defined by PJVS_bit_exp
    
    swap_bits.insert(single_jj_off_index,0) # it inserts the bit=0 for not biasing the first single junction
    PJVS_bit_exp.insert(single_jj_off_index,0)

    
    swap_bits.append(0) #this is added for loop calculations requirements
    Vtot = n_subsections*[0]
    V = 0
            
    for j in range(len(swap_bits)-1):   #It calculates the voltage of each channel
            V = V+Vlsb*swap_bits[j]*(2)**int(PJVS_bit_exp[j])
            Vtot[j] = (V + R*(swap_bits[j]-swap_bits[j+1])*I_bias)  
    
    if Vx >= 0: #if the input voltage is positive...
        return([Vtot,Vquantum])
        
    else: #if it is negative...
        Vtot_neg=[-i for i in Vtot] 
        return([Vtot_neg, -1.*Vquantum]) #I need Vquantum for viewing the expected waveform plot


    
# it swaps the bits according to the array structure defined by PJVS_bit_exp and add a bit=0 for the first single junction
#nbin: original bit sequence
def SwapBits(nbin):
    
        bit = len(nbin)    
        nbin_rev = list(reversed(nbin))                
        swap_bin = bit*[0] #initialize
        
        for i in range(bit):
            swap_bin[i] = nbin_rev[int(PJVS_bit_exp[i])] # bit series resorted according to PJVS_bit_exp
                
        return(swap_bin)




#It calculates the sequence (n_points, n_ch) matrix of voltages required for synthesizing a sinewave, Ibias in A
def Calc_Sine(amp, freq, phase, offset, n_points, Vlsb, R, I_bias, n_subsections):
    
    freq_sample = freq*n_points   
    period = float(1./freq)
    dt = float(1./freq_sample)
    t = arange(0,period,dt)
    phase_rad = phase*pi/180.

    Vx = [amp*sin(2*pi*freq*i+phase_rad)+offset for i in t]
    Vmatrix = [n_subsections*[0] for j in range(n_points)] #Initialize the matrix that will contain the voltage values for the sequence
    Vquantum = []
    
    for j in range(n_points):
        Vcalc= CalcQuantumVolt(Vx[j], Vlsb, R, I_bias, n_subsections)
        Vmatrix[j] = Vcalc[0]    # Save in the matrix the array that contains the voltage values, given by CalcQuantumVolt
        Vquantum.append(Vcalc[1])
        
    return([Vmatrix,Vquantum]) #Vquantum for the plot of the expected waveform




#It calculates the sequence (n_points, n_ch) matrix of voltages required for synthesizing a triangular wave 
def Calc_Triang(amp, freq, phase, offset, n_points, Vlsb, R, I_bias, n_subsections):
        
    freq_sample = freq*n_points
    period = 1./freq
    dt = 1./freq_sample
    t=arange(0,period,dt)
    phase_rad = phase*pi/180.
    
    Vx=[2*(amp/pi)*asin(sin(2*pi*freq*i+phase_rad)) for i in t] #triangular wave from sinewave
    
    Vmatrix = [n_subsections*[0] for j in range(n_points)]   #Initialize the matrix that will contain the voltage values for the sequence
    Vquantum = []
    for j in range(n_points):
        Vcalc= CalcQuantumVolt(Vx[j], Vlsb, R, I_bias, n_subsections)
        Vmatrix[j] = Vcalc[0]    #Save in the matrix the array that contains the voltage values, given by CalcQuantumVolt
        Vquantum.append(Vcalc[1])
    
    return([Vmatrix,Vquantum]) #Vquantum for the plot of the expected waveform



#It calculates the sequence (n_points, n_ch) matrix of voltages required for synthesizing a squarewave
def Calc_Square(amp, freq, phase, offset, n_points, Vlsb, R, I_bias, n_subsections):
    
    freq_sample = freq*n_points   
    period = 1./freq
    dt = 1./freq_sample
    t=arange(0,period,dt)
    phase_rad = phase*pi/180.
    Vx=[]
   
    first_zero = True
    
    for i in t:       
        arg= sin(2*pi*freq*i+phase_rad)

        if arg==0. and first_zero:
            Vx.append(amp*userdef_sign(arg)+offset)
            first_zero = False
        elif abs(arg)<10**(-12) and not first_zero:
            Vx.append(-1.*amp*userdef_sign(arg)+offset)
            first_zero = True
        else:
            Vx.append(amp*userdef_sign(arg)+offset)
                
    Vmatrix = [n_subsections*[0] for j in range(n_points)]   #Initialize the matrix that will contain the voltage values for the sequence
    Vquantum = []
    for j in range(n_points):
        Vcalc= CalcQuantumVolt(Vx[j], Vlsb, R, I_bias, n_subsections)
        Vmatrix[j] = Vcalc[0]    #Save in the matrix the array that contains the voltage values, given by CalcQuantumVolt
        Vquantum.append(Vcalc[1])
        
    return([Vmatrix,Vquantum]) #Vquantum for the plot of the expected waveform
    

def userdef_sign(x): # sign function defined by the user since numpy.sign(0) gives 0, but I need alternately 1 and -1
    if x >= 0:
        return 1.
    elif x < 0:
        return -1.

