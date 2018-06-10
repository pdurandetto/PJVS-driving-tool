from math import sin, pi, asin
from numpy import arange, log2, sign

import Settings

njj_subarray_list = Settings.NJJ_SUBSECTIONS_LIST
single_jj_off_index = Settings.NOT_BIASED_SINGLE_JUNCTION_POS -1       
QuantumTest_bits = Settings.QUANTIZATION_TEST_BITS

    

#it evaluates the lsb voltage and the maximum voltage by knowing KJ, the microwave frequency and the number of channels
def EvalParameters(freq_RF):
    
    Kj = 483597.90*10**9 #Josephson constant Kj90

    one_jj_volt = (freq_RF*10**9)/Kj #single junction voltage drop
    
    maxvoltage = one_jj_volt * ((sum(njj_subarray_list)-1)) #-1 for the not biased junction  
        
    pars = [one_jj_volt, maxvoltage]
    return(pars)




#It quantizes the voltage required according to the parameters and calculates the voltages that each channel has to provide
#input: voltage value to convert, single junction voltage (LSB), resistance, bias current, number of subsections
#output: array containing the voltage required on each channel
def CalcQuantumVolt(Vx, freqRF, R, I_bias, n_subsections): #Ibias in mA

    PJVS_bit_exp=[] #initialize the list that will contain the exponents
    #it gets a list of the exponents of each subarray, excluding the second single junction. This is needed for the binary conversion
    #as an example: [64, 32, 16, 8, 4, 2, 1, 1, 128, 256, 512, 1024, 2048, 4096] ---------> [6, 5, 4, 3, 2, 1, 0, 7, 8, 9, 10, 11, 12]
    for i in range(len(njj_subarray_list)):
        if i!=single_jj_off_index:
            PJVS_bit_exp.append(int(log2(njj_subarray_list[i])))

        
    bit = n_subsections-1 # because the chip has two single junctions, only one is used
    Vlsb, Vmax= EvalParameters(freqRF)
    
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
    
    if Vx<0.:
        n_bin = [-1*b for b in n_bin] #change sign to the bits 
 
    print(n_bin)
    swap_bits = SwapBits(n_bin, PJVS_bit_exp) #it swaps the binary array according to the array structure defined by PJVS_bit_exp
    
    swap_bits.insert(single_jj_off_index,0) # it inserts the bit=0 for not biasing the second single junction
    PJVS_bit_exp.insert(single_jj_off_index,0)
    #print(swap_bits)
    
    swap_bits.append(0) #this is added for loop calculations requirements    
    for i in range(len(I_bias)):
        I_bias[i].append(0)

    
    #from the bit status of each subsection it evalauates the current matrix index needed
    #swap_bits -----> row index of I_bias
    # 1 ----> row 0; 0 ----> row 1 ; -1 ----> row 2
    I_matrix_row = []
    for k in range(len(swap_bits)):
        if swap_bits[k]==1:
            I_matrix_row.append(int(0)) # n=1
        elif swap_bits[k]==0:
            I_matrix_row.append(int(1)) # n=0
        elif swap_bits[k]==-1:
            I_matrix_row.append(int(2)) # n=-1


    Vtot = n_subsections*[0]
    V = 0    
    for j in range(len(swap_bits)-1):   #It calculates the voltage of each channel
            #V = V+Vlsb*swap_bits[j]*(2)**int(PJVS_bit_exp[j])
            V = V+Vlsb*swap_bits[j]*njj_subarray_list[j]
            Vtot[j] = V + 0.001*R*(I_bias[I_matrix_row[j]][j]-I_bias[I_matrix_row[j+1]][j+1]) #bias current from mA to A, so divided by 1000
    
    return([Vtot, sign(Vx)*Vquantum])
        
    
# it swaps the bits according to the array structure defined by PJVS_bit_exp
#nbin: original bit sequence
def SwapBits(nbin, bit_exp):
    
        bit = len(nbin)    
        nbin_rev = list(reversed(nbin))                
        swap_bin = bit*[0] #initialize
        
        for i in range(bit):
            swap_bin[i] = nbin_rev[int(bit_exp[i])] # bit series resorted according to PJVS_bit_exp
                
        return(swap_bin)




#It calculates the sequence (n_points, n_ch) matrix of voltages required for synthesizing a sinewave, Ibias in mA
def CalcSine(amp, freq, phase, offset, n_points, freqRF, R, I_bias, n_subsections):
    
    freq_sample = freq*n_points   
    period = float(1./freq)
    dt = float(1./freq_sample)
    t = arange(0,period,dt)
    phase_rad = phase*pi/180.

    Vx = [amp*sin(2*pi*freq*i+phase_rad)+offset for i in t]
    Vmatrix = [n_subsections*[0] for j in range(n_points)] #Initialize the matrix that will contain the voltage values for the sequence
    Vquantum = []
    
    for j in range(n_points):
        Vcalc= CalcQuantumVolt(Vx[j], freqRF, R, I_bias, n_subsections)
        Vmatrix[j] = Vcalc[0]    # Save in the matrix the array that contains the voltage values, given by CalcQuantumVolt
        Vquantum.append(Vcalc[1])
    return([Vmatrix,Vquantum]) #Vquantum for the plot of the expected waveform




#It calculates the sequence (n_points, n_ch) matrix of voltages required for synthesizing a triangular wave 
def CalcTriang(amp, freq, phase, offset, n_points, freqRF, R, I_bias, n_subsections):
        
    freq_sample = freq*n_points
    period = 1./freq
    dt = 1./freq_sample
    t=arange(0,period,dt)
    phase_rad = phase*pi/180.
    
    Vx=[offset+2*(amp/pi)*asin(sin(2*pi*freq*i+phase_rad)) for i in t] #triangular wave from sinewave
    
    Vmatrix = [n_subsections*[0] for j in range(n_points)]   #Initialize the matrix that will contain the voltage values for the sequence
    Vquantum = []
    for j in range(n_points):
        Vcalc= CalcQuantumVolt(Vx[j], freqRF, R, I_bias, n_subsections)
        Vmatrix[j] = Vcalc[0]    #Save in the matrix the array that contains the voltage values, given by CalcQuantumVolt
        Vquantum.append(Vcalc[1])
    
    return([Vmatrix,Vquantum]) #Vquantum for the plot of the expected waveform



#It calculates the sequence (n_points, n_ch) matrix of voltages required for synthesizing a squarewave
def CalcSquare(amp, freq, phase, offset, n_points, freqRF, R, I_bias, n_subsections):
    
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
        Vcalc= CalcQuantumVolt(Vx[j], freqRF, R, I_bias, n_subsections)
        Vmatrix[j] = Vcalc[0]    #Save in the matrix the array that contains the voltage values, given by CalcQuantumVolt
        Vquantum.append(Vcalc[1])
        
    return([Vmatrix,Vquantum]) #Vquantum for the plot of the expected waveform
    


#function for executing the quantization test
def QuantumTest(Vlsb, I_bias, n_subsections, R, bit_inversion):
               
    if not bit_inversion:
        qbits = [q for q in QuantumTest_bits] # not qbits=QuantumTest_bits, because I need to create a copy and not to rename it
    else:
        qbits=[-1*q for q in QuantumTest_bits]
    
    qbits.append(0) #this is added for loop calculations requirements
    curr = [i for i in I_bias]
    curr.append(0)
    Vtot = n_subsections*[0]
    V = 0
    
    for j in range(len(qbits)-1):   #It calculates the voltage of each channel
            #V = V+Vlsb*qbits[j]*(2)**int(PJVS_bit_exp[j])
            V = V+Vlsb*qbits[j]*njj_subarray_list[j]
            
            #Vtot[j] = (V + R*(qbits[j]-qbits[j+1])*(I_bias/1000.)) #bias current from mA to A, so divided by 1000
            Vtot[j] = V + 0.001*R*(curr[j]-curr[j+1]) #bias current from mA to A, so divided by 1000
    return Vtot



def userdef_sign(x): # sign function defined by the user since numpy.sign(0) gives 0, but I need alternately 1 and -1
    if x >= 0:
        return 1.
    elif x < 0:
        return -1.


    
    
    

