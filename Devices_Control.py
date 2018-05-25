import clr #clr has been installed by writing "pip install pythonnet". First I had to uninstall the Anaconda clr package with "pip uninstall clr" because of conflict with the names
import visa #for controlling the voltmeter via GPIB interface
import sys
from numpy import diff
import Settings

sim= Settings.SIMULATION #global variable set in Main.py, if sim= True then the program is in simulation mode

if not sim:
    sys.path.insert(0,'C:\\Program Files (x86)\\Active Technologies\\AT-AWG-STUDIO SDK\\Library') #the path where the dll is located
    clr.AddReference('ArbStudioSDK') #dll of Active Technologies AT-AWG1104 

from System import Array, Byte, Double, Decimal,UInt32

if not sim:
    from ActiveTechnologies.Instruments.AWG4000.Control import *

njj_subs_list = Settings.NJJ_SUBSECTIONS_LIST
n_subs = len(njj_subs_list) # number of subsections is equal to the number of channels minus one, 14 in our case

serials=['LCRY2345I00080','LCRY2345I00081','LCRY2345I00082','LCRY2345I00083'] #LCRY2341I00185 (fifth)



masterdev = 1 # from 1 to 4
masterch = 2 # from 1 to 4 for device 1,2,3, for 1 to 3 for the last device (15 channel are used, the last channel of last device is not used and cannot be set as master)
fsample = (1*10**7) # sample frequency 10 M

Vaddr = 9 #GPIB address of nanovoltmeter

#Initialize AWGs and returns [] in the case that no devices were found, otherwise it returns the list of devices
def InitDevices():
   
    deviceset = DeviceSet()
    device = deviceset.DeviceList    
    ndev = device.Count #number of devices
    if (ndev == 0):
        return("no_dev")
   
    else:        
        # resorting the initial list according to the serial numbers order
                
        sort_device = ndev*[device[0]]
        for i in range(ndev):
            for j in range(ndev):
                if device[j].SerialId == serials[i]:
                    sort_device[i] = device[j]
                    if i==masterdev-1: 
                        mastdev = j #index of master device in the original DeviceList object, it could not be correctly sorted, that's why I do it, I need it later
            
        device = Array[Device](sort_device) #overwrite device, now I have a list of Device objects, and NOT a DeviceList object... THAT'S DIFFERENT!!!
        mod_channels= [Functionality.ARB, Functionality.ARB, Functionality.ARB, Functionality.ARB]  # Array for initializing each device 4 channels in ARB modality
        funct = Array[Functionality](mod_channels)
        result=[]
        
        [result.append(i.Initialize(funct)) for i in device]    #Devices initialized by calling Initialize method of AWG library
        
        ndevOK = 0 #counter of the number of devices that were correctly initialized
       
        for i in range(ndev):
            if (result[i].ErrorSource == ErrorCodes.RES_SUCCESS):
                print("\nDevice %s correctly initialized."% device[i].SerialId)
                ndevOK+=1

            else:
                print("\nWARNING: device %s not initialized!"% device[i].SerialId)
        print('\n')
        
        if ndevOK!=ndev: #all devices have to be correctly initialized
            return("err_dev")            
        
        res_master = deviceset.ATXSS_SetMasterChannel(Byte(mastdev), Byte(masterch)) #if masterch set to 0 they are all slaves
        if res_master.ErrorSource != ErrorCodes.RES_SUCCESS :
            print("\nWARNING: Master channel non correctly set!")
            return("ERR_MAST")                
             
        return(device) #it returns the list of devices


#it recalculates the output frequency that could be modified since tre prescaler has limited values, freq_signal in kHz
def RecalcSignalFreq(freq_signal, n_points):

    max_SRP = 16777216 #this is the maximum Sampling Rate Prescaler of AT-AWG1104
    sampl_rate_prescaler = round(fsample/(1000*freq_signal*n_points)) #*1000 ---> from kHz to Hz
    #it must be a number =1,2,4,8,10,...
    if sampl_rate_prescaler % 2 != 0 and sampl_rate_prescaler != 1 :
        sampl_rate_prescaler = int(sampl_rate_prescaler) + int(sampl_rate_prescaler % 2) #round to multiple of 2
        
    elif sampl_rate_prescaler > max_SRP:
        sampl_rate_prescaler = max_SRP
    elif sampl_rate_prescaler < 1:
        sampl_rate_prescaler = 1
    
    rec_freq_signal = float(fsample/(1000*n_points*sampl_rate_prescaler)) # from Hz to kHz
    return([rec_freq_signal, sampl_rate_prescaler]) #rec_freq_signal in kHz


    

#It loads the point on the channels. IN: list of devices, sampling rate, number of points, voltage matrix; OUT: 0 if errors occur, 1 if success        
def Load(devicelist, freq_signal, n_points, Vmatrix):
        
    ncount = 0 #counter of number of employed channels
    result= []   #init array of control booleans
    listchannel = GetListOfChannels(devicelist) #it converts the list of devices into a list of channels
    nchannels = len(listchannel)
    
    if nchannels != n_subs+1: #number of AWG channels must be equal to the number of subsections plus one
        return("ERR_NCH")
    
    for i in range(n_points):
        Vmatrix[i].insert(0,0.) #it insert a (0,0) at the first line, because the first channel is the low one (V-) and it is always 0 V and low impedance for having a short circuit (see later) 
    
    pars_freq = RecalcSignalFreq(freq_signal/1000., n_points)#because freq_signal is in Hz but RecalcSignalFreq requires kHz
    sampl_rate_prescaler = pars_freq[1]
    f_smpl = Decimal(fsample) #cast from float to Decimal needed for the following methods 
    for dev in devicelist: # I have to set the following parameters otherwise the devices are not sync
        res=dev.SetSamplingFrequency(f_smpl, f_smpl, ClockSource.Internal,f_smpl)
        if res[0].ErrorSource != ErrorCodes.RES_SUCCESS:
            return("ERR_FREQ")        
        res= dev.PairLeft.SetFrequencyInterpolation(FrequencyInterpolation.Frequency1X)
        if res.ErrorSource != ErrorCodes.RES_SUCCESS:
            return("ERR_FREQ") 
        res=dev.PairRight.SetFrequencyInterpolation(FrequencyInterpolation.Frequency1X)
        if res.ErrorSource != ErrorCodes.RES_SUCCESS:
            return("ERR_FREQ")         
        res=dev.SetATXSSDeSkewDelay(UInt32(0.))
        if res.ErrorSource != ErrorCodes.RES_SUCCESS:
            return("ERR_FREQ")        


    for ch in range(nchannels): #loop over channels
        channelARB = listchannel[ch]
        if(channelARB == None):
                return(0)
        
        elif channelARB.ChannelFunctionality == Functionality.ARB:
            
            channelARB.SampligRatePrescaler = sampl_rate_prescaler
            
            if ch==0:
                setimp = channelARB.SetOutputImpedance(OutputImpedance.LowImpedance) #first channel, first device, short circuited
            else:                              
                setimp = channelARB.SetOutputImpedance(OutputImpedance.Ohm50) # all other channels set to 50 Ohm
        
            if setimp.ErrorSource != ErrorCodes.RES_SUCCESS:
                return("ERR_IMP")
                
            chan = (n_points)*[0]
                
            #It saves into chan the sequence of the voltages of a channel, it corresponds to a column of Vmatrix
            for j in range(n_points):                                                                               
                chan[j] = (Vmatrix[j][ch])/2. # divided by 2 because Rout=50 Ohm
            
            #if ch==nchannels-1:
            #    print(chan)
            
            wavefrm = WaveformStruct()
            wavefrm.Sample = Array[Double](chan)
            
            
            if ch== 4*(masterdev-1)+masterch-1: #master channel
                markers = [1]
                wavefrm.Marker = Array[Double](markers) #add a marker on a channel, needed for the trigger
                
            wavefrmlist = Array[WaveformStruct]([wavefrm])
            res_load = channelARB.LoadWaveforms(wavefrmlist)
            
            genseq = GenerationSequenceStruct()
            seq = Array[GenerationSequenceStruct]([genseq])
            seq[0].WaveformIndex = 0
            seq[0].Repetitions = 1
            
            channelARB.LoadGenerationSequence(seq, TransferMode.NonReEntrant, True)
                
            if (res_load.ErrorSource == ErrorCodes.RES_SUCCESS):
                result.append(1)
            else:
                result.append(0)
                                
            ncount+=1
            
            channelARB.SetTriggerMode(TriggerMode.Continuous)
            
            if ch == 4*(masterdev-1)+masterch-1: #index of master channel in the list of channels                                
                
                x = channelARB.ATXSSSlaveDisableStartCondition()
                if x.ErrorSource != ErrorCodes.RES_SUCCESS:
                    print("CHANNEL ERROR " + str(ch+1))
                x = channelARB.ATXSSSlaveDisableStopCondition()
                if x.ErrorSource != ErrorCodes.RES_SUCCESS:
                    print("CHANNEL ERROR " + str(ch+1))
                                     
            else:

                x = channelARB.ATXSSSlaveEnableStartCondition(ATXSSEvent.Start) # it starts when master channel starts
                if x.ErrorSource != ErrorCodes.RES_SUCCESS:
                    print("CHANNEL ERROR " + str(ch+1))
                x = channelARB.ATXSSSlaveEnableStopCondition(ATXSSEvent.Stop) # it stops when master channel stops
                if x.ErrorSource != ErrorCodes.RES_SUCCESS:
                    print("CHANNEL ERROR " + str(ch+1))
                    
                #channelARB.SetTriggerMode(TriggerMode.Stepped)
    
    return(result) #it returns an array of 0 and 1 where 0 means that the channel was not loaded correctly, 1 is OK
    

#it converts a list of devices into a list of channels
def GetListOfChannels(devicelist):
    
    channels = []        
    for i in devicelist:
        for j in range(4): #4 is the number of channels per device
            channels.append(i.GetChannel(j))
    if len(channels)>(n_subs+1):
        channels= channels[0:(n_subs+1)] 
    channels = Array[Channel](channels)
    return(channels)


    
#It runs the synthesis of the waveforms on each channels
def Run(devicelist):

    channel_to_run = [1,2,3,4] #channels to run
    channel_to_run = Array[Byte](channel_to_run)
    
    result = []    
    
    for i in range(len(devicelist)):   #loop over devices     
        res_run = devicelist[i].RUN(channel_to_run)
        if res_run.ErrorSource != ErrorCodes.RES_SUCCESS:
            result.append(0)
            print("ERROR RUN DEVICE "+ serials[i])
        else:
            result.append(1)
        devicelist[i].ForceStop(channel_to_run) #it suddenly forces the stop, because it will starts again by forcing the trigger on the master channel in the next lines

    mastch = [masterch]
    mastch = Array[Byte](mastch)
    devicelist[masterdev-1].ForceTrigger(mastch) #it forces the trigger on the masterchannel
    
    return(result)
    
    
    
#Interrompe la generazione dell'onda sul dispositivo. IN: device; OUT: esito dell'operazione
def Stop(devicelist):
    
    result = []
    for i in range(len(devicelist)):   #loop over devices     
        res_stop = devicelist[i].STOP()
        if res_stop.ErrorSource != ErrorCodes.RES_SUCCESS:
            result.append(0)
            print("ERROR STOP DEVICE "+ serials[i])
        else:
            result.append(1)
    
    return(result)



# It initializes the nanovoltmeter Keithley 2182A, setting the NPLC
def InitVoltmeter(nplc):
    
    rm = visa.ResourceManager()
    list_instr = rm.list_resources()
    
    instrument = 'GPIB0::%i::INSTR'%Vaddr #GPIB address of nanovoltmeter
    idn = "KEITHLEY INSTRUMENTS INC.,MODEL 2182A,1197213,C02  /A02  \n"
    
    if instrument in list_instr:
        
        Vmeter = rm.open_resource(list_instr[list_instr.index(instrument)], timeout=10000)
        if Vmeter.query("*IDN?") == idn:
            print("\nVoltmeter correctly initialized " + str(Vmeter.query("*IDN?")))
            
            
            Vmeter.write("*RST")
            Vmeter.write("*CLS")
            Vmeter.write(":SENS:VOLT:RANGE:AUTO ON")
            Vmeter.write(":SENS:VOLT:DIG 8")
            Vmeter.write("VOLT:NPLC "+ str(nplc))

            return(Vmeter)
            
        else:
            print("Voltmeter not found!!!")
            return("ERR_VOLT")

    else:    
        print("Voltmeter not found!!!")
        return("ERR_VOLT")
    
    


def ReadVolt(voltmeter):
    try:
        Vrd = voltmeter.query("READ?")
        return(Vrd)
    except:
        print("Error in voltage reading!!!\n")
        return(0)

    
    

# set impedances for IV characteristics, one channel at 50 Ohm, one channel to low impedance and all the others at high impedance
def SetImpedanceIV(device, subsection_status): #subsection_status: list of 1 or 0, 1 means "ON", 0 means "OFF"

    subsection_status.insert(0,0)
    subsection_status.append(0)
    outp_imp_control= abs(diff(subsection_status)) # list of twelve 0 and two 1: Zero: HighImp; first 1: LowImp, second 1: 50 Ohm                

    channels = GetListOfChannels(device)

    if len(channels) != n_subs+1: #number of AWG channels must be equal to the number of subsections plus one
        return("ERR_NCH")
    
    lowimp_control = False
    
    for i in range(len(channels)): #loop over all channels

        if outp_imp_control[i]==0: # zero ----> high impedance
            setimp = channels[i].SetOutputImpedance(OutputImpedance.HighImpedance)
                           
        if outp_imp_control[i]==1 and lowimp_control == False: #low voltage ----> low impedance
            setimp = channels[i].SetOutputImpedance(OutputImpedance.LowImpedance)
            lowimp_control = True
            
        elif outp_imp_control[i]==1 and lowimp_control == True: #high voltage ----> 50 ohm
            setimp = channels[i].SetOutputImpedance(OutputImpedance.Ohm50)
            active_ch = i # is the index of the unique channel that is active, the one at 50 Ohm that provides voltage to let current flows to the low impedance channel
        
        if setimp.ErrorSource != ErrorCodes.RES_SUCCESS:
            return("ERR_IMP")
        
    return(active_ch) #it returns the position of the channel set to 50 Ohm, that is the only one generating a voltage
   
    
# set impedances for Quantization test, first channel at low impedance, all the others at 50 Ohm
def SetImpedanceTQ(device):

    channels = GetListOfChannels(device)
    for ch in range(len(channels)):
        if ch==0:
            setimp = channels[ch].SetOutputImpedance(OutputImpedance.LowImpedance) #first channel, first device, short circuited
        else:                              
            setimp = channels[ch].SetOutputImpedance(OutputImpedance.Ohm50) # all other channels set to 50 Ohm
    
        if setimp.ErrorSource != ErrorCodes.RES_SUCCESS:
            return("ERR_IMP")        
        if setimp.ErrorSource != ErrorCodes.RES_SUCCESS:
            return("ERR_IMP")
        
    return(0)    
            

def SetVoltageToSubsect(device, active_ch, voltage): # generates the voltage on the active channel, zero to all the others channels
    
    channels = GetListOfChannels(device)
    
    for i in range(len(channels)):
        if i==active_ch:
            
            channels[i].SetOutputVoltage(voltage/2.) # divided by 2 because 50 Ohm
        else:
            channels[i].SetOutputVoltage(0.) 


def SetDCVoltages(device, voltage_array): # generates a dc voltage on the each channel
    
    channels = GetListOfChannels(device)
    
    for i in range(len(channels)):
        
            if i==0 or i> len(voltage_array):
                res=channels[i].SetOutputVoltage(0.)

            else:
                res=channels[i].SetOutputVoltage(voltage_array[i-1]/2.) # divided by 2 because 50 Ohm

            if res.ErrorSource != ErrorCodes.RES_SUCCESS:
                return("ERR_SET_VOLT")
