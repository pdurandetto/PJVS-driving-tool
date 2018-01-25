import clr
import Settings

Settings.SIMULATION = False #this has to be set before importing Graphics
Settings.N_CHANNELS = 15 #number of AWG channels employed, 15 for a 1 V SNIS 13-bit array (there are 2 single junctions)
Settings.NJJ_SUBSECTIONS_LIST = [64,32,16,8,4,2,1,1,128,256,512,1024,2048,4096] #number of junctions of each subarray, starting from V- to V+
Settings.NJJ_SUBSECTIONS_EXPONENTS = [6,5,4,3,2,1,0,7,8,9,10,11,12] # exponents of the binary array from V- to V+, only one single junction is taken into account
Settings.VOLT_MAX_AWG = 12.0 #V for Active Technologies AT-AWG1104
Settings.NOT_BIASED_SINGLE_JUNCTION_POS = 7 #the seventh subsections is the second single junction that is never biased during the waveform synthesis

import Graphics

clr.AddReference("System.Windows.Forms")

from System.Windows.Forms import Application

#For running the Graphic User Interface
PJVS_control = Graphics.PJVS_GUI()
Application.Run(PJVS_control)


