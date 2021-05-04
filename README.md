# PJVS-driving-tool
Python program capable of properly driving a 13-bit Programmable Josephson Voltage Standard (PJVS) through the remote-control of four 4-channel arbitrary waveform generators (Active Technologies 1104) and a nanovoltmeter (Keithley 2182A).
It consists of three main forms:
1) checking IV characteristics of each PJVS subsection;
2) quantization test; 
3) quantum-based stepwise voltage synthesis.

# Notes:
Active-Technologies provides 32-bit DLLs for their AWG-1104 DLL, hence also 32-bit Python version has to be employed.

# Reference publications:

https://ieeexplore.ieee.org/abstract/document/8501187

https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0209246
