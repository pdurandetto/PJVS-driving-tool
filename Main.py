import clr
import Settings

Settings.SIMULATION = True #this has to be set before importing Graphics
Settings.NJJ_SUBSECTIONS_LIST = [64,32,16,8,4,2,1,1,128,256,512,1024,2048,4096] #number of junctions of each subarray, starting from V- to V+
Settings.NOT_BIASED_SINGLE_JUNCTION_POS = 8 #the 8th subsections (starting from 1) is the second single junction, that is never biased during the waveform synthesis
Settings.QUANTIZATION_TEST_BITS = [1,1,1,1,1,1,1,1,1,1,1,1,1,-1]# all subarrays biased on 1 step, except the last one that is biased on the -1 step --> the overall voltage should be zero
Settings.VOLT_MAX_AWG = 12.0 #V for Active Technologies AT-AWG1104

import Graphics

clr.AddReference("System.Windows.Forms")

from System.Windows.Forms import Application

#For running the Graphic User Interface
PJVS_control = Graphics.PJVS_GUI()
Application.Run(PJVS_control)


