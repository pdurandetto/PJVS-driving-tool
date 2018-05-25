#GRAPHICS PART
import clr
import Math_Functions
import File_Utilities
import Devices_Control
from numpy import diff, arange, sign, array, mean, linspace, std
from System import Array, EventArgs, Decimal, UInt32, Int32
import time #needed for simulation 
from random import uniform #needed for simulation
import Settings

clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.Drawing import Point, Size, Font, Color 
from System.Windows.Forms import Application, Form, Button, Label,TextBox, StatusBar, MessageBox, Panel, RadioButton, DataVisualization, GroupBox, PictureBox, CheckBox, NumericUpDown, PictureBoxSizeMode

Graph = DataVisualization.Charting

sim= Settings.SIMULATION #global variable set in Main.py, if sim= True then the program is in simulation mode
vmax_awg = Settings.VOLT_MAX_AWG
njj_subs_list = Settings.NJJ_SUBSECTIONS_LIST

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
            self.btn_INIT.Text = "INITIALIZE \n AWGs 1104"
            self.btn_INIT.Font = Font("Serif", 12.)
            self.btn_INIT.BackColor = Color.White
            self.btn_INIT.Location = Point(30, 40)
            self.btn_INIT.Size = Size (150, 75)
            self.btn_INIT.Click += self.Call_InitDevices
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
            
            #Bias current in mA
            self.current = Label()
            self.current.Text = "Bias current (mA): "
            self.current.Font = Font("Serif", 11.)
            self.current.Location = Point(20, 230)
            self.current.AutoSize = True
            
            self.Controls.Add(self.current)
            
            self.in_current = TextBox()
            self.in_current.Text = "1" # mA
            self.in_current.Location = Point(220, 230)
            self.in_current.Size = Size(100, 10)
            self.in_current.Leave += self.Set_in_current_Format
            
            self.Controls.Add(self.in_current)
            
           
            #Signal frequency in kHz
            self.freq_signal = Label()
            self.freq_signal.Text = "Signal frequency (kHz):"
            self.freq_signal.Font = Font("Serif", 11.)
            self.freq_signal.Location = Point(20, 260)
            self.freq_signal.AutoSize = True
            
            self.Controls.Add(self.freq_signal)
            
            self.in_freq_signal = TextBox()
            self.in_freq_signal.Text = "1" #kHz
            self.in_freq_signal.Location = Point(220, 260)
            self.in_freq_signal.Size = Size(100, 10)
            self.in_freq_signal.Leave += self.Set_in_freq_signal_Format
            self.Controls.Add(self.in_freq_signal)
            
            #Signal amplitude in V
            self.amp_signal = Label()
            self.amp_signal.Text = "Signal amplitude (V):"
            self.amp_signal.Font = Font("Serif", 11.)
            self.amp_signal.Location = Point(20, 290)
            self.amp_signal.AutoSize = True
                       
            self.Controls.Add(self.amp_signal)
            
            self.in_amp_signal = TextBox()
            self.in_amp_signal.Text = "1"  #V
            self.in_amp_signal.Location = Point(220, 290)
            self.in_amp_signal.Size = Size(100, 10)
            self.in_amp_signal.Leave += self.Set_in_volt_Format
            
            self.Controls.Add(self.in_amp_signal)

            #Signal phase in degrees
            self.phase = Label()
            self.phase.Text = "Signal phase (°):"
            self.phase.Font = Font("Serif", 11.)
            self.phase.Location = Point(20, 320)
            self.phase.AutoSize = True
            
            self.Controls.Add(self.phase)
            
            self.in_phase = TextBox()
            self.in_phase.Text = "0" #°
            self.in_phase.Location = Point(220, 320)
            self.in_phase.Size = Size(100, 10)
            self.in_phase.Leave += self.Set_in_phase_Format
            
            self.Controls.Add(self.in_phase)


            #Signal offset in V
            self.offset = Label()
            self.offset.Text = "Offset (V):"
            self.offset.Font = Font("Serif", 11.)
            self.offset.Location = Point(20, 350)
            self.offset.AutoSize = True
            
            self.Controls.Add(self.offset)
            
            self.in_offset = TextBox()
            self.in_offset.Text = "0" #V
            self.in_offset.Location = Point(220, 350)
            self.in_offset.Size = Size(100, 10)
            self.in_offset.Leave += self.Set_in_volt_Format
            self.Controls.Add(self.in_offset)

            #Number of steps
            self.n_steps = Label()
            self.n_steps.Text = "Steps per period \n (even number)"
            self.n_steps.Font = Font("Serif", 11.)
            self.n_steps.Location = Point(20, 380)
            self.n_steps.AutoSize = True
            
            self.Controls.Add(self.n_steps)
            
            self.in_n_steps = TextBox()
            self.in_n_steps.Text = "20"
            self.in_n_steps.Location = Point(220, 380)
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
            self.btn_LOAD.Text = "LOAD \n WAVES"
            self.btn_LOAD.Font = Font("Serif", 12.)
            self.btn_LOAD.BackColor = Color.White
            self.btn_LOAD.Location = Point(550, 500)
            self.btn_LOAD.Size = Size (150, 75)
            
            if sim:
                self.btn_LOAD.Enabled = True   #SIMULATION
            else:
                self.btn_LOAD.Enabled = False
                
            self.btn_LOAD.Click += self.Call_Eval_Parameters
            self.btn_LOAD.Click += self.Call_Load
            
            self.Controls.Add(self.btn_LOAD)
            
            #RUN button: runs AWGs channels
            self.btn_RUN = Button()
            self.btn_RUN.Text = "START"
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
            self.btn_TQ = Button()
            self.btn_TQ.Text = "Test Quantization"
            self.btn_TQ.Font = Font("Serif", 12.)
            self.btn_TQ.BackColor = Color.White
            self.btn_TQ.Location = Point(200, 80)
            self.btn_TQ.Size = Size (120, 50)
            if sim:        
                self.btn_TQ.Enabled = True      # SIMULATION
            else:
                self.btn_TQ.Enabled = False
                
            self.btn_TQ.Click += self.OpenFormTQ
            self.Controls.Add(self.btn_TQ)


            #function called for formatting the textboxes
            self.Call_Eval_Parameters(self,self) #called for evaluating parameters as soon as the form is opened, any two arguments are required although not used
            self.Set_in_freqRF_Format(self,self)
            self.Set_in_current_Format(self,self)
            self.Set_in_freq_signal_Format(self,self)
            self.Set_in_volt_Format(self,self)
            self.Set_in_phase_Format(self,self)
            self.Set_in_n_steps_Format(self,self)
            
########################################################################### end of constructor
            
            
        #functions for formatting the textboxes    
        def Set_in_freqRF_Format(self, sender, args):
            number = '{0:.3f}'.format(float(self.in_freqRF.Text))
            self.in_freqRF.Text = str(number)
            self.Call_Eval_Parameters(self,self)
            self.Set_in_volt_Format(self, self)
            
        
        def Set_in_current_Format(self, sender, args):
            number = '{0:.3f}'.format(float(self.in_current.Text))
            self.in_current.Text = str(number)

        def Set_in_freq_signal_Format(self, sender, args):
            # it recalculates the frequency according to Sampling Rate Prescaler, signal frequency and number of points, having fixed the sample rate            
            number = '{0:.6f}'.format(self.Call_RecalcFreq(self,self))
            self.in_freq_signal.Text = str(number)
            
        #It calls QuantumVolt for quantizing the voltage
        def Set_in_volt_Format(self, sender, args):
            
            Vamp = float(self.in_amp_signal.Text)
            Voffset = float(self.in_offset.Text)            
            Vamp_q= Math_Functions.CalcQuantumVolt(Vamp, float(self.in_freqRF.Text), 50, float(self.in_current.Text), n_subs)[1] #current in mA, element 1 of the output of CalcQuantumVolt
            Voffset_q= Math_Functions.CalcQuantumVolt(Voffset, float(self.in_freqRF.Text), 50, float(self.in_current.Text), n_subs)[1]                   
                        
            if (abs(Vamp_q)+abs(Voffset_q))>self.volt_max:
                if sender==self.in_offset:
                    Voffset_q = Math_Functions.CalcQuantumVolt(sign(Voffset_q)*(self.volt_max-abs(Vamp_q)),float(self.in_freqRF.Text), 50, float(self.in_current.Text), n_subs)[1]
                    
                elif sender==self.in_amp_signal:
                    Vamp_q = Math_Functions.CalcQuantumVolt(sign(Vamp_q)*(self.volt_max-abs(Voffset_q)), float(self.in_freqRF.Text), 50, float(self.in_current.Text), n_subs)[1]
                    
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
                


        #It calculates sampling rate and single junction voltage drop. It uses Eval_Parameters defined in module Math_Functions.
        def Call_Eval_Parameters(self, sender, args):
            
            freqRF = float(self.in_freqRF.Text)
            freq_signal = float(self.in_freq_signal.Text) #kHz
            n_steps = int(self.in_n_steps.Text)            
            
            Param_array = Math_Functions.Eval_Parameters(freqRF)
            
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
            self.Call_Eval_Parameters(sender, args)
            return(pars_freq[0])
            
        
        #Initialize AWGs calling InitDevices function defined in Device_Controls
        def Call_InitDevices(self, sender, args):
            Application.DoEvents()
            finddev = Devices_Control.InitDevices() #result of InitDevices functions
            
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
                    self.btn_TQ.Enabled = True
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
                I_bias = float(self.in_current.Text) #mA
                
                                
                if self.waveform == "SIN":
                    Vout = Math_Functions.Calc_Sine(amp, freq, phase, offset, n_steps, freqRF, R_out, I_bias, n_subs)
                    self.Vmatrix = Vout[0]
                    
                if self.waveform == "SQR":
                    Vout = Math_Functions.Calc_Square(amp, freq, phase, offset, n_steps, freqRF, R_out, I_bias, n_subs)
                    self.Vmatrix = Vout[0]
                    
                if self.waveform == "TRN":
                    Vout = Math_Functions.Calc_Triang(amp, freq, phase, offset, n_steps, freqRF, R_out, I_bias, n_subs)
                    self.Vmatrix = Vout[0]
                                
                #print(array(self.Vmatrix)[:,13])
                
                
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
       
            

                       
            
            
#************************************************* IV-CHARACTERISTIC FORM **********************************************            
            
            
        def OpenFormIV(self, sender, args):
                        
            self.running= False
            
            #form for IV characteristics
            self.form_IV = Form()
            self.form_IV.Text = "PJVS IVs"
            self.form_IV.Name = "PJVS IVs"
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
            self.form_IV.Rjj.Location = Point(10, 170)
            self.form_IV.Rjj.AutoSize = True
            
            self.form_IV.Controls.Add(self.form_IV.Rjj)            
            '''
            self.form_IV.in_Rjj = TextBox()
            self.form_IV.in_Rjj.Text = "0.065" #Ohm
            '''self.form_IV.in_Rjj.Location = Point(185, 170)
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
            self.form_IV.btn_saveIV.Click += self.Save
            
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
            if sender.Name== "InitVoltTQ":
                nplc = float(self.form_TQ.in_volt_NPLC.Text)          
                        
            self.voltmeter = Devices_Control.InitVoltmeter(nplc) #call InitVoltmeter from Devices_Control
            if self.voltmeter == "ERR_VOLT":
                    if sender.Name== "InitVoltIV":
                        self.form_IV.sb_IV.Text = "Result: Voltmeter not found!"
                    if sender.Name== "InitVoltTQ":
                        self.form_TQ.sb_TQ.Text = "Result: Voltmeter not found!"                        
                    return(-1)
            else:
                if sender.Name=="InitVoltIV":
                    self.form_IV.sb_IV.Text = "Result: Voltmeter correctly initialized"
                    self.form_IV.btn_InitVolt.BackColor = Color.LightBlue
                    self.form_IV.btn_runIV.Enabled = True
                    
                if sender.Name=="InitVoltTQ":
                    self.form_TQ.sb_TQ.Text = "Result: Voltmeter correctly initialized"
                    self.form_TQ.btn_InitVolt.BackColor = Color.LightBlue
                    self.form_TQ.btn_runTQ.Enabled = True
        
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
                    act_ch = Devices_Control.SetImpedanceIV(self.device, subs_status) #gets the index of the unique channel that is active
                    
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
                
                pars = Math_Functions.Eval_Parameters(float(self.in_freqRF.Text))
                
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
                            Devices_Control.SetVoltageToSubsect(self.device, act_ch, Vch) #call function in Devices_Control for setting Vch to the active channel                
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
                    


        #opens a new form for saving the IV (txt and jpeg)
        def Save(self, sender, args):
            self.form_save = Form()
            self.form_save.Text = "Save IV characteristic"
            self.form_save.Name = "Save IV characteristic"
            self.form_save.Size = Size(250, 200)
            self.form_save.CenterToScreen()        
            
            #Save IV button
            self.form_save.btn_saveIV = Button()
            self.form_save.btn_saveIV.Text = "Save"
            self.form_save.btn_saveIV.Font = Font("Serif", 12.)
            self.form_save.btn_saveIV.BackColor = Color.White
            self.form_save.btn_saveIV.Location = Point(50, 50)
            self.form_save.btn_saveIV.Size = Size (125, 50)
            
            self.form_save.btn_saveIV.Click += self.CallSaveIV
            
            self.form_save.Controls.Add(self.form_save.btn_saveIV)
            
            self.form_save.in_filename = TextBox()
            self.form_save.in_filename.Text = self.form_IV.in_note.Text
            self.form_save.in_filename.Location = Point(20, 20)
            self.form_save.in_filename.Size = Size(200, 10)
            self.form_save.in_filename.Font = Font("Serif", 12.)
            self.form_save.Controls.Add(self.form_save.in_filename)
            
            self.form_save.Show()


        
        def CallSaveIV(self, sender, args):
            data = self.form_IV.seriesIV.Points
            note = str(self.form_IV.in_note.Text)
            namefile = self.form_save.in_filename.Text
            
            File_Utilities.SaveIV(data, namefile, note)#call the functions for save txt and return the name of the file
                        
            self.form_save.Close()
 
            
        def FormIVClose(self, sender, args):
            
            self.StopClicked = True
            self.running = False #if Stop was already clicked once the IV is forced to immediately stop
            self.StopIV(self,self)
            self.form_IV.formClosed = True






#************************************************* TEST QUANTIZATION FORM **********************************************            
            
            
        def OpenFormTQ(self, sender, args):
                        
            self.running= False
            
            #form for quantization test
            self.form_TQ = Form()
            self.form_TQ.Text = "PJVS Quantization Test"
            self.form_TQ.Name = "PJVS Quantization Test"
            self.form_TQ.Size = Size(900, 600)
            self.form_TQ.CenterToScreen()
            
            #Button for initializing voltmeter
            self.form_TQ.btn_InitVolt = Button()
            self.form_TQ.btn_InitVolt.Text = "Initialize \n Voltmeter"
            self.form_TQ.btn_InitVolt.Name = "InitVoltTQ"        
            self.form_TQ.btn_InitVolt.Font = Font("Serif", 12.)
            self.form_TQ.btn_InitVolt.BackColor = Color.White
            self.form_TQ.btn_InitVolt.Location = Point(50, 30)
            self.form_TQ.btn_InitVolt.Size = Size (125, 50)
            if sim:
                self.form_TQ.btn_InitVolt.Enabled = False
                
            self.form_TQ.btn_InitVolt.Click += self.Call_InitVoltmeter
            
            self.form_TQ.Controls.Add(self.form_TQ.btn_InitVolt)


            #Bias current in mA
            self.form_TQ.current = Label()
            self.form_TQ.current.Text = "Bias current (mA): "
            self.form_TQ.current.Font = Font("Serif", 11.)
            self.form_TQ.current.Location = Point(10, 130)
            self.form_TQ.current.AutoSize = True
            self.form_TQ.Controls.Add(self.form_TQ.current)            
            
            self.form_TQ.in_current = NumericUpDown() #TextBox()
            self.form_TQ.in_current.Text = "0." #mA
            self.form_TQ.in_current.Value = Decimal(0) #mA
            self.form_TQ.in_current.DecimalPlaces = 3
            self.form_TQ.in_current.Minimum = Decimal(0)
            self.form_TQ.in_current.Maximum = Decimal(15)
            self.form_TQ.in_current.Increment = Decimal(0.002) #mA
            self.form_TQ.in_current.Location = Point(165, 130)
            self.form_TQ.in_current.Size = Size(70, 10)
            self.form_TQ.in_current.Leave += self.Set_in_current_TQ_Format
            self.form_TQ.in_current.ValueChanged += self.ChangeCurrent
        
            self.form_TQ.Controls.Add(self.form_TQ.in_current)
        
            #array of voltages on channels
            self.form_TQ.Vout_array=[]                       
            
            #Microwave frequency in GHz
            self.form_TQ.freqRF = Label()
            self.form_TQ.freqRF.Text = "RF frequency (GHz): "
            self.form_TQ.freqRF.Font = Font("Serif", 11.)
            self.form_TQ.freqRF.Location = Point(10, 100)
            self.form_TQ.freqRF.AutoSize = True
            
            self.form_TQ.Controls.Add(self.form_TQ.freqRF)
            
            self.form_TQ.in_freqRF = TextBox()
            self.form_TQ.in_freqRF.Text = "76.5" #GHz
            self.form_TQ.in_freqRF.Location = Point(165, 100)
            self.form_TQ.in_freqRF.Size = Size(70, 10)
            self.form_TQ.in_freqRF.Leave += self.Set_in_freqRF_TQ_Format
            
            self.form_TQ.Controls.Add(self.form_TQ.in_freqRF)

            #NPLC voltmeter
            self.form_TQ.volt_NPLC = Label()
            self.form_TQ.volt_NPLC.Text = "NPLC (0.01-50): "
            self.form_TQ.volt_NPLC.Font = Font("Serif", 11.)
            self.form_TQ.volt_NPLC.Location = Point(10, 160)
            self.form_TQ.volt_NPLC.AutoSize = True
            self.form_TQ.Controls.Add(self.form_TQ.volt_NPLC)            
            
            self.form_TQ.in_volt_NPLC = TextBox()
            self.form_TQ.in_volt_NPLC.Text = "1.0"
            self.form_TQ.in_volt_NPLC.Location = Point(165, 160)
            self.form_TQ.in_volt_NPLC.Size = Size(50, 10)
            self.form_TQ.in_volt_NPLC.Leave += self.Set_in_volt_NPLC_Format
        
            self.form_TQ.Controls.Add(self.form_TQ.in_volt_NPLC)


            #Checkbox inverting bias currents
            self.form_TQ.checkbox_invert_curr = CheckBox()
            self.form_TQ.checkbox_invert_curr.Location = Point(10,190)
            self.form_TQ.checkbox_invert_curr.Font = Font("Serif", 11.)
            self.form_TQ.checkbox_invert_curr.Text = "Invert"
            self.form_TQ.checkbox_invert_curr.Checked = False
            self.form_TQ.checkbox_invert_curr.CheckedChanged += self.ChangeCurrent
            self.form_TQ.Controls.Add(self.form_TQ.checkbox_invert_curr)

            
            #null voltage measurement for testing quantization
            self.form_TQ.null_volt = Label()
            self.form_TQ.null_volt.Text = "Voltage (V) "
            self.form_TQ.null_volt.Font = Font("Serif", 11.)
            self.form_TQ.null_volt.FontBold = True
            self.form_TQ.null_volt.Location = Point(80, 270)
            self.form_TQ.null_volt.AutoSize = True
            
            self.form_TQ.Controls.Add(self.form_TQ.null_volt)

            self.form_TQ.out_null_volt = TextBox()
            self.form_TQ.out_null_volt.Text = "0." #volt
            self.form_TQ.out_null_volt.Font = Font("Serif", 15.)
            self.form_TQ.out_null_volt.Enabled = False
            self.form_TQ.out_null_volt.Location = Point(50, 300)
            self.form_TQ.out_null_volt.Size = Size(150,70)
            self.form_TQ.out_null_volt.Leave += self.Set_out_null_volt_Format
            self.form_TQ.out_null_volt.TextChanged += self.Set_out_null_volt_Format
            
            self.form_TQ.Controls.Add(self.form_TQ.out_null_volt)     

            #null voltage measurement standard deviation
            self.form_TQ.null_volt_stdev = Label()
            self.form_TQ.null_volt_stdev.Text = "Std. Dev. Voltage (V) "
            self.form_TQ.null_volt_stdev.Font = Font("Serif", 11.)
            self.form_TQ.null_volt_stdev.FontBold = True
            self.form_TQ.null_volt_stdev.Location = Point(50, 350)
            self.form_TQ.null_volt_stdev.AutoSize = True
            
            self.form_TQ.Controls.Add(self.form_TQ.null_volt_stdev)

            self.form_TQ.out_null_volt_stdev = TextBox()
            self.form_TQ.out_null_volt_stdev.Text = "0." #volt
            self.form_TQ.out_null_volt_stdev.Font = Font("Serif", 15.)
            self.form_TQ.out_null_volt_stdev.Enabled = False
            self.form_TQ.out_null_volt_stdev.Location = Point(50, 380)
            self.form_TQ.out_null_volt_stdev.Size = Size(150,70)
            self.form_TQ.out_null_volt_stdev.Leave += self.Set_out_null_volt_Format
            self.form_TQ.out_null_volt_stdev.TextChanged += self.Set_out_null_volt_Format
            
            self.form_TQ.Controls.Add(self.form_TQ.out_null_volt_stdev)            
            
            self.form_TQ.out_null_volt_list = []
            
            #Plot Voltage values
            self.form_TQ.plotTQ = Graph.Chart()
            self.form_TQ.plotTQ.Location = Point(260, 10)
            self.form_TQ.plotTQ.Size = Size (450, 250)
            self.form_TQ.areaTQ = Graph.ChartArea()
            self.form_TQ.plotTQ.ChartAreas.Add(self.form_TQ.areaTQ)
            
            self.form_TQ.areaTQ.AxisX.MajorGrid.LineColor = Color.White
            self.form_TQ.areaTQ.AxisX.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            
            self.form_TQ.areaTQ.AxisY.IsStartedFromZero = False;
            #self.form_TQ.areaTQ.AxisX.MajorGrid.IntervalType = Graph.DateTimeIntervalType.Number
            #self.form_TQ.areaTQ.AxisX.MajorGrid.IntervalOffset = 0.
            self.form_TQ.areaTQ.AxisX.Title = 'Point'
            self.form_TQ.areaTQ.AxisX.TitleFont = Font("Serif", 12.)
            #self.form_TQ.areaTQ.AxisX.Minimum = 0.

            self.form_TQ.areaTQ.AxisY.MajorGrid.LineColor = Color.White
            self.form_TQ.areaTQ.AxisY.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            self.form_TQ.areaTQ.AxisY.Title = 'Voltage (V)'
            self.form_TQ.areaTQ.AxisY.TitleFont = Font("Serif", 12.)            
            self.form_TQ.areaTQ.BackColor = Color.LightGray
            self.form_TQ.areaTQ.AxisY.LabelStyle.Format = "E3"
            self.form_TQ.areaTQ.AxisX.LabelStyle.Format = "0"
            '''
            self.form_TQ.areaTQ.CursorX.Interval = 0
            self.form_TQ.areaTQ.CursorY.Interval = 0
            self.form_TQ.areaTQ.AxisX.ScaleView.Zoomable = True
            self.form_TQ.areaTQ.AxisY.ScaleView.Zoomable = True
        
            self.form_TQ.areaTQ.CursorX.IsUserEnabled = True
            self.form_TQ.areaTQ.CursorX.IsUserSelectionEnabled = True
            self.form_TQ.areaTQ.CursorX.SelectionColor = Color.Gray
            self.form_TQ.areaTQ.CursorY.SelectionColor = Color.Gray
            self.form_TQ.areaTQ.CursorY.IsUserEnabled = True
            self.form_TQ.areaTQ.CursorY.IsUserSelectionEnabled = True
            self.form_TQ.areaTQ.CursorX.LineColor = Color.Blue
            self.form_TQ.areaTQ.CursorX.LineWidth = 1
            self.form_TQ.areaTQ.CursorX.LineDashStyle = Graph.ChartDashStyle.DashDot
            self.form_TQ.areaTQ.CursorY.LineColor = Color.Blue
            self.form_TQ.areaTQ.CursorY.LineWidth = 1
            self.form_TQ.areaTQ.CursorY.LineDashStyle = Graph.ChartDashStyle.DashDot
            '''
            
            self.form_TQ.seriesTQ = Graph.Series("Quantization test")
            self.form_TQ.seriesTQ.ChartType = Graph.SeriesChartType.Line
            self.form_TQ.seriesTQ.Color = Color.Red
            self.form_TQ.seriesTQ.BorderWidth = 2
            self.form_TQ.seriesTQ.Points.AddXY(0.,0.)
            self.form_TQ.plotTQ.Series.Add(self.form_TQ.seriesTQ)
                   
            self.form_TQ.Controls.Add(self.form_TQ.plotTQ)            


            #Plot Voltage Standard deviation values
            self.form_TQ.plotTQ_stdev = Graph.Chart()
            self.form_TQ.plotTQ_stdev.Location = Point(260, 280)
            self.form_TQ.plotTQ_stdev.Size = Size (450, 250)
            self.form_TQ.areaTQ_stdev = Graph.ChartArea()            
            self.form_TQ.plotTQ_stdev.ChartAreas.Add(self.form_TQ.areaTQ_stdev)
            
            self.form_TQ.areaTQ_stdev.AxisX.MajorGrid.LineColor = Color.White
            self.form_TQ.areaTQ_stdev.AxisX.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            
            self.form_TQ.areaTQ_stdev.AxisY.IsStartedFromZero = False;
            self.form_TQ.areaTQ_stdev.AxisX.Title = 'Point'
            self.form_TQ.areaTQ_stdev.AxisX.TitleFont = Font("Serif", 12.)

            self.form_TQ.areaTQ_stdev.AxisY.MajorGrid.LineColor = Color.White
            self.form_TQ.areaTQ_stdev.AxisY.MajorGrid.LineDashStyle = Graph.ChartDashStyle.Dash
            self.form_TQ.areaTQ_stdev.AxisY.Title = 'Std.Dev Voltage (V)'
            self.form_TQ.areaTQ_stdev.AxisY.TitleFont = Font("Serif", 12.)            
            self.form_TQ.areaTQ_stdev.BackColor = Color.LightGray
            self.form_TQ.areaTQ_stdev.AxisY.LabelStyle.Format = "E3"
            self.form_TQ.areaTQ_stdev.AxisX.LabelStyle.Format = "0"
            
            self.form_TQ.seriesTQ_stdev = Graph.Series("Quantization test standard deviation")
            self.form_TQ.seriesTQ_stdev.ChartType = Graph.SeriesChartType.Line
            self.form_TQ.seriesTQ_stdev.Color = Color.Blue
            self.form_TQ.seriesTQ_stdev.BorderWidth = 2
            self.form_TQ.seriesTQ_stdev.Points.AddXY(0.,0.)
            self.form_TQ.plotTQ_stdev.Series.Add(self.form_TQ.seriesTQ_stdev)
                   
            self.form_TQ.Controls.Add(self.form_TQ.plotTQ_stdev)              


            #Button for running Quantization test
            self.form_TQ.btn_runTQ = Button()
            self.form_TQ.btn_runTQ.Text = "Run"
            self.form_TQ.btn_runTQ.Font = Font("Serif", 12.)
            self.form_TQ.btn_runTQ.BackColor = Color.LimeGreen
            self.form_TQ.btn_runTQ.Location = Point(740, 180)
            self.form_TQ.btn_runTQ.Size = Size (100, 50)
            
            if sim:
                self.form_TQ.btn_runTQ.Enabled = True #SIMULATION
            else:
                self.form_TQ.btn_runTQ.Enabled = False
                
            self.form_TQ.btn_runTQ.Click += self.RunTQ
            
            self.form_TQ.Controls.Add(self.form_TQ.btn_runTQ)
            
            
            #Button for stopping quantization test
            self.form_TQ.btn_stopTQ = Button()
            self.form_TQ.btn_stopTQ.Text = "Stop"
            self.form_TQ.btn_stopTQ.Font = Font("Serif", 12.)
            self.form_TQ.btn_stopTQ.BackColor = Color.Red
            self.form_TQ.btn_stopTQ.Location = Point(740, 250)
            self.form_TQ.btn_stopTQ.Size = Size (100, 50)
            self.form_TQ.btn_stopTQ.Enabled = False
            self.form_TQ.btn_stopTQ.Click += self.StopTQ
            
            self.form_TQ.Controls.Add(self.form_TQ.btn_stopTQ)


            #Button for refreshing plot
            self.form_TQ.btn_refreshTQ = Button()
            self.form_TQ.btn_refreshTQ.Text = "Refresh"
            self.form_TQ.btn_refreshTQ.Font = Font("Serif", 12.)
            self.form_TQ.btn_refreshTQ.BackColor = Color.LightBlue
            self.form_TQ.btn_refreshTQ.Location = Point(740, 320)
            self.form_TQ.btn_refreshTQ.Size = Size (100, 50)
            self.form_TQ.btn_refreshTQ.Enabled = False
            self.form_TQ.btn_refreshTQ.Click += self.RefreshTQ
            
            self.form_TQ.Controls.Add(self.form_TQ.btn_refreshTQ)
            
            
            #INRIM_logo
            self.form_TQ.logo = PictureBox()
            self.form_TQ.logo.Location = Point(20, 450)
            self.form_TQ.logo.Size = Size (210, 70)
            self.form_TQ.logo.SizeMode = PictureBoxSizeMode.StretchImage
            self.form_TQ.logo.Load("logo_inrim.jpg")
            self.form_TQ.Controls.Add(self.form_TQ.logo)            
            
            self.form_TQ.sb_TQ = StatusBar()
            self.form_TQ.sb_TQ.Text = "Ready"
            self.form_TQ.sb_TQ.Location = Point(20, 20)
            self.form_TQ.Controls.Add(self.form_TQ.sb_TQ)   
        
            self.form_TQ.counter =1
        
            self.form_TQ.Closing += self.FormTQClose
            self.form_TQ.formClosed = False
        
        
            self.form_TQ.Show()
                        
            self.Set_in_freqRF_TQ_Format(self,self)
            self.Set_in_current_TQ_Format(self,self)
            self.Set_out_null_volt_Format(self,self)


        def Set_in_freqRF_TQ_Format(self, sender, args):
            number = '{0:.3f}'.format(float(self.form_TQ.in_freqRF.Text))
            self.form_TQ.in_freqRF.Text = str(number)
                    
        def Set_in_current_TQ_Format(self, sender, args):
            number = '{0:.3f}'.format(float(self.form_TQ.in_current.Text))
            self.form_TQ.in_current.Text = str(number)

        def Set_out_null_volt_Format(self, sender, args):
            number = '{0:.10f}'.format(float(self.form_TQ.out_null_volt.Text))            
            self.form_TQ.out_null_volt.Text = str(number)
            number2 = '{0:.10f}'.format(float(self.form_TQ.out_null_volt_stdev.Text))
            self.form_TQ.out_null_volt_stdev.Text = str(number2)
            
        #change bias current in real time
        def ChangeCurrent(self, sender, args):
            #if self.running == True:
            freqRF = float(self.form_TQ.in_freqRF.Text) # GHz
            current = float(self.form_TQ.in_current.Text) # mA
            
            Vlsb = Math_Functions.Eval_Parameters(freqRF)[0]
            R = 50 # Ohm, output resistance of each channel
            
            if self.form_TQ.checkbox_invert_curr.Checked == True:
                inversion = True
            else:
                inversion = False
                
            self.form_TQ.Vout_array = Math_Functions.Quantum_test(Vlsb, current, n_subs, R, inversion)
            if not sim:
                Devices_Control.SetDCVoltages(self.device, self.form_TQ.Vout_array) #call function in Devices_Control for setting dc voltages to each channel                

                

        #Runs the quantization test calling function from Devices_Control
        def RunTQ(self, sender, args):
            
                if not sim:  
                    setimp_TQ = Devices_Control.SetImpedanceTQ(self.device)  #reset the correct output impedances values for each channel
                    if setimp_TQ=="ERR_IMP":
                        self.sb.Text = "WARNING: Output impedance not correctly set!"
                        return(-1)
                        
                                             
                self.running = True
                self.form_TQ.seriesTQ.Points.RemoveItem(0)
                self.form_TQ.sb_TQ.Text = "RUN"
                self.form_TQ.btn_runTQ.Enabled = False
                self.form_TQ.btn_stopTQ.Enabled = True
                self.form_TQ.btn_refreshTQ.Enabled = True
                                

                while self.running:
                    
                    Application.DoEvents()
                    if self.form_TQ.formClosed:
                        self.running = False
                        break
                    
                    if sim:
                        current = float(self.form_TQ.in_current.Text) # mA
                        Vread = current*uniform(0.9,1.)/1000.
                    else:
                        if self.running:
                            self.ChangeCurrent(self,self)
                            Vread = float(Devices_Control.ReadVolt(self.voltmeter)) #voltage read by the voltmeter

                    self.form_TQ.out_null_volt_list.append(Vread)
                    Vstddev = std(self.form_TQ.out_null_volt_list)

                             
                    '''
                    #stuff for the plot scale
                    if Vread > self.form_TQ.areaTQ.AxisY.Maximum:
                        self.form_TQ.areaTQ.AxisY.Maximum = Vread
            
                    if Vread < self.form_TQ.areaTQ.AxisY.Minimum:
                        self.form_TQ.areaTQ.AxisY.Minimum = Vread
                    
                    
                    if self.form_TQ.counter ==1:
                         self.form_TQ.seriesTQ.Points.RemoveItem(0)
                         self.form_TQ.areaTQ.AxisY.Maximum = Vread+Vread/100.
                         self.form_TQ.areaTQ.AxisY.Minimum = Vread-Vread/100.
                    '''     
                    self.form_TQ.seriesTQ.Points.AddXY(float(self.form_TQ.counter),float(Vread))
                    self.form_TQ.out_null_volt.Text = str(Vread)
                    
                    self.form_TQ.seriesTQ_stdev.Points.AddXY(float(self.form_TQ.counter),float(Vstddev))
                    self.form_TQ.out_null_volt_stdev.Text = str(Vstddev)
                    
                    if sim:
                        time.sleep(0.05) #SIMULATION
    
                    self.form_TQ.counter+=1


        def StopTQ(self, sender, args):
            
            Application.DoEvents()            
            self.running = False
               
            self.form_TQ.sb_TQ.Text = "STOP"
            self.form_TQ.btn_runTQ.Enabled = True
            self.form_TQ.btn_stopTQ.Enabled = False
            self.form_TQ.btn_stopTQ.BackColor = Color.Red
            if not sim:
                zero_volt_array = n_subs*[0.0]
                setvolt = Devices_Control.SetDCVoltages(self.device, zero_volt_array)
                if setvolt == "ERR_SET_VOLT":
                    self.form_TQ.sb.Text = "WARNING: Voltage not correctly set!"
                    return(-1)                   
                    
                
                #Devices_Control.Stop(self.device) #Stop devices
                #self.form_TQ.seriesTQ.Points.RemoveItem(int(self.form_TQ.counter)-int(1))
                
        def RefreshTQ(self, sender, args):
            
            Application.DoEvents()             
            self.form_TQ.seriesTQ.Points.Clear()
            self.form_TQ.seriesTQ_stdev.Points.Clear()             
            self.form_TQ.out_null_volt_list = []
            if not self.running:                
                self.form_TQ.seriesTQ.Points.AddXY(0.,0.)
                self.form_TQ.seriesTQ_stdev.Points.AddXY(0.,0.)        
            self.form_TQ.counter = 1




        def FormTQClose(self, sender, args):
        
            self.StopTQ(self,self)
            self.form_TQ.formClosed = True

    
           