#GRAPHICS PART
import clr
import Math_Functions
import Devices_Control
from numpy import diff, arange, sign, array, mean, std, transpose, float
from System import Array, EventArgs, Decimal
import time #needed for simulation 
from random import uniform #needed for simulation
import Settings
import os

clr.AddReference("System.IO")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.IO import StreamWriter, StreamReader
from System.Drawing import Point, Size, Font, Color, ContentAlignment, FontStyle
from System.Windows.Forms import Application, Form, Button, Label,TextBox, StatusBar, MessageBox, Panel, RadioButton, DataVisualization, GroupBox, PictureBox, CheckBox, NumericUpDown, PictureBoxSizeMode, CloseReason, SaveFileDialog, OpenFileDialog, DialogResult

Graph = DataVisualization.Charting

sim= Settings.SIMULATION #global variable set in Main.py, if sim= True then the program is in simulation mode
vmax_awg = Settings.VOLT_MAX_AWG
njj_subs_list = Settings.NJJ_SUBSECTIONS_LIST
QuantumTest_bits = Settings.QUANTIZATION_TEST_BITS

n_subs = len(njj_subs_list) # number of subsections is equal to the number of channels minus one, 14 in our case
#n_ch = n_subs+1 # the channels are the number of subsections plus one


class PJVS_GUI(Form):
        def __init__(self):
            
            self.Text = "PJVS Waveform Synthesis"
            self.Name = "PJVS Waveform Synthesis"
            self.Size = Size(920, 700)
            self.CenterToScreen()
            
            self.Vmatrix=[] #initialization of the (n,m) matrix of voltages, where n is the number of points and m is the number of channels (14)
            self.running= False #if True the waveform synthesis is running
            

            #Button for AWGs initialization
            self.btn_INIT = Button()
            self.btn_INIT.Text = "INITIALIZE \n AWGs"
            self.btn_INIT.Font = Font("Serif", 12.)
            self.btn_INIT.BackColor = Color.White
            self.btn_INIT.Location = Point(30, 40)
            self.btn_INIT.Size = Size (150, 75)
            self.btn_INIT.Click += self.Call_InitAWGs
            if sim:
                self.btn_INIT.Enabled = False
            else:
                self.btn_INIT.Enabled = True
            
            self.Controls.Add(self.btn_INIT)

           
            #Title of section
            self.msg1 = Label()
            self.msg1.Text = "Operating parameters:"
            self.msg1.Font = Font("Serif", 15.)
            self.msg1.Location = Point(20, 160)
            self.msg1.AutoSize = True
            
            self.Controls.Add(self.msg1)
            
            #Microwave frequency in GHz
            self.freqRF = Label()
            self.freqRF.Text = "RF frequency (GHz): "
            self.freqRF.Font = Font("Serif", 11.)
            self.freqRF.Location = Point(20, 200)
            self.freqRF.AutoSize = True
            
            self.Controls.Add(self.freqRF)
            
            self.in_freqRF = TextBox()
            self.in_freqRF.Text = "76.5" #GHz
            self.in_freqRF.Location = Point(220, 200)
            self.in_freqRF.Size = Size(100, 10)
            self.in_freqRF.Leave += self.Set_in_freqRF_Format
            
            self.Controls.Add(self.in_freqRF)
            

            
            #Button for editing the bias currents required for each subsection, it opens a new form where currents can be set, saved and loaded
            self.btn_edit_currents = Button()
            self.btn_edit_currents.Text = "Edit bias currents"
            self.btn_edit_currents.Font = Font("Serif", 11.)
            self.btn_edit_currents.BackColor = Color.White
            self.btn_edit_currents.Location = Point(90, 230)
            self.btn_edit_currents.Size = Size(170,30)
            self.btn_edit_currents.Click += self.OpenFormBC

           
            self.Controls.Add(self.btn_edit_currents)
            
            #Signal frequency in kHz
            self.freq_signal = Label()
            self.freq_signal.Text = "Signal frequency (kHz):"
            self.freq_signal.Font = Font("Serif", 11.)
            self.freq_signal.Location = Point(20, 280)
            self.freq_signal.AutoSize = True
            
            self.Controls.Add(self.freq_signal)
            
            self.in_freq_signal = TextBox()
            self.in_freq_signal.Text = "1" #kHz
            self.in_freq_signal.Location = Point(220, 280)
            self.in_freq_signal.Size = Size(100, 10)
            self.in_freq_signal.Leave += self.Set_in_freq_signal_Format
            self.Controls.Add(self.in_freq_signal)
            
            #Signal amplitude in V
            self.amp_signal = Label()
            self.amp_signal.Text = "Signal amplitude (V):"
            self.amp_signal.Font = Font("Serif", 11.)
            self.amp_signal.Location = Point(20, 310)
            self.amp_signal.AutoSize = True
                       
            self.Controls.Add(self.amp_signal)
            
            self.in_amp_signal = TextBox()
            self.in_amp_signal.Text = "1"  #V
            self.in_amp_signal.Location = Point(220, 310)
            self.in_amp_signal.Size = Size(100, 10)
            self.in_amp_signal.Leave += self.Set_in_volt_Format
            
            self.Controls.Add(self.in_amp_signal)

            #Signal phase in degrees
            self.phase = Label()
            self.phase.Text = "Signal phase (°):"
            self.phase.Font = Font("Serif", 11.)
            self.phase.Location = Point(20, 340)
            self.phase.AutoSize = True
            
            self.Controls.Add(self.phase)
            
            self.in_phase = TextBox()
            self.in_phase.Text = "0" #°
            self.in_phase.Location = Point(220, 340)
            self.in_phase.Size = Size(100, 10)
            self.in_phase.Leave += self.Set_in_phase_Format
            
            self.Controls.Add(self.in_phase)


            #Signal offset in V
            self.offset = Label()
            self.offset.Text = "Offset (V):"
            self.offset.Font = Font("Serif", 11.)
            self.offset.Location = Point(20, 370)
            self.offset.AutoSize = True
            
            self.Controls.Add(self.offset)
            
            self.in_offset = TextBox()
            self.in_offset.Text = "0" #V
            self.in_offset.Location = Point(220, 370)
            self.in_offset.Size = Size(100, 10)
            self.in_offset.Leave += self.Set_in_volt_Format
            self.Controls.Add(self.in_offset)

            #Number of steps
            self.n_steps = Label()
            self.n_steps.Text = "Steps per period \n (even number)"
            self.n_steps.Font = Font("Serif", 11.)
            self.n_steps.Location = Point(20, 400)
            self.n_steps.AutoSize = True
            
            self.Controls.Add(self.n_steps)
            
            self.in_n_steps = TextBox()
            self.in_n_steps.Text = "20"
            self.in_n_steps.Location = Point(220, 400)
            self.in_n_steps.Size = Size(100, 10)
            self.in_n_steps.Leave += self.Set_in_n_steps_Format
            self.Controls.Add(self.in_n_steps)


            #Plot Vt of the expected waveform
            self.plotVt = Graph.Chart()
            self.plotVt.Location = Point(350, 120)
            self.plotVt.Size = Size (520, 330)
            
            self.area=Graph.ChartArea()
            self.plotVt.ChartAreas.Add(self.area)
            self.area.AxisX.Minimum = 0
            self.area.AxisX.Maximum = 0.001
            self.area.AxisX.Interval = 0.0002
            self.area.AxisX.MajorGrid.LineColor = Color.White
            self.area.AxisX.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            self.area.AxisX.Title = 'Time (s)'
            self.area.AxisX.TitleFont = Font("Serif", 12.)
            self.area.AxisY.Minimum = -1.
            self.area.AxisY.Maximum = 1.
            self.area.AxisY.Interval = 0.2
            self.area.AxisY.MajorGrid.LineColor = Color.White
            self.area.AxisY.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            self.area.AxisY.Title = 'Voltage (V)'
            self.area.AxisY.TitleFont = Font("Serif", 12.)            
            self.area.BackColor = Color.Black

            
            self.series = Graph.Series("Vt")
            self.series.ChartType = Graph.SeriesChartType.Line
            self.series.Color = Color.LightGreen
            self.series.BorderWidth = 3
            
            self.plotVt.Series.Add(self.series)
            self.series.Points.AddXY(0.,0.)            
            self.Controls.Add(self.plotVt)
            

            # Sampling frequency from Devices_Control
            self.lab_f_Sample = Label()
            self.lab_f_Sample.Text = "Sampling Frequency: %e" % Devices_Control.fsample
            self.lab_f_Sample.Font = Font("Serif", 11.)
            self.lab_f_Sample.Location = Point(20, 480)
            self.lab_f_Sample.AutoSize = True
            
            self.Controls.Add(self.lab_f_Sample)

            # Sampling rate prescaler
            self.lab_sampl_rate_presc = Label()
            self.lab_sampl_rate_presc.Text = "Sampling Rate Prescaler: "
            self.lab_sampl_rate_presc.Font = Font("Serif", 11.)
            self.lab_sampl_rate_presc.Location = Point(20, 510)
            self.lab_sampl_rate_presc.AutoSize = True
            
            self.Controls.Add(self.lab_sampl_rate_presc)
            
            #Single junction voltage
            self.lab_single_junct_volt = Label()
            self.lab_single_junct_volt.Text = "Single junction voltage: "
            self.lab_single_junct_volt.Font = Font("Serif", 11.)
            self.lab_single_junct_volt.Location = Point(20, 540)
            self.lab_single_junct_volt.AutoSize = True
            
            self.Controls.Add(self.lab_single_junct_volt)
            
            #Maximum voltage
            self.lab_voltage_max = Label()
            self.lab_voltage_max.Text = "Maximum voltage: "
            self.lab_voltage_max.Font = Font("Serif", 11.)
            self.lab_voltage_max.Location = Point(20, 570)
            self.lab_voltage_max.AutoSize = True
            
            self.Controls.Add(self.lab_voltage_max)

         
            
            #groupbox
            self.groupbox_waveform = GroupBox()
            self.groupbox_waveform.Text = "Waveform type"
            self.groupbox_waveform.Name = "Waveform type"
            self.groupbox_waveform.Font = Font("Serif", 12.)
            self.groupbox_waveform.Location = Point(350, 470)
            self.groupbox_waveform.Size = Size(150,150)
            self.Controls.Add(self.groupbox_waveform)

            self.radio_sin = RadioButton()
            self.radio_sin.Text = "Sinewave"
            self.radio_sin.Font = Font("Serif", 12.)
            self.radio_sin.Location = Point(20, 20)
            self.radio_sin.Size = Size (120, 50)
            self.radio_sin.GroupName = "Waveform type"
            self.radio_sin.Checked = True
            self.waveform = "SIN"
            self.radio_sin.CheckedChanged += self.checked_waveform

            self.radio_sqr = RadioButton()
            self.radio_sqr.Text = "Squarewave"
            self.radio_sqr.Font = Font("Serif", 12.)
            self.radio_sqr.Location = Point(20, 55)
            self.radio_sqr.Size = Size (120, 50)
            self.radio_sqr.GroupName = "Waveform type"            
            self.radio_sqr.CheckedChanged += self.checked_waveform

            self.radio_trng = RadioButton()
            self.radio_trng.Text = "Triangwave"
            self.radio_trng.Font = Font("Serif", 12.)
            self.radio_trng.Location = Point(20, 90)
            self.radio_trng.Size = Size (120, 50)
            self.radio_trng.GroupName = "Waveform type"                        
            self.radio_trng.CheckedChanged += self.checked_waveform

            self.groupbox_waveform.Controls.Add(self.radio_sin)
            self.groupbox_waveform.Controls.Add(self.radio_sqr)
            self.groupbox_waveform.Controls.Add(self.radio_trng)
          
            #Button for loading the voltage matrix on AWGs channels
            self.btn_LOAD = Button()
            self.btn_LOAD.Text = "LOAD \n WAVEFORM"
            self.btn_LOAD.Font = Font("Serif", 12.)
            self.btn_LOAD.BackColor = Color.White
            self.btn_LOAD.Location = Point(550, 500)
            self.btn_LOAD.Size = Size (150, 75)
            
            if sim:
                self.btn_LOAD.Enabled = True   #SIMULATION
            else:
                self.btn_LOAD.Enabled = False
                
            self.btn_LOAD.Click += self.Call_EvalParameters
            self.btn_LOAD.Click += self.Call_Load
            
            self.Controls.Add(self.btn_LOAD)
            
            #RUN button: runs AWGs channels
            self.btn_RUN = Button()
            self.btn_RUN.Text = "RUN \n WAVEFORM"
            self.btn_RUN.Font = Font("Serif", 12.)
            self.btn_RUN.BackColor = Color.LimeGreen
            self.btn_RUN.Location = Point(720, 500)
            self.btn_RUN.Size = Size (150, 75)
            self.btn_RUN.Enabled = 0
            self.btn_RUN.Click += self.Call_Run
            
            self.Controls.Add(self.btn_RUN)


            #INRIM_logo
            self.logo = PictureBox()
            self.logo.Location = Point(500, 20)
            self.logo.Size = Size (240, 80)
            self.logo.SizeMode = PictureBoxSizeMode.StretchImage
            #self.logo.Autosize = True
            self.logo.Load("logo_inrim.jpg")
            self.Controls.Add(self.logo)
            
            #Status bar
            self.sb = StatusBar()
            self.sb.Text = "Ready"
            self.sb.Location = Point(20, 20)
            
            self.Controls.Add(self.sb)
            
            self.Closing += self.Call_Stop #form closing by x-clicking stops waveform synthesis            


            #Button on the first form for opening the form where IV characteristics can be performed
            self.btn_IV = Button()
            self.btn_IV.Text = "Check IVs"
            self.btn_IV.Font = Font("Serif", 12.)
            self.btn_IV.BackColor = Color.White
            self.btn_IV.Location = Point(200, 30)
            self.btn_IV.Size = Size (120, 50)
            if sim:        
                self.btn_IV.Enabled = True      # SIMULATION
            else:
                self.btn_IV.Enabled = False
                
            self.btn_IV.Click += self.OpenFormIV
            self.Controls.Add(self.btn_IV)


            #Button on the first form for opening the form where quantization test is performed
            self.btn_QT = Button()
            self.btn_QT.Text = "Test Quantization"
            self.btn_QT.Font = Font("Serif", 12.)
            self.btn_QT.BackColor = Color.White
            self.btn_QT.Location = Point(200, 80)
            self.btn_QT.Size = Size (120, 50)
            if sim:        
                self.btn_QT.Enabled = True      # SIMULATION
            else:
                self.btn_QT.Enabled = False
                
            self.btn_QT.Click += self.OpenFormQT
            self.Controls.Add(self.btn_QT)

            I_bias_pos=[]
            I_bias_zero=[]
            I_bias_neg=[]
            for j in range(n_subs):
                I_bias_pos.append(1.000) #mA
                I_bias_zero.append(0.000) #mA
                I_bias_neg.append(-1.000) #mA
                
            self.I_bias_tot = [I_bias_pos, I_bias_zero, I_bias_neg] 

            
            #function called for formatting the textboxes
            self.Call_EvalParameters(self,self) #called for evaluating parameters as soon as the form is opened, any two arguments are required although not used
            self.Set_in_freqRF_Format(self,self)
            #self.Set_in_current_Format(self,self)
            self.Set_in_freq_signal_Format(self,self)
            self.Set_in_volt_Format(self,self)
            self.Set_in_phase_Format(self,self)
            self.Set_in_n_steps_Format(self,self)
            
########################################################################### end of constructor
            
            
        #functions for formatting the textboxes    
        def Set_in_freqRF_Format(self, sender, args):
            number = '{0:.3f}'.format(float(self.in_freqRF.Text))
            self.in_freqRF.Text = str(number)
            self.Call_EvalParameters(self,self)
            self.Set_in_volt_Format(self, self)
            
        def Set_in_current_Format(self, sender, args):
            number = '{0:.3f}'.format(float(sender.Text))
            sender.Text = str(number)

        def Set_in_freq_signal_Format(self, sender, args):
            # it recalculates the frequency according to Sampling Rate Prescaler, signal frequency and number of points, having fixed the sample rate            
            number = '{0:.6f}'.format(self.Call_RecalcFreq(self,self))
            self.in_freq_signal.Text = str(number)
            
        #It calls QuantumVolt for quantizing the voltage
        def Set_in_volt_Format(self, sender, args):
            
            Vamp = float(self.in_amp_signal.Text)
            Voffset = float(self.in_offset.Text)            
            Vamp_q= Math_Functions.CalcQuantumVolt(Vamp, float(self.in_freqRF.Text), 50, self.I_bias_tot, n_subs)[1] #current in mA, element 1 of the output of CalcQuantumVolt
            Voffset_q= Math_Functions.CalcQuantumVolt(Voffset, float(self.in_freqRF.Text), 50, self.I_bias_tot, n_subs)[1]                   
                        
            if (abs(Vamp_q)+abs(Voffset_q))>self.volt_max:
                if sender==self.in_offset:
                    Voffset_q = Math_Functions.CalcQuantumVolt(sign(Voffset_q)*(self.volt_max-abs(Vamp_q)),float(self.in_freqRF.Text), 50, self.I_bias_tot, n_subs)[1]
                    
                elif sender==self.in_amp_signal:
                    Vamp_q = Math_Functions.CalcQuantumVolt(sign(Vamp_q)*(self.volt_max-abs(Voffset_q)), float(self.in_freqRF.Text), 50, self.I_bias_tot, n_subs)[1]
                    
            self.in_amp_signal.Text = '{0:.6f}'.format(Vamp_q)
            self.in_offset.Text = '{0:.6f}'.format(Voffset_q)



        def Set_in_phase_Format(self, sender, args):
            number = '{0:.3f}'.format(float(self.in_phase.Text))
            self.in_phase.Text = str(number) 

        # it recalculates the frequency according to Sampling Rate Prescaler, signal frequency and number of points, having fixed the sample rate 
        def Set_in_n_steps_Format(self, sender, args):
            
            np = round(float(self.in_n_steps.Text))
            
            if np<8: # 8 is the minimum number of points (steps) that is possible to load on the AWGs ...
                np = 8
            
            if np%2!= 0: # ... and it has to be a even number! odd doesn't work!
                np = np-1
             
            
            self.in_n_steps.Text = '{0:d}'.format(np)
            self.Set_in_freq_signal_Format(self,self)

        
        def checked_waveform(self, sender, args): #function for selecting the waveform type
            if not sender.Checked:
                return
            
            if sender.Text == "Sinewave":
                self.waveform = "SIN" # 0: SIN; 1: SQR; 2: TRN;
                
            if sender.Text == "Squarewave":
                self.waveform = "SQR" # 0: SIN; 1: SQR; 2: TRN;
                
            if sender.Text == "Triangwave":
                self.waveform = "TRN" # 0: SIN; 1: SQR; 2: TRN;
                


        #It calculates sampling rate and single junction voltage drop. It uses EvalParameters defined in module Math_Functions.
        def Call_EvalParameters(self, sender, args):
            
            freqRF = float(self.in_freqRF.Text)
            freq_signal = float(self.in_freq_signal.Text) #kHz
            n_steps = int(self.in_n_steps.Text)            
            
            Param_array = Math_Functions.EvalParameters(freqRF)
            
            #self.srp = Param_array[0] #sample rate prescaler
            self.single_jj_volt = Param_array[0]
            self.volt_max = Param_array[1]
                            
            # Write on the form the calculated values of parameters and change button colors
            self.lab_sampl_rate_presc.Text = "Sampling Rate Prescaler: " + '{0:d}'.format(Devices_Control.RecalcSignalFreq(freq_signal,n_steps)[1])
            self.lab_single_junct_volt.Text = "Single junction voltage: " +'{0:.3f} uV'.format(self.single_jj_volt*10**6)
            self.lab_voltage_max.Text = "Maximum voltage: " +'{0:.6f} V'.format(self.volt_max)
            self.in_n_steps.BackColor = Color.White
            self.btn_LOAD.BackColor = Color.White
            self.btn_RUN.BackColor = Color.LimeGreen

                
        #it recalculates the frequency according to the possible values of prescaler of the AWG employed
        def Call_RecalcFreq(self, sender, args):
            freq = float(self.in_freq_signal.Text)
            np = float(self.in_n_steps.Text)
            pars_freq = Devices_Control.RecalcSignalFreq(freq,np) # freq in kHz
            self.Call_EvalParameters(sender, args)
            return(pars_freq[0])
            
        
        #Initialize AWGs calling InitAWGs function defined in Device_Controls
        def Call_InitAWGs(self, sender, args):
            Application.DoEvents()
            finddev = Devices_Control.InitAWGs() #result of InitAWGs functions
            
            if finddev == "NO_DEV":
                MessageBox.Show("\nWARNING: No device found!")
                return(-1)
            elif finddev == "ERR_DEV": 
                MessageBox.Show("\nWARNING: One or more devices were not correctly initialized!")
                return(-1)
            elif finddev == "ERR_MAST": 
                MessageBox.Show("\nWARNING: Master channel not set!")
                return(-1)          
            else:    
                devicelist = finddev #list of devices          
                ndev = len(devicelist) #number of devices
                
                #Si controlla l'esito dell'inizializzazione e si modifica la barra di stato inferiore
                if (ndev == 0):
                    self.sb.Text = "Result: No device found"
                else:
                    self.sb.Text = "Result: %i device(s) correctly initialized" % ndev
                    
                    self.device = devicelist    #because I need it in LOAD function                    
                    self.btn_LOAD.Enabled = True
                    self.btn_IV.Enabled = True
                    self.btn_QT.Enabled = True
                sender.BackColor = Color.LightBlue

                

        #Call Load function in Devices_Control for loading voltage values on AWGs channels
        def Call_Load(self, sender, args):
                
                Application.DoEvents()                
                self.Vmatrix=[] #re-initialization of voltage matrix                
                
                #parameters values            
                amp = float(self.in_amp_signal.Text)
                freq = float(self.in_freq_signal.Text)*1000 #from kHz to Hz
                phase = float(self.in_phase.Text)
                offset = float(self.in_offset.Text)
                n_steps = int(self.in_n_steps.Text)
                freqRF  = float(self.in_freqRF.Text)
                
                R_out = float(50) #output impedance 50 Ohm
                
                                
                if self.waveform == "SIN":
                    Vout = Math_Functions.CalcSine(amp, freq, phase, offset, n_steps, freqRF, R_out, self.I_bias_tot, n_subs)
                    self.Vmatrix = Vout[0]
                    
                if self.waveform == "SQR":
                    Vout = Math_Functions.CalcSquare(amp, freq, phase, offset, n_steps, freqRF, R_out, self.I_bias_tot, n_subs)
                    self.Vmatrix = Vout[0]
                    
                if self.waveform == "TRN":
                    Vout = Math_Functions.CalcTriang(amp, freq, phase, offset, n_steps, freqRF, R_out, self.I_bias_tot, n_subs)
                    self.Vmatrix = Vout[0]
                                
                
                
                period = float(1/freq)
                
                n_rep = 1000 
                Vout_rep=[] #I create this array in order to correctly view the expected waveform on the plot. For doing this I need more points than the real ones
                for i in Vout[1]:
                    for j in range(n_rep): #each point is repeated n_rep times
                        Vout_rep.append(i)
                    
                dt = float(period/n_steps)
                t = arange(0,period,float(dt/n_rep))

                self.series.Points.Clear()
                for i in range(len(Vout_rep)):
                    self.series.Points.AddXY(t[i],Vout_rep[i])

                self.area.AxisX.Minimum = 0.0
                self.area.AxisX.Maximum = period
                self.area.AxisX.Interval = period/5.
                self.area.AxisX.MajorGrid.LineColor = Color.White
                self.area.AxisX.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
                
                if min(Vout_rep)==max(Vout_rep):                    
                    self.area.AxisY.Minimum = min(Vout_rep)-1.
                    self.area.AxisY.Maximum = max(Vout_rep)+1.
                    self.area.AxisY.Interval = (max(Vout_rep)-min(Vout_rep))/10.                    
                else:

                    self.area.AxisY.Minimum = min(Vout_rep)
                    self.area.AxisY.Maximum = max(Vout_rep)
                    self.area.AxisY.Interval = (max(Vout_rep)-min(Vout_rep))/10.
                
                self.area.AxisY.LabelStyle.Format = "0.000"
                self.area.AxisX.LabelStyle.Format = "E0"
                self.area.AxisY.MajorGrid.LineColor = Color.White
                self.area.AxisY.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
                self.area.BackColor = Color.Black
                self.area.CursorX.Interval = 0
                self.area.CursorY.Interval = 0
                self.area.AxisX.ScaleView.Zoomable = True
                self.area.AxisY.ScaleView.Zoomable = True
                self.area.CursorX.IsUserEnabled = True
                self.area.CursorX.IsUserSelectionEnabled = True
                self.area.CursorY.IsUserEnabled = True
                self.area.CursorY.IsUserSelectionEnabled = True
                self.area.CursorX.LineColor = Color.Blue
                self.area.CursorX.LineWidth = 1
                self.area.CursorX.LineDashStyle = Graph.ChartDashStyle.DashDot
                self.area.CursorY.LineColor = Color.Blue
                self.area.CursorY.LineWidth = 1
                self.area.CursorY.LineDashStyle = Graph.ChartDashStyle.DashDot
                
                
                if not sim:
                    result = Devices_Control.Load(self.device, freq, n_steps, self.Vmatrix) #Call Load function defined in Devices_Control, it return a list of 0 and 1, where 0 means the the ith channel was not loaded correctly, 1 the opposite
                    if result == "ERR_IMP":
                        self.sb.Text = "WARNING: Output impedance not correctly set!"
                        return(-1)
                    if result == "ERR_NCH":
                        self.sb.Text = "WARNING: Number of AWG channels and number of subsections are not consistent!"
                        return(-1)                        
                    else:
                                                
                    #Load result
                        ctrl=1
                                        
                        for x in result: #it checks that each channel were correctly loaded
                            ctrl = x*ctrl
                            
                        if (ctrl == 0): #it means that at least one channel was not correctly loaded
                            self.sb.Text = "Result: Loading error " + repr(result) #it prints the binary array where 1 means "Load OK" and 0 means "Load KO"
                            self.btn_RUN.Enabled = False
                            MessageBox.Show("WARNING: One or more channels were not correctly loaded!")
                        
                        else:
                            self.sb.Text = "Result: Points correctly loaded"
                            self.btn_LOAD.BackColor = Color.LightBlue
                            self.btn_RUN.Enabled = True
                            self.RUN=False #False if it's not generating, True if it's generating
                else:
                    self.sb.Text = "Result: Points correctly loaded"
                    self.btn_LOAD.BackColor = Color.LightBlue

        
        
        #Call Run function in Devices_Control that runs AWGs
        def Call_Run(self, sender, args):
            
            if not self.running:
                print("RUN")
                
                self.btn_RUN.BackColor = Color.Red
                self.btn_RUN.Text = "STOP"
                self.running = True
                
                result = Devices_Control.Run(self.device) #call Run from Devices_Control
                
                ctrl=1                
                
                for x in result:         
                    ctrl = x*ctrl                        
                        
                if ctrl == 1:
                    self.sb.Text = "Result: Devices working correctly"
                elif ctrl == 0: #at least one device is not working properly
                    self.sb.Text = "Result: Devices not working correctly"
                    
                self.btn_LOAD.Enabled = False #all buttons are disabled
                self.btn_INIT.Enabled = False
                                    
            elif self.running:
                self.Call_Stop(self, self)

                             
        def Call_Stop(self, sender, args):
            if self.running:
                print("STOP")
                self.btn_RUN.BackColor = Color.LimeGreen
                self.btn_RUN.Text = "START"
                self.running = False
                
                result = Devices_Control.Stop(self.device)
                
                ctrl = 1
                
                for x in result:
                    ctrl = ctrl*x
                    
                if ctrl == 1:
                    self.sb.Text = "Result: Devices correctly stopped"
                elif ctrl == 0: #at least one device wer not stopped properly
                    self.sb.Text = "Result: Devices not correctly stopped"
                        
                self.btn_LOAD.Enabled = True #all buttons are enabled
                self.btn_INIT.Enabled = True
       
            

#************************************************* BIAS CURRENTS FORM **********************************************            

        def OpenFormBC(self, sender, args):                                   

            self.form_BC = Form()
            self.form_BC.Text = "PJVS Bias currents"
            self.form_BC.Name = "PJVS Bias currents"
            self.form_BC.Size = Size(450, 650)
            self.form_BC.CenterToScreen()            
            
            '''
            self.form_BC.label_nsubs = Label()
            self.form_BC.label_nsubs.Text = "Subsections"
            self.form_BC.label_nsubs.Font = Font("Serif", 11.)
            self.form_BC.label_nsubs.Location = Point(20, 50)
            self.form_BC.label_nsubs.AutoSize = True
            
            self.form_BC.Controls.Add(self.form_BC.label_nsubs)
            '''
            
            self.form_BC.label_bias_curr = Label()
            self.form_BC.label_bias_curr.Text = "Bias currents (mA)"
            self.form_BC.label_bias_curr.Font = Font("Serif", 11.)
            self.form_BC.label_bias_curr.Location = Point(160, 20)
            self.form_BC.label_bias_curr.AutoSize = True
            
            self.form_BC.Controls.Add(self.form_BC.label_bias_curr)

            self.form_BC.label_bias_curr_pos = Label()
            self.form_BC.label_bias_curr_pos.Text = "n=1"
            self.form_BC.label_bias_curr_pos.Font = Font("Serif", 11.)
            self.form_BC.label_bias_curr_pos.Location = Point(140, 50)
            self.form_BC.label_bias_curr_pos.AutoSize = True
            
            self.form_BC.Controls.Add(self.form_BC.label_bias_curr_pos)

            self.form_BC.label_bias_curr_zero = Label()
            self.form_BC.label_bias_curr_zero.Text = "n=0"
            self.form_BC.label_bias_curr_zero.Font = Font("Serif", 11.)
            self.form_BC.label_bias_curr_zero.Location = Point(220, 50)
            self.form_BC.label_bias_curr_zero.AutoSize = True
            
            self.form_BC.Controls.Add(self.form_BC.label_bias_curr_zero)
            
            self.form_BC.label_bias_curr_neg = Label()
            self.form_BC.label_bias_curr_neg.Text = "n=-1"
            self.form_BC.label_bias_curr_neg.Font = Font("Serif", 11.)
            self.form_BC.label_bias_curr_neg.Location = Point(300, 50)
            self.form_BC.label_bias_curr_neg.AutoSize = True
            
            self.form_BC.Controls.Add(self.form_BC.label_bias_curr_neg)

            textbox_subjj_pos = []
            textbox_subjj_neg = [] 
            textbox_subjj_zero = []
            label_subjj = []
            
            for i in range(n_subs): #n_subs is the number of subsections (14)
                x_pos = TextBox()
                x_zero = TextBox()
                x_neg = TextBox()

                y = Label()
                textbox_subjj_pos.append(x_pos)
                textbox_subjj_neg.append(x_neg)
                textbox_subjj_zero.append(x_zero)

                label_subjj.append(y)
                
            self.form_BC.list_textbox_subjj_pos =  Array[TextBox](textbox_subjj_pos)
            self.form_BC.list_textbox_subjj_neg =  Array[TextBox](textbox_subjj_neg)
            self.form_BC.list_textbox_subjj_zero =  Array[TextBox](textbox_subjj_zero)
            
            self.form_BC.list_label_subjj =  Array[Label](label_subjj)

            for i in range(len(label_subjj)):
            
                self.form_BC.list_label_subjj[i].Location = Point(5,int(80+i*25))
                self.form_BC.list_label_subjj[i].Font = Font("Serif", 11.)
               
                self.form_BC.list_label_subjj[i].TextAlign = ContentAlignment.MiddleRight
                self.form_BC.list_label_subjj[i].Text = str(njj_subs_list[i])
                #self.form_BC.list_label_subjj[i].BackColor = Color.LightBlue
                self.form_BC.Controls.Add(self.form_BC.list_label_subjj[i])
            
            for j in range(len(textbox_subjj_pos)):
                self.form_BC.list_textbox_subjj_pos[j].Location = Point(130,int(80+j*25))
                self.form_BC.list_textbox_subjj_pos[j].Text = ("%.3f" %self.I_bias_tot[0][j]) #mA
                self.form_BC.list_textbox_subjj_pos[j].Size = Size(50,10)
                self.form_BC.list_textbox_subjj_pos[j].Leave += self.Set_in_current_Format
                self.form_BC.list_textbox_subjj_pos[j].TextChanged += self.SetBiasCurrents
                self.form_BC.Controls.Add(self.form_BC.list_textbox_subjj_pos[j])
                
            for j in range(len(textbox_subjj_zero)):   
                self.form_BC.list_textbox_subjj_zero[j].Location = Point(210,int(80+j*25))
                self.form_BC.list_textbox_subjj_zero[j].Text = ("%.3f" %self.I_bias_tot[1][j]) #mA
                self.form_BC.list_textbox_subjj_zero[j].Size = Size(50,10)
                self.form_BC.list_textbox_subjj_zero[j].Leave += self.Set_in_current_Format
                self.form_BC.list_textbox_subjj_zero[j].TextChanged += self.SetBiasCurrents             
                self.form_BC.Controls.Add(self.form_BC.list_textbox_subjj_zero[j])
                
            for j in range(len(textbox_subjj_neg)):   
                self.form_BC.list_textbox_subjj_neg[j].Location = Point(290,int(80+j*25))
                self.form_BC.list_textbox_subjj_neg[j].Text = ("%.3f" %self.I_bias_tot[2][j]) #mA                
                self.form_BC.list_textbox_subjj_neg[j].Size = Size(50,10)
                self.form_BC.list_textbox_subjj_neg[j].Leave += self.Set_in_current_Format
                self.form_BC.list_textbox_subjj_neg[j].TextChanged += self.SetBiasCurrents                            
                self.form_BC.Controls.Add(self.form_BC.list_textbox_subjj_neg[j])
                
                
            #button and textbox for setting the same value to all subsetions bias currents
            self.form_BC.textbox_currtoall_pos = TextBox()
            self.form_BC.textbox_currtoall_pos.Location = Point(130,490)
            self.form_BC.textbox_currtoall_pos.Text = "1.000" #mA
            self.form_BC.textbox_currtoall_pos.Size = Size(50,10)
            self.form_BC.textbox_currtoall_pos.Leave += self.Set_in_current_Format
            self.form_BC.Controls.Add(self.form_BC.textbox_currtoall_pos)

            self.form_BC.textbox_currtoall_zero = TextBox()
            self.form_BC.textbox_currtoall_zero.Location = Point(210,490)
            self.form_BC.textbox_currtoall_zero.Text = "0.000" #mA
            self.form_BC.textbox_currtoall_zero.Size = Size(50,10)
            self.form_BC.textbox_currtoall_zero.Leave += self.Set_in_current_Format
            self.form_BC.Controls.Add(self.form_BC.textbox_currtoall_zero)

            self.form_BC.textbox_currtoall_neg = TextBox()
            self.form_BC.textbox_currtoall_neg.Location = Point(290,490)
            self.form_BC.textbox_currtoall_neg.Text = "-1.000" #mA
            self.form_BC.textbox_currtoall_neg.Size = Size(50,10)
            self.form_BC.textbox_currtoall_neg.Leave += self.Set_in_current_Format
            self.form_BC.Controls.Add(self.form_BC.textbox_currtoall_neg)

            self.form_BC.btn_currtoall_pos = Button()
            self.form_BC.btn_currtoall_pos.Name = "POS"
            self.form_BC.btn_currtoall_pos.Location = Point(115,455)
            self.form_BC.btn_currtoall_pos.Font = Font("Serif", 11.)
            self.form_BC.btn_currtoall_pos.Text = "Set to all"
            self.form_BC.btn_currtoall_pos.AutoSize = True
            self.form_BC.btn_currtoall_pos.Click  += self.SetCurrToAll
            self.form_BC.Controls.Add(self.form_BC.btn_currtoall_pos)

            self.form_BC.btn_currtoall_zero = Button()
            self.form_BC.btn_currtoall_zero.Name = "ZERO"
            self.form_BC.btn_currtoall_zero.Location = Point(195,455)
            self.form_BC.btn_currtoall_zero.Font = Font("Serif", 11.)
            self.form_BC.btn_currtoall_zero.Text = "Set to all"
            self.form_BC.btn_currtoall_zero.AutoSize = True
            self.form_BC.btn_currtoall_zero.Click  += self.SetCurrToAll
            self.form_BC.Controls.Add(self.form_BC.btn_currtoall_zero)             

            self.form_BC.btn_currtoall_neg = Button()
            self.form_BC.btn_currtoall_neg.Name = "NEG"
            self.form_BC.btn_currtoall_neg.Location = Point(275,455)
            self.form_BC.btn_currtoall_neg.Font = Font("Serif", 11.)
            self.form_BC.btn_currtoall_neg.Text = "Set to all"
            self.form_BC.btn_currtoall_neg.AutoSize = True
            self.form_BC.btn_currtoall_neg.Click  += self.SetCurrToAll
            self.form_BC.Controls.Add(self.form_BC.btn_currtoall_neg)


            self.form_BC.btn_save = Button()
            self.form_BC.btn_save.Location = Point(100,520)
            self.form_BC.btn_save.Font = Font("Serif", 11.)
            self.form_BC.btn_save.Text = "Save to File"
            self.form_BC.btn_save.Size = Size(100,50)
            self.form_BC.btn_save.Click += self.SaveBiasCurrents
            self.form_BC.btn_save.BackColor = Color.LightBlue
            self.form_BC.Controls.Add(self.form_BC.btn_save)
            
            self.form_BC.btn_load = Button()
            self.form_BC.btn_load.Location = Point(250,520)
            self.form_BC.btn_load.Font = Font("Serif", 11.)
            self.form_BC.btn_load.Text = "Load File"
            self.form_BC.btn_load.Size = Size(100,50)
            self.form_BC.btn_load.BackColor = Color.LightBlue
            self.form_BC.btn_load.Click += self.LoadBiasCurrents
            
            self.form_BC.Controls.Add(self.form_BC.btn_load)
            
            self.form_BC.sb_BC = StatusBar()
            self.form_BC.sb_BC.Text = "Ready"
            self.form_BC.sb_BC.Location = Point(20, 20)
            self.form_BC.Controls.Add(self.form_BC.sb_BC)
            
            self.SetBiasCurrents(self,self)
            
            self.form_BC.Show()
            self.form_BC.Closing += self.FormBCClose                       

               
            
        def SetCurrToAll(self, sender, args):
            if sender.Name == "POS":
                currtoall = self.form_BC.textbox_currtoall_pos.Text
                for i in self.form_BC.list_textbox_subjj_pos:
                    i.Text = currtoall
            elif sender.Name == "ZERO":
                currtoall = self.form_BC.textbox_currtoall_zero.Text
                for i in self.form_BC.list_textbox_subjj_zero:
                    i.Text = currtoall        
            elif sender.Name == "NEG":
                currtoall = self.form_BC.textbox_currtoall_neg.Text
                for i in self.form_BC.list_textbox_subjj_neg:
                    i.Text = currtoall
        
        def SetBiasCurrents(self, sender, args):
            #create a matrix of currents, n_subs rows and 3 columns for 1, 0 and -1 quantum steps
            I_bias_pos = []
            I_bias_zero = []
            I_bias_neg = []
                                            
            for j in range(n_subs):
                I_bias_pos.append(float(self.form_BC.list_textbox_subjj_pos[j].Text)) #mA
                I_bias_zero.append(float(self.form_BC.list_textbox_subjj_zero[j].Text)) #mA
                I_bias_neg.append(float(self.form_BC.list_textbox_subjj_neg[j].Text)) #mA

            self.I_bias_tot = [I_bias_pos, I_bias_zero, I_bias_neg]            


        # save currents into a txt file
        def SaveBiasCurrents(self, sender, args):
            
            folder = "Bias Currents Files"
            if not os.path.exists(folder):
                os.makedirs(folder)
            
            
            curr_matrix = transpose(self.I_bias_tot)            
            save_currents = SaveFileDialog()
            save_currents.Filter = "txt files (*.txt)|*.txt"
            #save_currents.FilterIndex = 2
            save_currents.RestoreDirectory = True
            save_currents.InitialDirectory = os.getcwd() + "\\" + folder
            
            if save_currents.ShowDialog() == DialogResult.OK:            
  
                writer = StreamWriter(save_currents.OpenFile())
                writer.WriteLine("{0},{1},{2},{3}"," Subsections ", " Current n=1 (mA) ", " Current n=0 (mA) ", " Current n=-1 (mA) ")
                for i in range(len(curr_matrix)):                    
                    writer.WriteLine("{0},{1},{2},{3}","   %d  "%(njj_subs_list[i]), "   %.3f   "%(curr_matrix[i][0]), "   %.3f   "%(curr_matrix[i][1]), "   %.3f   "%(curr_matrix[i][2]))
                writer.Dispose()
                writer.Close()            
                self.form_BC.sb_BC.Text = "Result: file saved"
            
    
        
        #it loads currents from a txt file
        def LoadBiasCurrents(self, sender, args):
            
            load_currents = OpenFileDialog()
            load_currents.Filter = "txt files (*.txt)|*.txt"
            #load_currents.FilterIndex = 2
            load_currents.RestoreDirectory = True
            load_currents.InitialDirectory = os.getcwd()
            
            lines_to_skip = 1 
            counter = 0            
            read_currents=[]
            
            if load_currents.ShowDialog() == DialogResult.OK:
                reader = StreamReader(load_currents.OpenFile())
                
                line = reader.ReadLine()
                while line is not None:                    
                    if counter<lines_to_skip:
                        counter+=1
                        line = reader.ReadLine()
                    else:
                        if line is None:
                            break
                        row=list(array(str(line).split(",")).astype(float))
                        read_currents.append(row)
                        counter+=1
                        line = reader.ReadLine()
            
                for i in range(n_subs):
                    if self.form_BC.list_label_subjj[i].Text == str(int(read_currents[i][0])):
                        self.form_BC.list_textbox_subjj_pos[i].Text = "%.3f"%(read_currents[i][1])
                        self.form_BC.list_textbox_subjj_zero[i].Text = "%.3f"%(read_currents[i][2])                               
                        self.form_BC.list_textbox_subjj_neg[i].Text = "%.3f"%(read_currents[i][3])
                    else:
                        self.form_BC.sb_BC.Text = "Result: bias currents not loaded!"
                        break
                    
                    if i== n_subs-1:
                        self.form_BC.sb_BC.Text = "Result: bias currents loaded correctly"
            print(self.I_bias_tot)        
              
                
                
        def FormBCClose(self, sender, args):
            if args.CloseReason == CloseReason.UserClosing :
                self.form_BC.Visible = False
                
                
                
                
#************************************************* IV-CHARACTERISTIC FORM **********************************************            
            
            
        def OpenFormIV(self, sender, args):
                        
            self.running= False
            
            #form for IV characteristics
            self.form_IV = Form()
            self.form_IV.Text = "PJVS IV-characteristics"
            self.form_IV.Name = "PJVS IV-characteristics"
            self.form_IV.Size = Size(900, 620)
            self.form_IV.CenterToScreen()
            
            #Button for initializing voltmeter
            self.form_IV.btn_InitVolt = Button()
            self.form_IV.btn_InitVolt.Text = "Initialize \n Voltmeter"
            self.form_IV.btn_InitVolt.Name = "InitVoltIV"        
            self.form_IV.btn_InitVolt.Font = Font("Serif", 12.)
            self.form_IV.btn_InitVolt.BackColor = Color.White
            self.form_IV.btn_InitVolt.Location = Point(50, 30)
            self.form_IV.btn_InitVolt.Size = Size (125, 50)
            if sim:
                self.form_IV.btn_InitVolt.Enabled = False
                
            self.form_IV.btn_InitVolt.Click += self.Call_InitVoltmeter
            
            self.form_IV.Controls.Add(self.form_IV.btn_InitVolt)


            #Maximum current in mA
            self.form_IV.curr_max = Label()
            self.form_IV.curr_max.Text = "Maximum current (mA): "
            self.form_IV.curr_max.Font = Font("Serif", 11.)
            self.form_IV.curr_max.Location = Point(10, 130)
            self.form_IV.curr_max.AutoSize = True
            self.form_IV.Controls.Add(self.form_IV.curr_max)            
            
            self.form_IV.in_curr_max = TextBox()
            self.form_IV.in_curr_max.Text = "0." #mA
            self.form_IV.in_curr_max.Location = Point(185, 130)
            self.form_IV.in_curr_max.Size = Size(50, 10)
            self.form_IV.in_curr_max.Leave += self.Set_in_curr_max_Format
        
            self.form_IV.Controls.Add(self.form_IV.in_curr_max)

            #NPLC voltmeter
            self.form_IV.volt_NPLC = Label()
            self.form_IV.volt_NPLC.Text = "NPLC (0.01-50): "
            self.form_IV.volt_NPLC.Font = Font("Serif", 11.)
            self.form_IV.volt_NPLC.Location = Point(10, 210)
            self.form_IV.volt_NPLC.AutoSize = True
            self.form_IV.Controls.Add(self.form_IV.volt_NPLC)            
            
            self.form_IV.in_volt_NPLC = TextBox()
            self.form_IV.in_volt_NPLC.Text = "0.1" #mA
            self.form_IV.in_volt_NPLC.Location = Point(185, 210)
            self.form_IV.in_volt_NPLC.Size = Size(50, 10)
            self.form_IV.in_volt_NPLC.Leave += self.Set_in_volt_NPLC_Format
        
            self.form_IV.Controls.Add(self.form_IV.in_volt_NPLC)

            
            #Expected single junction normal resistance in Ohm, needed since AWGs are voltage generators
            '''
            self.form_IV.Rjj = Label()
            self.form_IV.Rjj.Text = "Resistance 1 jj (Ohm): "
            self.form_IV.Rjj.Font = Font("Serif", 11.)
            self.form_IV.Rjj.Location = Point(10, 250)
            self.form_IV.Rjj.AutoSize = True
            
            self.form_IV.Controls.Add(self.form_IV.Rjj)            
            '''
            self.form_IV.in_Rjj = TextBox()
            self.form_IV.in_Rjj.Text = "0.037" #Ohm 37 mOhm
            '''self.form_IV.in_Rjj.Location = Point(185, 250)
            self.form_IV.in_Rjj.Size = Size(50, 10)
            self.form_IV.in_Rjj.Leave += self.Set_in_Rjj_Format
        
            self.form_IV.Controls.Add(self.form_IV.in_Rjj)
            '''
            #Number of IV points
            self.form_IV.npointsIV = Label()
            self.form_IV.npointsIV.Text = "Number of points: "
            self.form_IV.npointsIV.Font = Font("Serif", 11.)
            self.form_IV.npointsIV.Location = Point(10, 170)
            self.form_IV.npointsIV.AutoSize = True
            
            
            self.form_IV.Controls.Add(self.form_IV.npointsIV)            
            
            self.form_IV.in_npointsIV = TextBox()
            self.form_IV.in_npointsIV.Text = "50"
            self.form_IV.in_npointsIV.Location = Point(185, 170)
            self.form_IV.in_npointsIV.Size = Size(50, 10)
            self.form_IV.in_npointsIV.Leave += self.Set_in_npointsIV_Format
        
            self.form_IV.Controls.Add(self.form_IV.in_npointsIV)



            checkbox_subjj = []
            
            self.subs = njj_subs_list
            
            for i in range(n_subs): #n_subs is the number of subsections (14)
                x = CheckBox()
                checkbox_subjj.append(x)
                
            self.form_IV.list_checkbox_subjj =  Array[CheckBox](checkbox_subjj)                        
            
            #self.subsect = self.subs[0] #indice delle sottosezioni che polarizzo (0:64; 1:(64+32); 2:(64+32+16); ......)

            
            self.form_IV.list_checkbox_all = CheckBox()
            self.form_IV.list_checkbox_all.Location = Point(270,60)
            self.form_IV.list_checkbox_all.Font = Font("Serif", 11.)
            self.form_IV.list_checkbox_all.BackColor = Color.LightBlue
            self.form_IV.list_checkbox_all.Text = "Select all"
            self.form_IV.list_checkbox_all.CheckedChanged += self.SelectDeselectAll
            self.form_IV.Controls.Add(self.form_IV.list_checkbox_all)      
            
            for i in range(len(checkbox_subjj)):
            
                self.form_IV.list_checkbox_subjj[i].Location = Point(270,int(85+i*25))
                self.form_IV.list_checkbox_subjj[i].Font = Font("Serif", 11.)
                self.form_IV.list_checkbox_subjj[i].Text = str(self.subs[i])
                self.form_IV.list_checkbox_subjj[i].BackColor = Color.LightBlue
                self.form_IV.list_checkbox_subjj[i].CheckedChanged += self.GetNumbAndSect
                self.form_IV.Controls.Add(self.form_IV.list_checkbox_subjj[i])
                                  
            #Subsections panel
            self.form_IV.panel_subjj = Panel()
            self.form_IV.panel_subjj.Location = Point(260,50) 
            self.form_IV.panel_subjj.Size = Size(130,400)
            self.form_IV.panel_subjj.BackColor = Color.LightBlue
            self.form_IV.panel_subjj.Text = "Subsections"
            self.form_IV.Controls.Add(self.form_IV.panel_subjj)
            
            #Total number of junctions selected
            self.form_IV.njj_tot = Label()
            self.form_IV.njj_tot.Text = "Number of junctions: 0 "
            self.form_IV.njj_tot.Font = Font("Serif", 11.)
            self.form_IV.njj_tot.Location = Point(10, 300)
            self.form_IV.njj_tot.AutoSize = True
            
            self.form_IV.Controls.Add(self.form_IV.njj_tot)
            
            #Number of subsections selected
            self.form_IV.nsubs = Label()
            self.form_IV.nsubs.Text = "Number of subsections: 0 "
            self.form_IV.nsubs.Font = Font("Serif", 11.)
            self.form_IV.nsubs.Location = Point(10, 340)
            self.form_IV.nsubs.AutoSize = True
            
            self.form_IV.Controls.Add(self.form_IV.nsubs)

            #Checkbox for averaging IV
            self.form_IV.checkbox_avg = CheckBox()
            self.form_IV.checkbox_avg.Location = Point(10,380)
            self.form_IV.checkbox_avg.Font = Font("Serif", 11.)
            self.form_IV.checkbox_avg.Text = "Average"
            self.form_IV.checkbox_avg.Checked = False
            self.form_IV.Controls.Add(self.form_IV.checkbox_avg)
            
            #Counts the number of averages
            self.form_IV.out_avg = TextBox()
            self.form_IV.out_avg.Text = "0"
            self.form_IV.out_avg.Enabled = False
            self.form_IV.out_avg.BackColor = Color.White
            self.form_IV.out_avg.ForeColor = Color.Black
            self.form_IV.out_avg.BackColor = Color.White
            self.form_IV.out_avg.Location = Point(115, 380)
            self.form_IV.out_avg.Size = Size(50, 10)            
        
            self.form_IV.Controls.Add(self.form_IV.out_avg)

        
            #Plot IV characteristic
            self.form_IV.plotIV = Graph.Chart()
            self.form_IV.plotIV.Location = Point(430, 10)
            self.form_IV.plotIV.Size = Size (450, 450)
            self.form_IV.areaIV = Graph.ChartArea()
            self.form_IV.plotIV.ChartAreas.Add(self.form_IV.areaIV)
            
            
            self.form_IV.areaIV.AxisX.MajorGrid.LineColor = Color.White
            self.form_IV.areaIV.AxisX.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            self.form_IV.areaIV.AxisX.MajorGrid.IntervalType = Graph.DateTimeIntervalType.Number
            self.form_IV.areaIV.AxisX.MajorGrid.IntervalOffset = 0.
            self.form_IV.areaIV.AxisX.Title = 'Voltage (V)'
            self.form_IV.areaIV.AxisX.TitleFont = Font("Serif", 12.)

            self.form_IV.areaIV.AxisY.MajorGrid.LineColor = Color.White
            self.form_IV.areaIV.AxisY.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            self.form_IV.areaIV.AxisY.Title = 'Current (mA)'
            self.form_IV.areaIV.AxisY.TitleFont = Font("Serif", 12.)            
            self.form_IV.areaIV.BackColor = Color.LightGray
            self.form_IV.areaIV.AxisY.LabelStyle.Format = "0.000"
            self.form_IV.areaIV.AxisX.LabelStyle.Format = "E0"

            self.form_IV.areaIV.CursorX.Interval = 0
            self.form_IV.areaIV.CursorY.Interval = 0
            self.form_IV.areaIV.AxisX.ScaleView.Zoomable = True
            self.form_IV.areaIV.AxisY.ScaleView.Zoomable = True
        
            self.form_IV.areaIV.CursorX.IsUserEnabled = True
            self.form_IV.areaIV.CursorX.IsUserSelectionEnabled = True
            self.form_IV.areaIV.CursorX.SelectionColor = Color.Gray
            self.form_IV.areaIV.CursorY.SelectionColor = Color.Gray
            self.form_IV.areaIV.CursorY.IsUserEnabled = True
            self.form_IV.areaIV.CursorY.IsUserSelectionEnabled = True
            self.form_IV.areaIV.CursorX.LineColor = Color.Blue
            self.form_IV.areaIV.CursorX.LineWidth = 1
            self.form_IV.areaIV.CursorX.LineDashStyle = Graph.ChartDashStyle.DashDot
            self.form_IV.areaIV.CursorY.LineColor = Color.Blue
            self.form_IV.areaIV.CursorY.LineWidth = 1
            self.form_IV.areaIV.CursorY.LineDashStyle = Graph.ChartDashStyle.DashDot
            
            self.form_IV.seriesIV = Graph.Series("IV")
            self.form_IV.seriesIV.ChartType = Graph.SeriesChartType.Line
            self.form_IV.seriesIV.Color = Color.Red
            self.form_IV.seriesIV.BorderWidth = 2
            self.form_IV.seriesIV.ToolTip="V = #VALX{0.######} V\nI = #VALY{0.###} mA"
            self.form_IV.plotIV.Series.Add(self.form_IV.seriesIV)                        
            
            self.form_IV.series_new_datapoint = Graph.Series("new datapoint")
            self.form_IV.series_new_datapoint.ChartType = Graph.SeriesChartType.Point
            self.form_IV.series_new_datapoint.Color = Color.Blue
            self.form_IV.series_new_datapoint.BorderWidth = 2
            self.form_IV.series_new_datapoint.Points.AddXY(0.,0.)
            self.form_IV.plotIV.Series.Add(self.form_IV.series_new_datapoint)
            
            self.form_IV.Controls.Add(self.form_IV.plotIV)            


            #Button for running IV
            self.form_IV.btn_runIV = Button()
            self.form_IV.btn_runIV.Text = "Run IV"
            self.form_IV.btn_runIV.Font = Font("Serif", 12.)
            self.form_IV.btn_runIV.BackColor = Color.LimeGreen
            self.form_IV.btn_runIV.Location = Point(530, 500)
            self.form_IV.btn_runIV.Size = Size (100, 50)
            
            if sim:
                self.form_IV.btn_runIV.Enabled = True #SIMULATION
            else:
                self.form_IV.btn_runIV.Enabled = False
                
            self.form_IV.btn_runIV.Click += self.RunIV
            
            self.form_IV.Controls.Add(self.form_IV.btn_runIV)
            
            
            #Button for stopping IV
            self.form_IV.btn_stopIV = Button()
            self.form_IV.btn_stopIV.Text = "Stop IV"
            self.form_IV.btn_stopIV.Font = Font("Serif", 12.)
            self.form_IV.btn_stopIV.BackColor = Color.Red
            self.form_IV.btn_stopIV.Location = Point(630, 500)
            self.form_IV.btn_stopIV.Size = Size (100, 50)
            self.form_IV.btn_stopIV.Enabled = False
            self.form_IV.btn_stopIV.Click += self.StopIV
            
            self.form_IV.Controls.Add(self.form_IV.btn_stopIV)
            
            #Button for saving IV
            self.form_IV.btn_saveIV = Button()
            self.form_IV.btn_saveIV.Text = "Save"
            self.form_IV.btn_saveIV.Font = Font("Serif", 12.)
            self.form_IV.btn_saveIV.BackColor = Color.White
            self.form_IV.btn_saveIV.Location = Point(730, 500)
            self.form_IV.btn_saveIV.Size = Size (100, 50)
            self.form_IV.btn_saveIV.Enabled = False
            self.form_IV.btn_saveIV.Click += self.SaveIV
            
            self.form_IV.Controls.Add(self.form_IV.btn_saveIV)            
            


            #Notes
            self.form_IV.note = Label()
            self.form_IV.note.Text = "Note:"
            self.form_IV.note.Font = Font("Serif", 12.)
            self.form_IV.note.Location = Point(450, 468)
            self.form_IV.note.AutoSize = True
        
            self.form_IV.Controls.Add(self.form_IV.note)

            self.form_IV.in_note = TextBox()
            self.form_IV.in_note.Text = ""
            self.form_IV.in_note.Font = Font("Serif", 12.)
            self.form_IV.in_note.Location = Point(500, 465)
            self.form_IV.in_note.Size = Size(350, 10)
        
            self.form_IV.Controls.Add(self.form_IV.in_note)

            
            #INRIM_logo
            self.form_IV.logo = PictureBox()
            self.form_IV.logo.Location = Point(20, 470)
            self.form_IV.logo.Size = Size (210, 70)
            self.form_IV.logo.SizeMode = PictureBoxSizeMode.StretchImage
            self.form_IV.logo.Load("logo_inrim.jpg")
            self.form_IV.Controls.Add(self.form_IV.logo)
            
            self.form_IV.sb_IV = StatusBar()
            self.form_IV.sb_IV.Text = "Ready"
            self.form_IV.sb_IV.Location = Point(20, 20)
            
            self.form_IV.Controls.Add(self.form_IV.sb_IV)
            
            self.StopClicked = False # if stop button is clicked it waits until IV is finished, if it's clicked again it stops immediately the IV characteristic
            self.IVpts_counter = 0
            
            self.form_IV.Closing += self.FormIVClose
            self.form_IV.formClosed = False
            
            self.form_IV.Show()

            self.Set_in_curr_max_Format(self,self)
            self.Set_in_Rjj_Format(self,self)
            self.Set_in_npointsIV_Format(self,self)



        #functions for formatting the textboxes
        def Set_in_curr_max_Format(self, sender, args):
            number = '{0:.3f}'.format(float(self.form_IV.in_curr_max.Text))
            self.form_IV.in_curr_max.Text = str(number)
        
        def Set_in_Rjj_Format(self, sender, args):
            number = '{0:.3f}'.format(float(self.form_IV.in_Rjj.Text))
            self.form_IV.in_Rjj.Text = str(number)
            
        def Set_in_npointsIV_Format(self, sender, args):
            number = '{0:d}'.format(round(float(self.form_IV.in_npointsIV.Text)))
            self.form_IV.in_npointsIV.Text = str(number)
            
            
        def Set_in_volt_NPLC_Format(self, sender, args):
            number = float('{0:.3f}'.format(float(sender.Text)))
            if number>50:
                number=50
            elif number<0.01:
                number=0.01
            sender.Text = str(number)            
            

                                    
            
        #Calls the search of voltmeter
        def Call_InitVoltmeter(self, sender, args):
            if sender.Name== "InitVoltIV":
                nplc = float(self.form_IV.in_volt_NPLC.Text)
            if sender.Name== "InitVoltQT":
                nplc = float(self.form_QT.in_volt_NPLC.Text)          
                        
            self.voltmeter = Devices_Control.InitVoltmeter(nplc) #call InitVoltmeter from Devices_Control
            if self.voltmeter == "ERR_VOLT":
                    if sender.Name== "InitVoltIV":
                        self.form_IV.sb_IV.Text = "Result: Voltmeter not found!"
                    if sender.Name== "InitVoltQT":
                        self.form_QT.sb_QT.Text = "Result: Voltmeter not found!"                        
                    return(-1)
            else:
                if sender.Name=="InitVoltIV":
                    self.form_IV.sb_IV.Text = "Result: Voltmeter correctly initialized"
                    self.form_IV.btn_InitVolt.BackColor = Color.LightBlue
                    self.form_IV.btn_runIV.Enabled = True
                    
                if sender.Name=="InitVoltQT":
                    self.form_QT.sb_QT.Text = "Result: Voltmeter correctly initialized"
                    self.form_QT.btn_InitVolt.BackColor = Color.LightBlue
                    self.form_QT.btn_runQT.Enabled = True
        
        #for selecting or deselecting all subsection checkboxes
        def SelectDeselectAll(self, sender, args):
            if self.form_IV.list_checkbox_all.Checked==True:
                for i in self.form_IV.list_checkbox_subjj:
                    if i.Checked==False:
                        i.Checked=True
                
            if self.form_IV.list_checkbox_all.Checked==False:
                for i in self.form_IV.list_checkbox_subjj:
                    if i.Checked==True:
                        i.Checked=False                    
            

        #print the number of junctions and of subsections that are flagged            
        def GetNumbAndSect(self, sender, args):
            njj = 0
            nsubs = 0
            for i in self.form_IV.list_checkbox_subjj:
                if i.Checked == True:
                    njj+=int(i.Text)
                    nsubs+=1
            
            self.form_IV.njj_tot.Text="Number of junctions: "+ str(njj)
            self.form_IV.nsubs.Text="Number of subsections: "+ str(nsubs)
            
        
        #Runs the IV characteristics calling function from Devices_Control
        def RunIV(self, sender, args):
                                               
                njj = 0
                                
                subs_status=[] #array containing the status of each subsection: 1 means "ON", 0 means "OFF"
                for i in self.form_IV.list_checkbox_subjj:
                    if i.Checked == True:
                        subs_status.append(int(1)) #if flagged
                        njj = njj+int(i.Text)
                        
                    elif i.Checked == False:
                        subs_status.append(int(0)) #if not flagged
                
                subs_on=[] #indexes of subsections ON
                for i in range(len(subs_status)): 
                    if subs_status[i]==1:
                        subs_on.append(i)
                        
    
                if len(subs_on)<1:
                    print("WARNING: No subsection selected!")
                    MessageBox.Show("WARNING: No subsection selected!")
                    return(-1)
        
                else:
                    for i in diff(subs_on):
                        if abs(i)!=1:
                            print("WARNING: Select adjacent subsections!")
                            MessageBox.Show("WARNING: Select adjacent subsections!")
                            return(-1)                   
                        else:
                            continue                
                               
                if not sim:                                         
                    act_ch = Devices_Control.SetImpedance(self.device, subs_status) #gets the index of the unique channel that is active
                    
                    if act_ch == "ERR_NCH":
                        self.form_IV.sb.Text = "WARNING: Number of AWG channels and number of subsections are not consistent!"
                        return(-1)
                    if act_ch == "ERR_IMP":
                        self.sb.Text = "WARNING: Output impedance not correctly set!"
                        return(-1)
                        
                curr_max = float(self.form_IV.in_curr_max.Text)   #current in mA          
                if curr_max==0.:
                    MessageBox.Show("WARNING: Set current greater than zero")                    
                    return(-1)
                    
                self.running = True
                self.form_IV.sb_IV.Text = "RUN"
                self.form_IV.btn_runIV.Enabled = False
                self.form_IV.btn_stopIV.Enabled = True      
                self.form_IV.checkbox_avg.Enabled = False
                self.StopClicked = False
                self.form_IV.btn_saveIV.Enabled = False
                self.form_IV.areaIV.AxisX.StripLines.Clear()                        
                
                first_span = True                        
                
                pars = Math_Functions.EvalParameters(float(self.in_freqRF.Text))
                
                Vstep = pars[0]*njj #Voltage of first Shapiro step
                                                            
                for i in [-3,-2,-1,0,1,2,3]: #for viewing in the plot were 1,2, and 3 Shapiro steps should occur
                    sl = Graph.StripLine()
                    sl.Interval = Graph.DateTimeIntervalType.Auto
                    sl.StripWidth = Vstep/50.
                    sl.IntervalOffset = i*Vstep-0.5*sl.StripWidth
                    sl.IntervalOffsetType = Graph.DateTimeIntervalType.Auto                    
                    sl.StripWidthType = Graph.DateTimeIntervalType.Number
                    sl.BackColor = Color.FromArgb(80, 0, 255, 200)
                    self.form_IV.areaIV.AxisX.StripLines.Add(sl)
                

                Rjj_exp = float(self.form_IV.in_Rjj.Text) # Ohm, expected single junction resistance
                
                R = 50 #Ohm output impedance of the active channel
                                
                Vmax = float(curr_max*(R + njj*Rjj_exp)/1000.) #expected maximum voltage in V
                if abs(Vmax)>=vmax_awg: #this is the maximum voltage that the awg can provide, it is set in Main.py
                    Vmax = sign(Vmax)*vmax_awg
                
                n_pts = int(self.form_IV.in_npointsIV.Text)
                
                dV = float(2*Vmax/n_pts) #voltage variation            
                Vstart = 0. #starting voltage                        
                
                #list of the voltages provided by the active channel (0--->Vmax; Vmax--->-Vmax; -Vmax---> 0)         
                Vlist = list(arange(Vstart,Vmax,dV))+list(arange(Vmax,Vstart,-dV))+list(arange(Vstart,-Vmax,-dV))+list(arange(-Vmax,Vstart,dV))              
                                       

                self.form_IV.seriesIV.Points.Clear()
                self.form_IV.series_new_datapoint.Points.Clear()

                
                vmin = -1*abs(njj*Rjj_exp*curr_max/1000.)
                vmax = abs(njj*Rjj_exp*curr_max/1000.)                
                imin = -1*abs(curr_max)
                imax = abs(curr_max)
                                    
                self.form_IV.areaIV.AxisX.Minimum = vmin
                self.form_IV.areaIV.AxisX.Maximum = vmax
                self.form_IV.areaIV.AxisY.Minimum = imin
                self.form_IV.areaIV.AxisY.Maximum = imax
                self.form_IV.areaIV.AxisX.Interval = float((vmax-vmin)/10.)
                self.form_IV.areaIV.AxisY.Interval = float((imax-imin)/10.)
                
                i=0
                j=0
                
                Vlist_new=[]

                avg_count = 0
                self.form_IV.out_avg.Text = str(avg_count)
                
                while self.running:

                    Application.DoEvents()
                    if self.form_IV.formClosed:
                        self.running = False
                        break
                            
                    if first_span:
                        Vch = Vlist[i] #Vch is the voltage provided by the active channel
                    else:
                        Vch = Vlist_new[i] 
                    
                    
                    if self.form_IV.checkbox_avg.Checked and not first_span and i == 0:
                        avg_count+=1
                        self.form_IV.out_avg.Text = str(avg_count)
                        
                    if sim:
                        curr = 1000.*Vch/(R+njj*Rjj_exp) #SIMULATION
                        sigmaV= curr_max*njj*Rjj_exp/(100.*1000.)
                        #sigmaV = 0
                        Vread = curr*njj*Rjj_exp/1000. + sigmaV*uniform(-1.,1.) 
                    
                    else:
                        if self.running: #because HALT button is clicked and IV is forced to terminate
                            Vsubs = n_subs*[0]
                            Vsubs[act_ch-1]=Vch
                            Devices_Control.SetDCVoltages(self.device, Vsubs) #it sets a non-zero dc voltage only on the active channel
                            Vread = float(Devices_Control.ReadVolt(self.voltmeter)) #voltage read by the voltmeter
                        else:
                            break
                        
                    curr = float(1000.*(Vch-Vread)/R) #current calculation in mA
                    
                    #stuff for the plot scale
                    if Vread > self.form_IV.areaIV.AxisX.Maximum:
                        vmax = Vread
                        self.form_IV.areaIV.AxisX.Maximum = Vread
                        self.form_IV.areaIV.AxisX.Interval = float((vmax-vmin)/10.)
            
                    
                    if Vread < self.form_IV.areaIV.AxisX.Minimum:
                        vmin = Vread
                        self.form_IV.areaIV.AxisX.Minimum = Vread
                        self.form_IV.areaIV.AxisX.Interval = float((vmax-vmin)/10.)                        
           
                    
                    if curr > self.form_IV.areaIV.AxisY.Maximum:
                        imax = curr
                        self.form_IV.areaIV.AxisY.Maximum = curr
                        self.form_IV.areaIV.AxisY.Interval = float((imax-imin)/10.)
                                            
                    if curr < self.form_IV.areaIV.AxisY.Minimum:
                        imin = curr 
                        self.form_IV.areaIV.AxisY.Minimum = curr
                        self.form_IV.areaIV.AxisY.Interval = float((imax-imin)/10.)

                    self.form_IV.series_new_datapoint.Points.Clear()
                    
                    
                    #points represented in the IV characteristics, one red line and blue data points
                    dp = Graph.DataPoint(Vread,curr)
                    dp2 = Graph.DataPoint(Vread,curr)                        
                    
                    if first_span:
                        self.form_IV.seriesIV.Points.Add(dp)
                        self.form_IV.series_new_datapoint.Points.Clear()
                        self.form_IV.series_new_datapoint.Points.Add(dp2) #blue data points are deleted from time to time
                    
                    else:
                        if self.form_IV.checkbox_avg.Checked: # averaging of the IV characteristic
                            if j<self.form_IV.seriesIV.Points.Count:                                                        
                                dp_prev = self.form_IV.seriesIV.Points.Items[j] #take the jth element of the previous span
                            else:
                                self.form_IV.seriesIV.Points.Add(dp)
                                dp_prev = dp
                            #excluding first span (when avg_count=1) from the average since it could have a lower number of points    
                            xavg = ((dp_prev.XValue)*(avg_count-1) + (dp.XValue))/(avg_count)
                            yavg = ((dp_prev.YValues[0])*(avg_count-1) + (dp.YValues[0]))/(avg_count)

                            dp_avg = Graph.DataPoint(xavg,yavg)

                            self.form_IV.seriesIV.Points.SetItem(j,dp_avg)
                            self.form_IV.series_new_datapoint.Points.Clear()
                            self.form_IV.series_new_datapoint.Points.AddXY(xavg,yavg)                                
                            
                        else:
                            if j>= self.form_IV.seriesIV.Points.Count:
                                self.form_IV.seriesIV.Points.Add(dp)
                            else:                                
                                self.form_IV.seriesIV.Points.SetItem(j,dp)
                            self.form_IV.series_new_datapoint.Points.Clear()
                            self.form_IV.series_new_datapoint.Points.Add(dp2)
                            
                    if sim:
                        time.sleep(0.05) #SIMULATION        
                    
                    
                    
                    if first_span:
                        if abs(curr)<=curr_max:
                            Vlist_new.append(Vch) #new list used in the next loops where the current is actually lower than curr_max
                        
                        else:
                            self.form_IV.seriesIV.Points.RemoveItem(self.form_IV.seriesIV.Points.Count-1) #delete last datapoint because the current is bigger than curr_max
                            self.form_IV.series_new_datapoint.Points.RemoveItem(0)
                            Vthres = abs(Vch)
                            while abs(Vlist[i]) >= Vthres:   #step to the next voltage value                            
                                i+=1
                                if i == len(Vlist): 
                                    i = 0
                                    j = 0
                        

                        if i == len(Vlist)-1:  # last element of the list, start again and not first span anymore                
                            
                            #Rjj_exp = float(1000*(vmax-vmin)/(imax-imin))
                            #print("\n Resistance = " + str(Rjj_exp) + " Ohm; Number of junction: " + str(round(Rjj_exp/Rjj_exp)))
                            i = 0
                            j = 0
                                                        
                            first_span = False
                            
                            #recalculate the list of voltages to generate n_pts points
                            Vmax_new = max(Vlist_new)
                            Vmin_new = min(Vlist_new)
                            Vstart_new = mean([Vmax_new,Vmin_new])                            
                            dV_new = (Vmax_new-Vmin_new)/n_pts
                            Vlist_new = list(arange(Vstart_new,Vmax_new,dV_new))+list(arange(Vmax_new,Vstart_new,-dV_new))+list(arange(Vstart_new,Vmin_new,-dV_new))+list(arange(Vmin_new,Vstart_new,dV_new)) 

                        else:
                            i+=1
                    else:
                        #stuff for plot scale
                        xmax = self.form_IV.seriesIV.Points.FindMaxByValue("X",0).XValue
                        xmin = self.form_IV.seriesIV.Points.FindMinByValue("X",0).XValue
                        ymax = self.form_IV.seriesIV.Points.FindMaxByValue("Y1",0).YValues[0]
                        ymin = self.form_IV.seriesIV.Points.FindMinByValue("Y1",0).YValues[0]                               
                        
                        self.form_IV.areaIV.AxisX.Maximum = xmax
                        self.form_IV.areaIV.AxisX.Minimum = xmin
                        self.form_IV.areaIV.AxisX.Interval = (xmax-xmin)/10.
                                     
                        self.form_IV.areaIV.AxisY.Maximum = ymax
                        self.form_IV.areaIV.AxisY.Minimum = ymin                               
                        self.form_IV.areaIV.AxisY.Interval = (ymax-ymin)/10.

                        
                        
                        if i == len(Vlist_new)-1:  #last element of the new list, so not the first span, start again

                                                                       
                            #Rjj_exp = float(1000*(vmax-vmin)/(imax-imin))
                            #print("\n Resistance = " + str(Rjj_exp) + " Ohm; Number of junctions: " + str(round(Rjj_exp/Rjj_exp)))
                            i = 0
                            j = 0

                        else: #otherwise I go to the next point
                            i+=1
                            j+=1
                    
                    self.IVpts_counter = i
                    if self.StopClicked and self.IVpts_counter ==0:
                        self.form_IV.btn_stopIV.OnClick(EventArgs.Empty)  #if Stop clicked once it waits until the IV is finished                          
                                                



        def StopIV(self, sender, args):
            Application.DoEvents()
            if not self.StopClicked: #if first click it finishes the IV characteristic, if I click again it suddenly stops
                self.StopClicked = True
                self.form_IV.btn_stopIV.Text = 'Halt' 
                self.form_IV.btn_stopIV.BackColor = Color.Yellow 

            elif self.StopClicked:
                self.running = False #if Stop was already clicked once the IV is forced to immediately stop
                if not sim:
                    zero_volt_array = n_subs*[0.0]
                    setvolt = Devices_Control.SetDCVoltages(self.device, zero_volt_array)
                    if setvolt == "ERR_SET_VOLT":
                        self.form_IV.sb.Text = "WARNING: Voltage not correctly set!"
                        return(-1)                     
                    
                self.form_IV.sb_IV.Text = "STOP"
                self.form_IV.btn_runIV.Enabled = True
                self.form_IV.btn_stopIV.Enabled = False
                self.form_IV.checkbox_avg.Enabled = True
                self.StopClicked = False                
                self.form_IV.btn_stopIV.Text = 'Stop IV'
                self.form_IV.btn_stopIV.BackColor = Color.Red
                if self.IVpts_counter == 0:
                    
                    self.form_IV.btn_saveIV.Enabled = True
                
                else:
                    self.form_IV.btn_saveIV.Enabled = False  
                    
                    

        def SaveIV(self, sender, args):

            folder = "Meas"
            if not os.path.exists(folder):
                os.makedirs(folder)
            
            IVdata = self.form_IV.seriesIV.Points
            notes = str(self.form_IV.in_note.Text)    
            
            voltcurr=[]
            for i in range(IVdata.Count):
                volt = IVdata.Items[i].XValue
                curr = IVdata.Items[i].YValues[0]
                voltcurr.append([volt,curr])    
      
            
            save_IV = SaveFileDialog()
            save_IV.Filter = "txt files (*.txt)|*.txt"
            save_IV.RestoreDirectory = True
            save_IV.FileName = notes
            save_IV.InitialDirectory = os.getcwd() + "\\" + folder
            
            if save_IV.ShowDialog() == DialogResult.OK:            
  
                writer = StreamWriter(save_IV.OpenFile())
                writer.WriteLine("{0},{1},{2}"," Voltage (V) "," Current (mA) ", notes)
                
                for i in range(IVdata.Count):                  
                    writer.WriteLine("{0},{1}","   %.10f  " % voltcurr[i][0], "   %.5f   " % voltcurr[i][1])
                writer.Dispose()
                writer.Close()
            
            
            graphname = str(save_IV.FileName)[:-3]+"jpg" #save the plot with the same name of the txt file
            self.form_IV.plotIV.SaveImage(graphname, Graph.ChartImageFormat.Jpeg)            
            self.form_IV.sb_IV.Text = "Result: files saved"
 
            
        def FormIVClose(self, sender, args):
            
            self.StopClicked = True
            self.running = False #if Stop was already clicked once the IV is forced to immediately stop
            self.StopIV(self,self)
            self.form_IV.formClosed = True






#************************************************* TEST QUANTIZATION FORM **********************************************            
            
            
        def OpenFormQT(self, sender, args):
                        
            self.running= False
            
            #form for quantization test
            self.form_QT = Form()
            self.form_QT.Text = "PJVS Quantization Test"
            self.form_QT.Name = "PJVS Quantization Test"
            self.form_QT.Size = Size(900, 650)
            self.form_QT.CenterToScreen()
            
            #Button for initializing voltmeter
            self.form_QT.btn_InitVolt = Button()
            self.form_QT.btn_InitVolt.Text = "Initialize \n Voltmeter"
            self.form_QT.btn_InitVolt.Name = "InitVoltQT"        
            self.form_QT.btn_InitVolt.Font = Font("Serif", 12.)
            self.form_QT.btn_InitVolt.BackColor = Color.White
            self.form_QT.btn_InitVolt.Location = Point(50, 30)
            self.form_QT.btn_InitVolt.Size = Size (125, 50)
            if sim:
                self.form_QT.btn_InitVolt.Enabled = False
                
            self.form_QT.btn_InitVolt.Click += self.Call_InitVoltmeter
            
            self.form_QT.Controls.Add(self.form_QT.btn_InitVolt)

            
            #Bias currents in mA
            self.form_QT.current = Label()
            self.form_QT.current.Text = "Bias currents (mA)"
            self.form_QT.current.Font = Font("Serif", 11.)#, FontStyle.Bold) # don't know why it doesn't work anymore
            self.form_QT.current.BackColor = Color.LightBlue
            self.form_QT.current.Location = Point(40, 140)
            self.form_QT.current.AutoSize = True
            self.form_QT.Controls.Add(self.form_QT.current)            
            


            textbox_subjj = []
            label_subjj = []
            
            for i in range(n_subs): #n_subs is the number of subsections (14)
                x = NumericUpDown()
                y = Label()
                
                textbox_subjj.append(x)
                label_subjj.append(y)
                
            self.form_QT.list_textbox_subjj =  Array[NumericUpDown](textbox_subjj)            
            self.form_QT.list_label_subjj =  Array[Label](label_subjj)

            for i in range(len(label_subjj)):
            
                self.form_QT.list_label_subjj[i].Location = Point(10,int(170+i*25))
                self.form_QT.list_label_subjj[i].Font = Font("Serif", 11.)
                self.form_QT.list_label_subjj[i].Size = Size(70,15)
                self.form_QT.list_label_subjj[i].TextAlign = ContentAlignment.MiddleRight
                self.form_QT.list_label_subjj[i].BackColor = Color.LightBlue
                if QuantumTest_bits[i]==1:
                    self.form_QT.list_label_subjj[i].Text = ("%d (+)" % njj_subs_list[i])
                elif QuantumTest_bits[i]==-1:
                    self.form_QT.list_label_subjj[i].Text = ("%d (-)" % njj_subs_list[i])
                self.form_QT.Controls.Add(self.form_QT.list_label_subjj[i])
           
            self.form_QT.currents =[] #array containing all bias currents for quantization test
            for i in range(len(textbox_subjj)):
                self.form_QT.list_textbox_subjj[i].Location = Point(110,int(170+i*25))
            
                if QuantumTest_bits[i]==1:
                    self.form_QT.list_textbox_subjj[i].DecimalPlaces = 3
                    self.form_QT.list_textbox_subjj[i].Minimum = Decimal(0.)
                    self.form_QT.list_textbox_subjj[i].Maximum = Decimal(15.)
                    self.form_QT.list_textbox_subjj[i].Value = Decimal(1) #mA                    
                    self.form_QT.list_textbox_subjj[i].Increment = Decimal(0.002) #mA
                    self.form_QT.currents.append(float(self.form_QT.list_textbox_subjj[i].Text))
                    
                elif QuantumTest_bits[i]==-1:
                    
                    self.form_QT.list_textbox_subjj[i].DecimalPlaces = 3
                    self.form_QT.list_textbox_subjj[i].Minimum = Decimal(-15.)
                    self.form_QT.list_textbox_subjj[i].Maximum = Decimal(0.)
                    self.form_QT.list_textbox_subjj[i].Value = Decimal(-1) #mA 
                    self.form_QT.list_textbox_subjj[i].Increment = Decimal(0.002) #mA
                    self.form_QT.currents.append(float(self.form_QT.list_textbox_subjj[i].Text))

                self.form_QT.list_textbox_subjj[i].ValueChanged += self.ChangeCurrent    
                self.form_QT.list_textbox_subjj[i].Size = Size(80,10)

                self.form_QT.Controls.Add(self.form_QT.list_textbox_subjj[i])                                                
            
            #array of voltages on channels
            self.form_QT.Vout_array=[]                       

            
            #Checkbox inverting bias currents
            self.form_QT.btn_invert_curr = Button()
            self.form_QT.btn_invert_curr.Location = Point(55,530)
            self.form_QT.btn_invert_curr.Font = Font("Serif", 12.)
            self.form_QT.btn_invert_curr.Text = "Invert"
            self.form_QT.btn_invert_curr.Size = Size(90,40)
            self.form_QT.btn_invert_curr.Click += self.Inversion
            self.form_QT.Controls.Add(self.form_QT.btn_invert_curr)
            self.form_QT.inversion = False

            
            # bias currents panel
            self.form_QT.panel_currents = Panel()
            self.form_QT.panel_currents.Location = Point(5,130) 
            self.form_QT.panel_currents.Size = Size(200,450)
            self.form_QT.panel_currents.BackColor = Color.LightBlue
            self.form_QT.Controls.Add(self.form_QT.panel_currents)
            
            #NPLC voltmeter
            self.form_QT.volt_NPLC = Label()
            self.form_QT.volt_NPLC.Text = "NPLC (0.01-50): "
            self.form_QT.volt_NPLC.Font = Font("Serif", 11.)
            self.form_QT.volt_NPLC.Location = Point(15, 100)
            self.form_QT.volt_NPLC.AutoSize = True
            self.form_QT.Controls.Add(self.form_QT.volt_NPLC)            
            
            self.form_QT.in_volt_NPLC = TextBox()
            self.form_QT.in_volt_NPLC.Text = "1.0"
            self.form_QT.in_volt_NPLC.Location = Point(150, 100)
            self.form_QT.in_volt_NPLC.Size = Size(50, 10)
            self.form_QT.in_volt_NPLC.Leave += self.Set_in_volt_NPLC_Format
        
            self.form_QT.Controls.Add(self.form_QT.in_volt_NPLC)

            
            #null voltage measurement for testing quantization
            self.form_QT.null_volt = Label()
            self.form_QT.null_volt.Text = "Voltage (V) "
            self.form_QT.null_volt.Font = Font("Serif", 11.)
            self.form_QT.null_volt.FontBold = True
            self.form_QT.null_volt.Location = Point(700, 190)
            self.form_QT.null_volt.AutoSize = True
            
            self.form_QT.Controls.Add(self.form_QT.null_volt)

            self.form_QT.out_null_volt = TextBox()
            self.form_QT.out_null_volt.Text = "0." #volt
            self.form_QT.out_null_volt.Font = Font("Serif", 15.)
            self.form_QT.out_null_volt.Enabled = False
            self.form_QT.out_null_volt.Location = Point(670, 220)
            self.form_QT.out_null_volt.Size = Size(150,70)
            self.form_QT.out_null_volt.Leave += self.Set_out_null_volt_Format
            self.form_QT.out_null_volt.TextChanged += self.Set_out_null_volt_Format
            
            self.form_QT.Controls.Add(self.form_QT.out_null_volt)     

            #null voltage measurement standard deviation
            self.form_QT.null_volt_stdev = Label()
            self.form_QT.null_volt_stdev.Text = "Std. Dev. Voltage (V) "
            self.form_QT.null_volt_stdev.Font = Font("Serif", 11.)
            self.form_QT.null_volt_stdev.FontBold = True
            self.form_QT.null_volt_stdev.Location = Point(670, 280)
            self.form_QT.null_volt_stdev.AutoSize = True
            
            self.form_QT.Controls.Add(self.form_QT.null_volt_stdev)

            self.form_QT.out_null_volt_stdev = TextBox()
            self.form_QT.out_null_volt_stdev.Text = "0." #volt
            self.form_QT.out_null_volt_stdev.Font = Font("Serif", 15.)
            self.form_QT.out_null_volt_stdev.Enabled = False
            self.form_QT.out_null_volt_stdev.Location = Point(670, 310)
            self.form_QT.out_null_volt_stdev.Size = Size(150,70)
            self.form_QT.out_null_volt_stdev.Leave += self.Set_out_null_volt_Format
            self.form_QT.out_null_volt_stdev.TextChanged += self.Set_out_null_volt_Format
            
            self.form_QT.Controls.Add(self.form_QT.out_null_volt_stdev)            
            
            self.form_QT.out_null_volt_list = []
            
            #Plot Voltage values
            self.form_QT.plotQT = Graph.Chart()
            self.form_QT.plotQT.Location = Point(220, 10)
            self.form_QT.plotQT.Size = Size (400, 270)
            self.form_QT.areaQT = Graph.ChartArea()
            self.form_QT.plotQT.ChartAreas.Add(self.form_QT.areaQT)
            
            self.form_QT.areaQT.AxisX.MajorGrid.LineColor = Color.White
            self.form_QT.areaQT.AxisX.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            
            self.form_QT.areaQT.AxisY.IsStartedFromZero = False;
            #self.form_QT.areaQT.AxisX.MajorGrid.IntervalType = Graph.DateTimeIntervalType.Number
            #self.form_QT.areaQT.AxisX.MajorGrid.IntervalOffset = 0.
            self.form_QT.areaQT.AxisX.Title = 'Point'
            self.form_QT.areaQT.AxisX.TitleFont = Font("Serif", 12.)
            #self.form_QT.areaQT.AxisX.Minimum = 0.

            self.form_QT.areaQT.AxisY.MajorGrid.LineColor = Color.White
            self.form_QT.areaQT.AxisY.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            self.form_QT.areaQT.AxisY.Title = 'Voltage (V)'
            self.form_QT.areaQT.AxisY.TitleFont = Font("Serif", 12.)            
            self.form_QT.areaQT.BackColor = Color.LightGray
            self.form_QT.areaQT.AxisY.LabelStyle.Format = "E3"
            self.form_QT.areaQT.AxisX.LabelStyle.Format = "0"
            '''
            self.form_QT.areaQT.CursorX.Interval = 0
            self.form_QT.areaQT.CursorY.Interval = 0
            self.form_QT.areaQT.AxisX.ScaleView.Zoomable = True
            self.form_QT.areaQT.AxisY.ScaleView.Zoomable = True
        
            self.form_QT.areaQT.CursorX.IsUserEnabled = True
            self.form_QT.areaQT.CursorX.IsUserSelectionEnabled = True
            self.form_QT.areaQT.CursorX.SelectionColor = Color.Gray
            self.form_QT.areaQT.CursorY.SelectionColor = Color.Gray
            self.form_QT.areaQT.CursorY.IsUserEnabled = True
            self.form_QT.areaQT.CursorY.IsUserSelectionEnabled = True
            self.form_QT.areaQT.CursorX.LineColor = Color.Blue
            self.form_QT.areaQT.CursorX.LineWidth = 1
            self.form_QT.areaQT.CursorX.LineDashStyle = Graph.ChartDashStyle.DashDot
            self.form_QT.areaQT.CursorY.LineColor = Color.Blue
            self.form_QT.areaQT.CursorY.LineWidth = 1
            self.form_QT.areaQT.CursorY.LineDashStyle = Graph.ChartDashStyle.DashDot
            '''
            
            self.form_QT.seriesQT = Graph.Series("Quantization test")
            self.form_QT.seriesQT.ChartType = Graph.SeriesChartType.Line
            self.form_QT.seriesQT.Color = Color.Red
            self.form_QT.seriesQT.BorderWidth = 2
            self.form_QT.seriesQT.Points.AddXY(0.,0.)
            self.form_QT.plotQT.Series.Add(self.form_QT.seriesQT)
                   
            self.form_QT.Controls.Add(self.form_QT.plotQT)            


            #Plot Voltage Standard deviation values
            self.form_QT.plotQT_stdev = Graph.Chart()
            self.form_QT.plotQT_stdev.Location = Point(220, 310)
            self.form_QT.plotQT_stdev.Size = Size (400, 270)
            self.form_QT.areaQT_stdev = Graph.ChartArea()            
            self.form_QT.plotQT_stdev.ChartAreas.Add(self.form_QT.areaQT_stdev)
            
            self.form_QT.areaQT_stdev.AxisX.MajorGrid.LineColor = Color.White
            self.form_QT.areaQT_stdev.AxisX.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            
            self.form_QT.areaQT_stdev.AxisY.IsStartedFromZero = False;
            self.form_QT.areaQT_stdev.AxisX.Title = 'Point'
            self.form_QT.areaQT_stdev.AxisX.TitleFont = Font("Serif", 12.)

            self.form_QT.areaQT_stdev.AxisY.MajorGrid.LineColor = Color.White
            self.form_QT.areaQT_stdev.AxisY.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            self.form_QT.areaQT_stdev.AxisY.Title = 'Running Std.Dev (V)'
            self.form_QT.areaQT_stdev.AxisY.TitleFont = Font("Serif", 12.)            
            self.form_QT.areaQT_stdev.BackColor = Color.LightGray
            self.form_QT.areaQT_stdev.AxisY.LabelStyle.Format = "E3"
            self.form_QT.areaQT_stdev.AxisX.LabelStyle.Format = "0"
            
            self.form_QT.seriesQT_stdev = Graph.Series("Quantization test standard deviation")
            self.form_QT.seriesQT_stdev.ChartType = Graph.SeriesChartType.Line
            self.form_QT.seriesQT_stdev.Color = Color.Blue
            self.form_QT.seriesQT_stdev.BorderWidth = 2
            self.form_QT.seriesQT_stdev.Points.AddXY(0.,0.)
            self.form_QT.plotQT_stdev.Series.Add(self.form_QT.seriesQT_stdev)
                   
            self.form_QT.Controls.Add(self.form_QT.plotQT_stdev)              


            #Button for running Quantization test
            self.form_QT.btn_runQT = Button()
            self.form_QT.btn_runQT.Text = "Run"
            self.form_QT.btn_runQT.Font = Font("Serif", 12.)
            self.form_QT.btn_runQT.BackColor = Color.LimeGreen
            self.form_QT.btn_runQT.Location = Point(700, 380)
            self.form_QT.btn_runQT.Size = Size (100, 50)
            
            if sim:
                self.form_QT.btn_runQT.Enabled = True #SIMULATION
            else:
                self.form_QT.btn_runQT.Enabled = False
                
            self.form_QT.btn_runQT.Click += self.RunQT
            
            self.form_QT.Controls.Add(self.form_QT.btn_runQT)
            
            
            #Button for stopping quantization test
            self.form_QT.btn_stopQT = Button()
            self.form_QT.btn_stopQT.Text = "Stop"
            self.form_QT.btn_stopQT.Font = Font("Serif", 12.)
            self.form_QT.btn_stopQT.BackColor = Color.Red
            self.form_QT.btn_stopQT.Location = Point(700, 450)
            self.form_QT.btn_stopQT.Size = Size (100, 50)
            self.form_QT.btn_stopQT.Enabled = False
            self.form_QT.btn_stopQT.Click += self.StopQT
            
            self.form_QT.Controls.Add(self.form_QT.btn_stopQT)


            #Button for refreshing plot
            self.form_QT.btn_refreshQT = Button()
            self.form_QT.btn_refreshQT.Text = "Refresh"
            self.form_QT.btn_refreshQT.Font = Font("Serif", 12.)
            self.form_QT.btn_refreshQT.BackColor = Color.LightBlue
            self.form_QT.btn_refreshQT.Location = Point(700, 520)
            self.form_QT.btn_refreshQT.Size = Size (100, 50)
            self.form_QT.btn_refreshQT.Enabled = False
            self.form_QT.btn_refreshQT.Click += self.RefreshQT
            
            self.form_QT.Controls.Add(self.form_QT.btn_refreshQT)
            
            
            #INRIM_logo
            self.form_QT.logo = PictureBox()
            self.form_QT.logo.Location = Point(630, 40)
            self.form_QT.logo.Size = Size (240, 80)
            self.form_QT.logo.SizeMode = PictureBoxSizeMode.StretchImage
            self.form_QT.logo.Load("logo_inrim.jpg")
            self.form_QT.Controls.Add(self.form_QT.logo)            
            
            self.form_QT.sb_QT = StatusBar()
            self.form_QT.sb_QT.Text = "Ready"
            self.form_QT.sb_QT.Location = Point(20, 20)
            self.form_QT.Controls.Add(self.form_QT.sb_QT)   
          
            self.form_QT.counter =1
        
            self.form_QT.Closing += self.FormQTClose
            self.form_QT.formClosed = False
        
        
            self.form_QT.Show()
                        
            #self.Set_in_freqRF_QT_Format(self,self)
            #self.Set_in_current_QT_Format(self,self)
            self.Set_out_null_volt_Format(self,self)


        def Set_out_null_volt_Format(self, sender, args):
            number = '{0:.10f}'.format(float(self.form_QT.out_null_volt.Text))            
            self.form_QT.out_null_volt.Text = str(number)
            number2 = '{0:.10f}'.format(float(self.form_QT.out_null_volt_stdev.Text))
            self.form_QT.out_null_volt_stdev.Text = str(number2)


        def Inversion(self, sender, args):
            
            self.form_QT.inversion = not(self.form_QT.inversion)

            curr = [j for j in self.form_QT.currents]
            for i in range(len(curr)):
                
                if self.form_QT.inversion:
                    if QuantumTest_bits[i]==1:
                        self.form_QT.list_label_subjj[i].Text = ("%d (-)" % njj_subs_list[i])
                        self.form_QT.list_textbox_subjj[i].Minimum = Decimal(-15.)    
                        self.form_QT.list_textbox_subjj[i].Text = str(-1.*curr[i]) #mA
                        self.form_QT.list_textbox_subjj[i].Maximum = Decimal(0.)
                        
                    elif QuantumTest_bits[i]==-1:
                        self.form_QT.list_label_subjj[i].Text = ("%d (+)" % njj_subs_list[i])
                        self.form_QT.list_textbox_subjj[i].Maximum = Decimal(15.)    
                        self.form_QT.list_textbox_subjj[i].Text = str(-1.*curr[i]) #mA
                        self.form_QT.list_textbox_subjj[i].Minimum = Decimal(0.)                         
                else:
                    if QuantumTest_bits[i]==1:
                        self.form_QT.list_label_subjj[i].Text = ("%d (+)" % njj_subs_list[i])
                        self.form_QT.list_textbox_subjj[i].Maximum = Decimal(15.)    
                        self.form_QT.list_textbox_subjj[i].Text = str(-1.*curr[i]) #mA
                        self.form_QT.list_textbox_subjj[i].Minimum = Decimal(0.)                         
                    elif QuantumTest_bits[i]==-1:
                        self.form_QT.list_label_subjj[i].Text = ("%d (-)" % njj_subs_list[i])
                        self.form_QT.list_textbox_subjj[i].Minimum = Decimal(-15.)    
                        self.form_QT.list_textbox_subjj[i].Text = str(-1.*curr[i]) #mA
                        self.form_QT.list_textbox_subjj[i].Maximum = Decimal(0.)                        
    
            self.form_QT.currents = [-1.*j for j in curr]
            curr.clear()
            

                
        #change bias current in real time
        def ChangeCurrent(self, sender, args):
            #if self.running == True:
            freqRF = float(self.in_freqRF.Text) # GHz
                       
            Vlsb = Math_Functions.EvalParameters(freqRF)[0]
            R = 50 # Ohm, output resistance of each channel
            self.form_QT.currents=[]             
            for i in range(len(self.form_QT.list_textbox_subjj)):
                self.form_QT.currents.append(float(self.form_QT.list_textbox_subjj[i].Text))                
            self.form_QT.Vout_array = Math_Functions.QuantumTest(Vlsb, self.form_QT.currents, n_subs, R, self.form_QT.inversion)
            if not sim:
                Devices_Control.SetDCVoltages(self.device, self.form_QT.Vout_array) #call function in Devices_Control for setting dc voltages to each channel                

                

        #Runs the quantization test calling function from Devices_Control
        def RunQT(self, sender, args):
            
                if not sim:  
                    setimp_QT = Devices_Control.SetImpedance(self.device)  #reset the correct output impedances values for each channel
                    if setimp_QT=="ERR_IMP":
                        self.sb.Text = "WARNING: Output impedance not correctly set!"
                        return(-1)
                        
                                             
                self.running = True
                self.form_QT.seriesQT.Points.RemoveItem(0)
                self.form_QT.sb_QT.Text = "RUN"
                self.form_QT.btn_runQT.Enabled = False
                self.form_QT.btn_stopQT.Enabled = True
                self.form_QT.btn_refreshQT.Enabled = True
                                

                while self.running:
                    
                    Application.DoEvents()
                    if self.form_QT.formClosed:
                        self.running = False
                        break
                    
                    if sim:
                        current = mean(self.form_QT.currents)
                        Vread = current*uniform(-1.,1.)/100000.
                    else:
                        if self.running:
                            self.ChangeCurrent(self,self)
                            Vread = float(Devices_Control.ReadVolt(self.voltmeter)) #voltage read by the voltmeter

                    self.form_QT.out_null_volt_list.append(Vread)
                    Vstddev = std(self.form_QT.out_null_volt_list)

                             
                    '''
                    #stuff for the plot scale
                    if Vread > self.form_QT.areaQT.AxisY.Maximum:
                        self.form_QT.areaQT.AxisY.Maximum = Vread
            
                    if Vread < self.form_QT.areaQT.AxisY.Minimum:
                        self.form_QT.areaQT.AxisY.Minimum = Vread
                    
                    
                    if self.form_QT.counter ==1:
                         self.form_QT.seriesQT.Points.RemoveItem(0)
                         self.form_QT.areaQT.AxisY.Maximum = Vread+Vread/100.
                         self.form_QT.areaQT.AxisY.Minimum = Vread-Vread/100.
                    '''     
                    self.form_QT.seriesQT.Points.AddXY(float(self.form_QT.counter),float(Vread))
                    self.form_QT.out_null_volt.Text = str(Vread)
                    
                    self.form_QT.seriesQT_stdev.Points.AddXY(float(self.form_QT.counter),float(Vstddev))
                    self.form_QT.out_null_volt_stdev.Text = str(Vstddev)
                    
                    if sim:
                        time.sleep(0.05) #SIMULATION
    
                    self.form_QT.counter+=1


        def StopQT(self, sender, args):
            
            Application.DoEvents()            
            self.running = False
               
            self.form_QT.sb_QT.Text = "STOP"
            self.form_QT.btn_runQT.Enabled = True
            self.form_QT.btn_stopQT.Enabled = False
            self.form_QT.btn_stopQT.BackColor = Color.Red
            if not sim:
                zero_volt_array = n_subs*[0.0]
                setvolt = Devices_Control.SetDCVoltages(self.device, zero_volt_array)
                if setvolt == "ERR_SET_VOLT":
                    self.form_QT.sb.Text = "WARNING: Voltage not correctly set!"
                    return(-1)                   
                    
                
                #Devices_Control.Stop(self.device) #Stop devices
                #self.form_QT.seriesQT.Points.RemoveItem(int(self.form_QT.counter)-int(1))
                
        def RefreshQT(self, sender, args):
            
            Application.DoEvents()             
            self.form_QT.seriesQT.Points.Clear()
            self.form_QT.seriesQT_stdev.Points.Clear()             
            self.form_QT.out_null_volt_list = []
            if not self.running:                
                self.form_QT.seriesQT.Points.AddXY(0.,0.)
                self.form_QT.seriesQT_stdev.Points.AddXY(0.,0.)        
            self.form_QT.counter = 1




        def FormQTClose(self, sender, args):
        
            self.StopQT(self,self)
            self.form_QT.formClosed = True

    
           
