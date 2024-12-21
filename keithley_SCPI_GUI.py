
'''
 MIT License

Copyright (c) 2024 Tanay Dey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Additional Terms:
The author of this code retains all rights to the intellectual property contained within. 
Any unauthorized use, modification, or distribution of this code may result in legal action.

Please respect the author's rights and adhere to the following guidelines:

 Disclaimer:
This code is provided "as-is" and without warranty of any kind, express or implied. 
The author assumes no responsibility for any damages or consequences arising from the use of this code.

Modification:

Any modifications made to this code should be documented and attributed to the original author. 
Prior permission for significant changes is recommended.  
Please contact the author at tanay.phys@gmail.com to discuss modifications.

Citation:
If you use this code in your research or presentations, please cite it by referencing this GitLab repository: 
https://gitlab.cern.ch/tdey/keithley_2470_power_supply_gui.git.

By using this code, you agree to abide by these terms.

Author: Dr. Tanay Dey
Present Affiliation: SAHA INSTITUTE OF NUCLEAR PHYSICS (SINP), KOLKATA, INDIA
'''

import pyvisa as visa
import time
import matplotlib.pyplot as plt

from tkinter import *
import tkinter as Tk
from tkinter import ttk

from tkinter import messagebox 	as msg
import os
from tkinter import filedialog
counter=0


import sys
import numpy as np
import numpy.linalg as npl
import matplotlib as matplotlib 
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import copy
import time
import glob as glob

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import sys
import os
import requests
import io
import time
import copy
from datetime import date,datetime
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from io import StringIO
from contextlib import redirect_stdout
import logging
from PIL import Image, ImageTk
from matplotlib.widgets import Slider
import screeninfo
from tkinter.font import Font
import re
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import MultipleLocator

from matplotlib import style
#from ttk import OptionMenu, Style
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, HPacker, VPacker


matplotlib.use("TkAgg")

import math
import serial
import socket
import pickle
import tempfile
import serial.tools.list_ports
import pandas as pd
#from stringcolor import * 

current_threshold=1#0.01#0.000150#1.0e-6
max_voltage=1500
plt_flag=1
#def set_threshold():
xp=[]
yp=[]
ypp=[]
xp_ap=[]
temp_arr=[]
humid_arr=[]
time_arr=[]
rm=None
dummy=None
location=None
instrument=None
search_flag=0
run_time_flag=0
pause_plot=0
figure_canvas=None
#global instrument#,rm,location
plot1=None
plot2=None
plot3=None
animation=None
warn_flag=0
legn_flag=0
start_vol=0
end_vol=0
step_vol=0
time_delay=0
curr_th=0
legend1=None

sim_flag=0
run_flag=0
stop_flag=0
run_index=0
baud_rate = 9600
ard_flag=0
rmp_dwn_flag=0
all_ports = {''}

def set_plot_on_or_off(val=1):
	plt_flag=val	

   
def measure_current():
    global instrument
    #instrument.write("*RST")
    #instrument.write("*CLS")
    #instrument.write(":TRIG:SOURCE CURR")
    instrument.write(":SENS:FUNC 'CURR'")
    #instrument.write(":SENS:CURR:PROT 0.1e-12")
    instrument.write(":SENSE:CURR:UNIT AMP")
    instrument.write(":CURR:RANG:AUTO ON")
    instrument.write("MEAS:CURR?")
    return float(instrument.read().strip())


def measure_voltage():
    global instrument
    instrument.write("*CLS")
    #instrument.write(":SENSE:FUNC 'VOLT'")    
    instrument.write("MEAS:VOLT?")
    return float(instrument.read().strip())
    
def check_output_state():
    global instrument
    output_state = instrument.query(":OUTPUT:STATE?")
    if output_state.strip() == "1":
        #print("Output is ON")
        return 1
    else:
        print("Output is OFF")
        return 0
def set_current_threshold(threshold):
	global instrument
	instrument.write(":SOUR:VOLT:ILIM %f" %threshold)

def clr_n_reset_powersupply(vol_step):
	global instrument
	instrument.write(":OUTP ON")
	instrument.write("*WAI")
	voltage_r1 = measure_voltage()
	print('Init voltage::',voltage_r1)
	while voltage_r1>1e-10:
		voltage_r1=voltage_r1-vol_step
		voltage_r2,current_r2=setVoltage(voltage_r1)
		print('Applied voltage:', voltage_r1)
		print('Voltage:', voltage_r2)
		print('current:', current_r2,"\n\n")
		instrument.write("*WAI")
		voltage_r1=voltage_r2
  
	voltage_r2,current_r2=setVoltage(0.0)
	print('Applied voltage:', 0)
	print('Voltage:', voltage_r2)
	print('current:', current_r2,"\n\n")
 
	instrument.write("*CLS")
	instrument.write("*RST")
	print('Voltage is ramped down to zero')
	#set_current_threshold(current_threshold)
    
def ramp_down_zero(v_step=1.0,delay_t=0.01):
	global instrument,rmp_dwn_flag
	#instrument.write(":OUTP ON")
	instrument.write("*WAI")
	voltage_r1 = measure_voltage()
	curr_r1 = measure_current()
	#if curr_th>=abs(curr_r1):
	print('Threshod crossed Curr:: ',curr_r1*1e9,' VOlTAGE:: ',voltage_r1)
	print("Ramping Down Please Wait")
	rmp_dwn_flag=1
	end_volt=0
 
	if voltage_r1>0 and abs(voltage_r1)>=20:
		end_volt=22
		#ramp_up(22,v_step,delay_t)
	#elif voltage_r1>0 and abs(voltage_r1)<20:
	#	end_volt=0
		#ramp_up(0,v_step,delay_t)
	elif voltage_r1<0 and abs(voltage_r1)>=20:
		end_volt=-22
 		#ramp_up(-22,v_step,delay_t)
	else:
		end_volt=0
		#ramp_up(0,v_step,delay_t)
	diff=abs(end_vol-voltage_r1)
	if(diff<=v_step):
		v_step=v_step/2.0
	ramp_up(end_volt,v_step,delay_t)
	
	
  
	#setVoltage(0.0)
	#instrument.write("*CLS")
	#instrument.write("*RST")
	#print('Voltage is ramped down to zero')
def chk_polarity(voltage,pol_voltage):
	if voltage>pol_voltage:
		return 1
	else:
		return 0
def ramp_up_run(voltage_r1,voltage,vol_step,polar1,sec_t):
	global instrument,rmp_dwn_flag
	if abs(voltage_r1-voltage)>1e-2:
		voltage_r1=voltage_r1+vol_step
		polar2=chk_polarity(voltage_r1,voltage)
		if polar1 !=polar2:
			voltage_r2,current_r2 =setVoltage(voltage)
			current_r2=current_r2*1000000000.0
			if var.get()==1:
				temp,humid=run_arduino()
				p_reading.set('VOLTAGE:: '+str(round(voltage_r2,4))+' V\n'+'CURRENT::'+ str(round(current_r2,4)) +' nA'+"\n"+'Temp:: '+temp+' \u00B0C  Humid:: '+humid+' %')
				labels1.config(text=p_reading.get())
			else:
				p_reading.set('VOLTAGE:: '+str(round(voltage_r2,4))+' V\n'+'CURRENT::'+ str(round(current_r2,4)) +' nA')
				labels1.config(text=p_reading.get())
			if(rmp_dwn_flag==1):
				print('Voltage is Set to zero 1')
				instrument.write(":OUTP OFF")
				rmp_dwn_flag=0

			#print('Voltage is Set to zero 1')
			#instrument.write(":OUTP OFF")
			return
		voltage_r2,current_r2=setVoltage(voltage_r1)
		current_r2=current_r2*1000000000.0
		time.sleep(sec_t)
		if var.get()==1:
				temp,humid=run_arduino()
				p_reading.set('VOLTAGE:: '+str(round(voltage_r2,4))+' V\n'+'CURRENT::'+ str(round(current_r2,2)) +' nA'+"\n"+'Temp:: '+temp+' \u00B0C  Humid:: '+humid+' %')
				labels1.config(text=p_reading.get())
		else:
				p_reading.set('VOLTAGE:: '+str(round(voltage_r2,4))+' V\n'+'CURRENT::'+ str(round(current_r2,2)) +' nA')
				labels1.config(text=p_reading.get())
		instrument.write("*WAI")
		if(abs(voltage_r2-voltage)<=1e-2):
			voltage_r2,current_r2=setVoltage(voltage)
			current_r2=current_r2*1000000000.0
			if var.get()==1:
				temp,humid=run_arduino()
				p_reading.set('VOLTAGE:: '+str(round(voltage_r2,4))+' V\n'+'CURRENT::'+ str(round(current_r2,2)) +' nA'+"\n"+'Temp:: '+temp+' \u00B0C  Humid:: '+humid+' %')
				labels1.config(text=p_reading.get())
			else:
				p_reading.set('VOLTAGE:: '+str(round(voltage_r2,4))+' V\n'+'CURRENT::'+ str(round(current_r2,2)) +' nA')
				labels1.config(text=p_reading.get())
			if(rmp_dwn_flag==1):
				instrument.write(":OUTP OFF")
				print('Voltage is Set to zero 1')
				
				
				rmp_dwn_flag=0
				return
			return
		if(rmp_dwn_flag==1):
			print('Ramping Down\nCurr:: ',current_r2,' VOlTAGE:: ',voltage_r2)   

		window.after(1000,lambda: ramp_up_run(voltage_r1,voltage,vol_step,polar1,sec_t))
	else:
		voltage_r2,current_r2=setVoltage(voltage)	
		current_r2=current_r2*1000000000.0
		if var.get()==1:
				temp,humid=run_arduino()
				p_reading.set('VOLTAGE:: '+str(round(voltage_r2,4))+' V\n'+'CURRENT::'+ str(round(current_r2,4)) +' nA'+"\n"+'Temp:: '+temp+' \u00B0C  Humid:: '+humid+' %')
				labels1.config(text=p_reading.get())
		else:
				p_reading.set('VOLTAGE:: '+str(round(voltage_r2,4))+' V\n'+'CURRENT::'+ str(round(current_r2,4)) +' nA')
				labels1.config(text=p_reading.get())
		if(rmp_dwn_flag==1):
			print('Voltage is Set to zero 2')

			instrument.write(":OUTP OFF")
			rmp_dwn_flag=0
		return


def ramp_up(voltage,vol_step=.50,sec_t=0.01):
	global instrument,rmp_dwn_flag
	instrument.write("*WAI")
	voltage_r1 = measure_voltage()
	current_r1=measure_current()*1000000000.0
	if var.get()==1:
		temp,humid=run_arduino()
		p_reading.set('VOLTAGE:: '+str(round(measure_voltage(),4))+' V\n'+'CURRENT::'+ str(round(current_r1,2)) +' nA'+"\n"+'Temp:: '+temp+' \u00B0C  Humid:: '+humid+' %')
		labels1.config(text=p_reading.get())
	else:
		p_reading.set('VOLTAGE:: '+str(round(measure_voltage(),4))+' V\n'+'CURRENT::'+ str(round(current_r1,2)) +' nA')
		labels1.config(text=p_reading.get())

	indx=0
	polar1=chk_polarity(voltage_r1,voltage)
	if voltage_r1>voltage:
			vol_step=-1.0*vol_step
	if abs(voltage)<0.5 and abs(voltage_r1)<1:
		setVoltage(voltage)
		if(rmp_dwn_flag==1):
			instrument.write(":OUTP OFF")
			rmp_dwn_flag=0

	else:
		ramp_up_run(voltage_r1,voltage,round(vol_step,1),polar1,sec_t)		
    
def set_single_voltage():
	global instrument
	if(is_blank_string(p_address.get())==True or search_flag==0):			
		msg.showwarning('warning','Power supply is not detected \n SEARCH OR SET SOURCE ADDRESS')
		return  0

	step_voltage_num=0
	delay_time_num=1
	if(down_step_voltage.get()=='' or delay_time.get()==''):
		step_voltage_num=5
		delay_time_num=1
	else:
		flag4,step_voltage_num=is_number(step_voltage.get())
		flag5,delay_time_num=is_number(delay_time.get()) 

	ramp_up(float(single_voltage.get()),step_voltage_num,delay_time_num)

def ramp_down_single_voltage():
	global instrument
	if(is_blank_string(p_address.get())==True or search_flag==0):			
		msg.showwarning('warning','Power supply is not detected \n SEARCH OR SET SOURCE ADDRESS')
		return  0

	step_voltage_num=0
	delay_time_num=1
	if(down_step_voltage.get()=='' or delay_time.get()==''):
		step_voltage_num=5
		delay_time_num=1
	else:
		flag4,step_voltage_num=is_number(down_step_voltage.get())
		flag5,delay_time_num=is_number(delay_time.get()) 
	ramp_down_zero(step_voltage_num,delay_time_num)
	

def setVoltage(voltage):
    global instrument
    try:    
        instrument.write(":SOUR:FUNC VOLT")
        instrument.write("*WAI")
        instrument.write(":SOUR:VOLT:RANG:AUTO ON")
        instrument.write(":SOUR:VOLT %f" %voltage)
        instrument.write("*WAI")
        instrument.write(":OUTP ON")
        instrument.write("*WAI")
                        
        voltage_r = measure_voltage()
        current = measure_current()
        return voltage_r,current
    except visa.VisaIOError as error:
        print("Error:", error)
        return -9999,-9999

def set_output_off():
	global instrument
	instrument.write(":OUTP OFF")




##################################################################################################################
#																												 #
#                                        GUI PART													 #
#																												 #
##################################################################################################################


def find_powersupply(location):
	flag=0      
	address_powersupply=''
	for loc in location:
		index = loc.find('USB')
		if(index!=-1):
			flag=1
			address_powersupply=loc
			break
	return flag,address_powersupply
 
def find_powersupply1(location):
	flag=0      
	index = location.find('USB')
	if(index!=-1):
		flag=1
	
		
	return flag,location
 
def search():
	global instrument,location,search_flag
	global figure,figure_canvas,image_label_keithley,ax
	rm = visa.ResourceManager()
	plot_VI_graph(-1,1)
	try:
		location=rm.list_resources() 
		print(location)
		value,address=find_powersupply(location)
		
		if(value==1):
			instrument = rm.open_resource(address)
			print('Power supply Detected at address:: ',address)
			p_address.set(address)
			window.after(0, show_yellow_light)
			search_flag=1

		else:
			msg.showwarning("warning", "Power supply is not detected. \n Turn on it or check USB connection\n or set address manually.")
			p_address.set('') 
			window.after(0, show_red_light)
			print('Power Supply Not Detected:\nPlease verify that the USB cable is plugged in \nor the power switch is turned on\n or set address manually.')
	except pyvisa.Error as e:
		window.after(0, show_red_light)
		p_address.set('') 
		msg.showerror("Error", f"PyVISA error: {e}")		 	

def is_blank_string(s):
    return not s or s.isspace()



def set_address():
	global instrument,rm,search_flag
	global dummy
	rm = visa.ResourceManager()
	dummy='HELLO'
	try:
		if(is_blank_string(p_address.get())==False):
			
			flag,address=find_powersupply1(p_address.get())
			if flag==1:
				instrument = rm.open_resource(address)
				msg.showinfo("Information", "Power supply address set::\n"+p_address.get())
				p_address.set(address)
				window.after(0, show_yellow_light)
				search_flag=1
				return
			else:
				msg.showwarning("warning", "Set a valid address")
				window.after(0, show_red_light)
				p_address.set('')  
				return
			print(p_address.get())
		else:
			msg.showwarning("warning", "First Search or Set Power supply address")	
			p_address.set('') 
			return

	except visa.Error as e:
		window.after(0, show_red_light)
		p_address.set('') 
		msg.showerror("Error", f"Set Valid Address\nPyVISA error: {e}")		 	
	
	except ValueError as ve:
		window.after(0, show_red_light)
		p_address.set('') 
		msg.showerror("Error", f"Set Valid Address\nValueError: {ve}")
	except AttributeError as ae:
		window.after(0, show_red_light)
		p_address.set('') 
		msg.showerror("Error", f"Set Valid Address\nAttributeError: {ae}")

def search_or_set():
	global sim_flag
	plot_VI_graph(0,0)
	sim_flag=0
	if(is_blank_string(p_address.get())==False):
		set_address()
	else:
			
		
		search()
		

def get_screen_size():
    screen_info = screeninfo.get_monitors()[0]  
    width = screen_info.width
    height = screen_info.height
    return width, height
def disable_key_events(event):
  """Disables key events for the Text widget."""
  return "break" 
def previous_widget():
    current_widget = window.focus_get()
    previous_widget = current_widget.tk_traverse(tk.LEFT)
    if previous_widget:
        previous_widget.focus_set()
def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    buttonRun.set_focus()
    return 'break'
       
def on_enter(event):
    event.widget.config(bg='plum')

def on_leave(event):
    event.widget.config(bg='white')

def on_entry_click(event):
    #module_name.set('')
    event.widget.config(bg='plum')	
    if screen.get() == "e.g:: Kickoff Module":
        screen.delete(0, Tk.END)

def on_focus_out(event):
    event.widget.config(bg='white')
    if not screen.get() or module_name.get()=='':
        screen.insert(0, "e.g:: Kickoff Module")
        module_name.set(screen.get())
    
def but_foc():
     button1.focus_set()
     
def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
def get_temp_dir():
  """Gets the temporary directory used by PyInstaller."""
  temp_dir = tempfile.gettempdir()
  # Adjust the path based on your PyInstaller configuration
  return os.path.join(temp_dir, '_MEI<some_random_string>')


def light_images(s1):
	if getattr(sys, 'frozen', False):
    # The application is frozen (i.e., running as a bundled executable)
    		base_path = sys._MEIPASS
	else:
    # The application is not frozen
    		base_path = os.path.abspath(".")

	image_path = Image.os.path.join(base_path,'light_files',str(s1))
	image = Image.open(image_path)
	# Replace "image.png" with your image path
	resized_image1 = image.resize((200, 85))
	photo1 = ImageTk.PhotoImage(resized_image1)
	return photo1
	
def exits(event=None):
	#exit()
	window.quit()
	#exit()
	
def Toggle_light(event=None):
	#global light_image
	global image_label2,photo2,photo3
	#light_image.set('y1.png')
	#s1=light_image.get()
	#light_images(s1)
	#photo2=image_place()
	image_label2.config(image=photo2)
	#if image_label2['image'] == photo2:
	#print('running')
	#image_label2.grid(row=10, column=0, sticky="n",padx=0,pady=0)
	
	#s1=light_image.get()
	#image_place(s1)

#def main():

def HVTEST():
	user_response = msg.askquestion("HV TEST", "HV test selected \n Do you want to continue?").lower()
	if user_response in ('no', 'N','NO','N','No','nO'):
		radio_button1.deselect()
		start_voltage.set('')
		end_voltage.set('')
		current_th.set('10000')
		step_voltage.set('5')
		down_step_voltage.set('10')
		delay_time.set('1')

		return
	else:	
		
		print('HV TEST SELECTED')
		start_voltage.set('0')
		end_voltage.set('1000')
		current_th.set('1')
		step_voltage.set('10')
		down_step_voltage.set('10')
		delay_time.set('1')
		
def IVTEST():
	user_response = msg.askquestion("IV TEST", "IV test selected \n Do you want to continue?").lower()
	if user_response in ('no', 'N','NO','N','No','nO'):
		radio_button2.deselect()
		start_voltage.set('')
		end_voltage.set('')
		current_th.set('10000')
		step_voltage.set('5')
		down_step_voltage.set('10')
		delay_time.set('1')

		return
	else:	
		
		print('IV TEST SELECTED')
		
		start_voltage.set('0')
		end_voltage.set('-800')
		current_th.set('1000')
		step_voltage.set('5')
		down_step_voltage.set('10')
		delay_time.set('1')

def radioselect1(event=None):
     radio_button1.select()
def radioselect2(event=None):
     radio_button2.select()     
     
def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
	
def on_mousewheel(event):
    if event.delta > 0:
        canvas.yview_scroll(-1, "units")
    elif event.delta < 0:
        canvas.yview_scroll(1, "units")

    if event.delta > 0:
        canvas.xview_scroll(-1, "units")
    elif event.delta < 0:
        canvas.xview_scroll(1, "units")

def is_number(num):
    try:
        
        return True,float(num)
    except ValueError:
        return False
ii=0        
def idle_state():
	global instrument,search_flag,rm,ii
	global image_label2,photo1,photo2,photo3

	image_label2.config(image=photo2)
	print("idle state",ii)
	ii=ii+1
def run_state():
	global instrument,search_flag,rm,ii
	global image_label2,photo1,photo2,photo3

	image_label2.config(image=photo3)
	image_label2.grid(row=0, column=1, sticky="n",padx=0,pady=0)
	print("run state",ii)
	ii=ii+1
def stop_state():
	global instrument,search_flag,rm,ii
	global image_label2,photo1,photo2,photo3

	image_label2.config(image=photo2)
	print("idle state",ii)
	ii=ii+1

def RUN_IV_HV():
	global instrument,search_flag,rm,run_time_flag
	global image_label2,photo1,photo2,photo3
	run_time_flag=0
	flag1,current_th_num=0,0
	flag2,start_voltage_num=0,0
	flag3,end_voltage_num=0,0
	flag4,step_voltage_num=0,0
	flag5,delay_time_num=0,0
	print(p_address.get(), 'search flag',search_flag)
	if(is_blank_string(p_address.get())==True or search_flag==0):			
		msg.showwarning('warning','Power supply is not detected \n SEARCH OR SET SOURCE ADDRESS')
		return  0
	if(user_answer.get()==''):
		msg.showwarning('warning','Please choose any option from \nTEST TYPE HV/IV')
		return  0	
	
	
	try:
		flag1,current_th_num=is_number(current_th.get())
		flag2,start_voltage_num=is_number(start_voltage.get())
		flag3,end_voltage_num=is_number(end_voltage.get())
		flag4,step_voltage_num=is_number(step_voltage.get())
		flag5,delay_time_num=is_number(delay_time.get())								
		if (user_answer.get()=='HV'):
			if(not flag1 or not flag2 or not flag3 or not flag4 or not flag5):
				msg.showwarning('warning','Please provide numbers to the voltage and current parameters')
				return 0
			if(start_voltage_num<0): 
				msg.showwarning('warning','For HV TEST:: start voltage should be positive or zero')
				return  0
			elif(end_voltage_num<0):
				msg.showwarning('warning','For HV TEST:: end voltage should be positive')
				return  0
			elif(step_voltage_num<0):
				msg.showwarning('warning','For HV TEST:: voltage step should be non-negative')
				return  0	
			elif(current_th_num<0):
				msg.showwarning('warning','For HV TEST:: current threshold should be non-negative')
				return  0
			elif(delay_time_num<0):
				msg.showwarning('warning','For HV TEST:: delay time should be non-negative')
				return  0
			elif(abs(start_voltage_num)>max_voltage):
				msg.showwarning('warning','For HV TEST:: start voltage goes beyond max-limit 1500 V')
				return  0	
			elif(abs(end_voltage_num)>max_voltage):
				msg.showwarning('warning','For HV TEST:: end voltage goes beyond max-limit 1500 V')
				return  0
			elif(abs(step_voltage_num)>max_voltage):
				msg.showwarning('warning','For IV TEST:: Magnitude of voltage step exceeds max-limit 1500 V')
				return  0	
					
			elif(abs(end_voltage_num)<abs(start_voltage_num)):
				msg.showwarning('warning','For HV TEST:: Magnitude of start voltage should be less than end voltage')
				return  0
			elif(abs(end_voltage_num)<abs(step_voltage_num)):
				msg.showwarning('warning','For HV TEST:: Magnitude of end voltage should be greater than voltage step. Is is recomended that voltage step should be within 50 V')
				return  0	
			elif(abs(step_voltage_num)>100):
				msg.showwarning('warning','For HV TEST:: It is recomended that voltage step should be within 100 V. Please reduce step size or do at your own risk')
				user_response = msg.askquestion("HV TEST", "Do you want to change the voltage step size?").lower()
				if user_response in ('no', 'N','NO','N','No','nO'):
					run_time_flag=1
					print('HV TEST IS RUNNING')
					return 1
				else:
						
					return  0	
				
			else:
				run_time_flag=1
					
				print('HV TEST IS RUNNING')
				return 1	


							
				
		elif (user_answer.get()=='IV'):
			if(not flag1 or not flag2 or not flag3 or not flag4 or not flag5):
				msg.showwarning('warning','Please provide numbers to the voltage and current parameters')
				return  0
			if(start_voltage_num>0): 
				msg.showwarning('warning','For IV start voltage should be negative or zero')
				return  0
			elif(end_voltage_num>0):
				msg.showwarning('warning','For IV end voltage should be negative')
				return  0
			elif(step_voltage_num<0):
				msg.showwarning('warning','For IV voltage step should be non-negative')
				return	0
			elif(current_th_num<0):
				msg.showwarning('warning','For IV current threshold should be non-negative')
				return  0
			elif(delay_time_num<0):
				msg.showwarning('warning','For IV TEST:: delay time should be non-negative')
				return  0
			elif(abs(start_voltage_num)>max_voltage):
				msg.showwarning('warning','For IV TEST:: Magnitude of start voltage exceeds max-limit 1500 V')
				return	0
			elif(abs(end_voltage_num)>max_voltage):
				msg.showwarning('warning','For IV TEST:: Magnitude of end voltage exceeds max-limit 1500 V')
				return	0
			elif(abs(step_voltage_num)>max_voltage):
				msg.showwarning('warning','For IV TEST:: Magnitude of voltage step exceeds max-limit 1500 V')
				return	0

			elif(abs(end_voltage_num)<abs(start_voltage_num)):
				msg.showwarning('warning','For IV TEST:: Magnitude of start voltage should be less than end voltage')
				return 0
			elif(abs(end_voltage_num)<abs(step_voltage_num)):
				msg.showwarning('warning','For IV TEST:: Magnitude of end voltage should be greater than voltage step. Is is recomended that voltage step should be within 50 V')
				return	0
			elif(abs(step_voltage_num)>50):
				msg.showwarning('warning','For IV TEST:: It is recomended that voltage step should be within 50 V. Please reduce step size or do at your own risk')
				user_response = msg.askquestion("IV TEST", "Do you want to change the voltage step size?").lower()
				if user_response in ('no', 'N','NO','N','No','nO'):
					run_time_flag=1
					print('IV TEST IS RUNNING')
					return 1
				else:
						
					return	0
					
			else:
				run_time_flag=1
				print('IV TEST IS RUNNING')
				return 1
						
		if(run_time_flag==1):
			return 1
			
	except visa.Error as e:
		window.after(0, show_red_light)
		p_address.set('') 
		msg.showerror("Error", f"Set Valid Address\nPyVISA error: {e}")		 	
	
						
			
	except ValueError as ve:
		msg.showerror("Error", f"ValueError: {ve}")
	except TypeError as te:
		if(not flag1 or not flag2 or not flag3 or not flag4 or not flag5):
			msg.showwarning('warning','Please provide valid numbers to\n the voltage, current and time parameters')
		msg.showerror("Error", f"TypeError: {te}")


def auto_run_process():
	global instrument,search_flag,rm,run_time_flag,animation
	global image_label2,photo1,photo2,photo3
	global plot1,xp,yp,run_index,line,ypp,xp_ap,temp_arr,humid_arr,time_arr
	global figure,figure_canvas,image_label_keithley,ax
	global start_vol,end_vol,step_vol,down_step_vol,time_delay,curr_th,warn_flag,legn_flag,legend1,pause_plot,run_flag,ax2,run_init_flg,polarinit
	print('\n\n\nvar Is::',var.get())
	temp=0.0
	humid=0.0
	temp1=''
	humid1=''
 
	if var.get()==1:
		temp1,humid1=run_arduino()
		print("Temp:: ",temp1,"\n","Humid:: ",humid1)
		if temp1=='-999':
			print("Temp:: ",temp1,"\n","Humid:: ",humid1)
			stop_run()
		elif temp1=='-998':
			print("Temp:: ",temp,"\n","Humid:: ",humid)
			while temp1=='-998':
				temp1,humid1=run_arduino()
				time.sleep(0.3)
		temp=float(temp1)
		humid=float(humid1)
	try:
		
		if abs(end_vol-start_vol)>1e-3:
			polarrun=chk_polarity(end_vol,start_vol)
			if polarinit !=polarrun:
				print('polarity not the same')
				start_vol=end_vol
				
			if abs(start_vol)>1:
				ramp_up(start_vol,step_vol,time_delay)
			else:	
				setVoltage(start_vol)
			time.sleep(time_delay)
			voltage_tmp = measure_voltage()
			current_tmp = measure_current()
			current_tmp_store=current_tmp*1000000000.0
			current_tmp_1=0
			if current_tmp<0:
				current_tmp_1=-current_tmp
			else:
				current_tmp_1=current_tmp
   
			diff_I=abs(curr_th-current_tmp_1)*1000000000.0
   
			diff_V=abs(start_vol-voltage_tmp)
			if (diff_V>=step_vol or diff_I<=20)  and warn_flag==0:
			#if ( diff_I<=20)  and warn_flag==0:
				current_tmp1=current_tmp*1e9
				warning_message = 'WARNING: The current limit has been reached \n The voltage ramp-up is stopped \n Value of last measured current is '+str(round(current_tmp1,1)) +' nA'
				print(warning_message)
				xl=[]
				yl=[]
				if len(xp) == 0 or len(yp)==0:
						xp.append(0)
						xp_ap.append(0)
						yp.append(0)
						temp_arr.append(float(temp))	
						humid_arr.append(float(humid))  
						time_arr.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))  
						plot1.set_data(xp, yp)
						plot2.set_data(xp_ap, yp)
				if legn_flag==0:
					if var.get()==1:
						legend1=ax.legend(handles=[plot1,plot2,plot5,plot6])
					else:
						legend1=ax.legend(handles=[plot1,plot2])	
					legend1.get_frame().set_facecolor('lightgreen')
					ax.add_artist(legend1)
					legn_flag=1

				xl.append(xp[0])
				yl.append(yp[0])
				plot3.set_label(warning_message)
				plot3.set_data(xl, yl)#=ax.scatter(xp[0], yp[0],marker='',label=warning_message)#,color='red', label="Set voltage")
				if var.get()==1:
					all_handles = [plot1,plot2,plot5,plot6,plot3]
				else:
					all_handles = [plot1,plot2,plot3]	
				if(legend1):
					legend1.remove()
				legend1 = ax.legend(handles=all_handles)
				legend1.get_frame().set_facecolor('lightgreen')
				legend1.get_texts()[4].set_color('red')
							
				warn_flag=1

				xp.append(voltage_tmp)
				xp_ap.append(start_vol)
				yp.append(current_tmp_store)
				temp_arr.append(float(temp))	
				humid_arr.append(float(humid))	
				time_arr.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))      
				plot1.set_data(xp, yp)
				plot2.set_data(xp_ap, yp)
				ax.relim()
				ax.autoscale_view()
				ax2.relim()
				ax2.autoscale_view()
			
				figure_canvas.draw()
				ramp_down_zero(down_step_vol,time_delay)
				save_results()
				window.after(0, show_yellow_light)
				return
			if(abs(voltage_tmp-end_vol)<1e-3 or abs(start_vol-end_vol)<1e-3):

				run_flag=0
				ramp_down_zero(down_step_vol,time_delay)

				save_results()
				window.after(0, show_yellow_light)
				return
				
			xp.append(voltage_tmp)
			xp_ap.append(start_vol)
			yp.append(current_tmp*1e9)	
			temp_arr.append(float(temp))
			humid_arr.append(float(humid))  
			time_arr.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))      
			plot1.set_data(xp, yp)
			plot2.set_data(xp_ap, yp)
			plot5.set_data(xp,temp_arr)
			plot6.set_data(xp,humid_arr)

			ax.relim()
			ax.autoscale_view()
			ax2.relim()
			ax2.autoscale_view()
			
			figure_canvas.draw()
			if legn_flag==0:
				if var.get()==1:
					legend1=ax.legend(handles=[plot1,plot2,plot5,plot6])
				else:
					legend1=ax.legend(handles=[plot1,plot2])	
				legend1.get_frame().set_facecolor('lightgreen')
				ax.add_artist(legend1)
				legn_flag=1
			
			if check_output_state()==1:
					if  pause_plot==0 and stop_flag==0:

						window.after(1000, auto_run_process)
					elif pause_plot==1 and stop_flag!=0:
						window.after(0, show_yellow_light)
						return
					elif stop_flag==1:
						ramp_down_zero(down_step_vol,time_delay)
						
						save_results()
						window.after(0, show_yellow_light)
						return
					else:
						window.after(0, show_yellow_light)
						return

			if True:# run_init_flg==0:	
				print("Run init is in 1st",run_init_flg)
				if start_vol<=end_vol:
					start_vol=start_vol+step_vol
				else:
					start_vol=start_vol-step_vol
				run_init_flg=1
		
			
		elif legn_flag==1 and warn_flag==0:
			print('lengn if cond',start_vol)
			voltage_tmp,current_tmp=setVoltage(start_vol)	
			xp.append(voltage_tmp)
			xp_ap.append(start_vol)
			yp.append(current_tmp*1e9)	  
			temp_arr.append(float(temp))	
			humid_arr.append(float(humid))    
			time_arr.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))  
			plot1.set_data(xp, yp)#=ax.scatter(xp, yp,marker='o',color='blue', label="Measured voltage")  # Update data for plotting
			plot2.set_data(xp_ap, yp)#ax.scatter(xp_ap, yp,marker='*',color='red', label="Set voltage")
			ax.relim()
			ax.autoscale_view()

			figure_canvas.draw()
			ramp_down_zero(down_step_vol,time_delay)
			run_flag=0
			save_results()
			window.after(0, show_yellow_light)
			return
			
			
		
		else:


			ramp_down_zero(down_step_vol,time_delay)
			save_results()
			window.after(1000, show_yellow_light)
			return
			
	except ValueError as ve:
		msg.showerror("Error", f"ValueError: {ve}")
	except TypeError as te:
		msg.showerror("Error", f"TypeError: {te}")
 		
			
def start_process():
	global image_label2,photo1,photo2,photo3,animation,xp,yp,ypp,xp_ap
	global figure,figure_canvas,image_label_keithley,ax,run_index,line,sim_flag,temp_arr,time_arr,humid_arr
	global start_vol,end_vol,step_vol,down_step_vol,time_delay,curr_th,warn_flag,legn_flag,pause_plot,run_flag,ax2,stop_flag,run_init_flg,polarinit

	sim_flag=0
	run_flag=RUN_IV_HV()
	if(not run_flag):
		return
	run_index=0
	warn_flag=0
	legn_flag=0
	run_flag=1
	pause_plot=0
	stop_flag=0
	run_init_flg=0

	xp=[]
	yp=[]
	ypp=[]
	xp_ap=[]
	temp_arr=[]
	humid_arr=[]
	time_arr=[]

	flag1,current_th_num=is_number(current_th.get())
	flag2,start_voltage_num=is_number(start_voltage.get())
	flag3,end_voltage_num=is_number(end_voltage.get())
	flag4,step_voltage_num=is_number(step_voltage.get())
	flag6,down_step_vol_num=is_number(down_step_voltage.get())
	flag5,delay_time_num=is_number(delay_time.get())



	start_vol=start_voltage_num
	end_vol=end_voltage_num
	step_vol=step_voltage_num	
	down_step_vol=down_step_vol_num
	time_delay=delay_time_num
	
	plot_VI_graph(-1,1)
	if (user_answer.get()=='HV'): 
		plot1.set_linestyle('--')
		plot2.set_linestyle('--')
		ax.set_ylim(-current_th_num*1e3-100, current_th_num*1e3+100)
		ax.set_xlim(start_vol, end_vol+step_vol)
	if (user_answer.get()=='IV'): 
		plot1.set_linestyle('--')
		plot2.set_linestyle('--')
	if(step_vol>40):
		x_locator=MultipleLocator(step_vol)
		ax.xaxis.set_major_locator(x_locator)
	if var.get()==1:
		ax2.set_ylim(0, 150)
		
	polarinit=chk_polarity(end_vol,start_vol)
	current_th_num=current_th_num*0.000001
	curr_th=current_th_num
	set_current_threshold(current_th_num)

	show_green_light()
	auto_run_process()	

def reverse_bias_current(voltage, saturation_current, recombination_current):
  Vt = 0.0258  # Thermal voltage (in volts)
  q = 1.602e-19  # Electron charge (in coulombs)
  #At 300K, kT/q = 25.85 mV, the "thermal voltage".
  eta=2 #for silicon
  # Exponential model for saturation current
  saturation_term = saturation_current * (math.exp(voltage / (eta*Vt)) - 1)

  # Constant term for recombination current
  recombination_term = recombination_current

  return saturation_term + recombination_term
	
def simulation_run():
	global instrument,search_flag,rm,run_time_flag,animation
	global image_label2,photo1,photo2,photo3,temp_arr,time_arr,humid_arr
	global plot1,xp,yp,run_index,line,ypp,xp_ap,warn_flag,legend1
	global figure,figure_canvas,image_label_keithley,ax,plot4,ax2,pause_plot,sim_flag,stop_flag
	degree_symbol = chr(0x00B0)
	plot1.set_color('red')
	plot4.set_color('blue') 
	plot1.set_label('I-V in Left Scale')
	plot4.set_label('I-V in Right Scale')
	module_name.set(f"IV Characteristic of a silicon diode at room temperature 25{degree_symbol}C")
	sim_flag=1
	plot_VI_graph(-1,1)
	pause_plot=0
	warn_flag=0
	stop_flag=0
	ax.set_ylim(-0.000005, 0.000005)  # Adjust limits based on your data
	ax2.set_ylim([-0.001, 0.001])  # Adjust limits based on your data
	ax2.set_xlim(-0.5,0.6)
	ax.set_xlim(-0.5,0.6)
	xp=[]
	yp=[]
	ypp=[]
	xp_ap=[]
	temp_arr=[]
	humid_arr=[]
	time_arr=[]
	run_index=-.5
	simulation()

	
def simulation():
	global instrument,search_flag,rm,run_time_flag,animation
	global image_label2,photo1,photo2,photo3,temp_arr,time_arr,humid_arr
	global plot1,xp,yp,run_index,line,ypp,xp_ap,warn_flag,legend1
	global figure,figure_canvas,image_label_keithley,ax,plot4,ax2,pause_plot,sim_flag,var
	window.after(0, show_green_light)
	print('var Is::',var.get())
	temp='25'
	humid='30'
	if var.get()==1:
		temp,humid=run_arduino()
		if temp=='-999':
			print("Temp:: ",temp,"\n","Humid:: ",humid)
			stop_run()
		elif temp=='-998':
			print("Temp:: ",temp,"\n","Humid:: ",humid)
			while temp=='-998':
				temp,humid=run_arduino()
				time.sleep(0.3)
			#window.after(1000, simulation)	
		print("Temp:: ",temp,"\n","Humid:: ",humid)
	
	i=0
	#while i<20:
	saturation_current = 1e-12
	recombination_current = 1e-15	
	#xr=np.random.rand()
	#yr=run_index*(-1+np.random.rand()*2)
	voltage=run_index
	if(run_index<0): 
		
		xp.append(voltage)
		temp_arr.append(float(temp))	
		humid_arr.append(float(humid))   # Create x-values based on data list length
		time_arr.append(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))  
		cur=reverse_bias_current(voltage,saturation_current,recombination_current)*1e6
		yp.append(cur)
		#yp.append(-run_index*run_index+yr) # Assign actual data values to y
		#ypp.append(-run_index*run_index)
		plot1.set_data(xp, yp)
	else:
		xp_ap.append(voltage) # Create x-values based on data list length
		
		cur=reverse_bias_current(voltage,saturation_current,recombination_current)*1e6
		ypp.append(cur)
		
		plot4.set_data(xp_ap,ypp)	
	if var.get()==1:
			p_reading.set('VOLTAGE:: '+str(round(voltage,4))+' V\n'+'CURRENT::'+ str(round(cur,8)) +' μA'+"\n"+'Temp:: '+temp+' \u00B0C  Humid:: '+humid+' %')
			labels1.config(text=p_reading.get())
	else:
		p_reading.set('VOLTAGE:: '+str(round(voltage,4))+' V\n'+'CURRENT::'+ str(round(cur,8)) +' μA')
		labels1.config(text=p_reading.get())

	if cur>=0.001:
				warning_message = 'WARNING: The current limit has been reached \n Value of last measured current is '+str(round(cur,4)) +' μA'
				print(warning_message)
				xl=[]
				yl=[]
				xl.append(xp[0])
				yl.append(yp[0])
				
				plot3.set_label(warning_message)
				plot3.set_data(xl, yl) 	

				warn_flag=1
				all_handles = [plot1,plot4,plot3]

				legend1 = ax2.legend(handles=all_handles)
				legend1.get_frame().set_facecolor('lightgreen')
				legend1.get_texts()[0].set_color('red')
				legend1.get_texts()[1].set_color('blue')

	ax.relim()
	ax.autoscale_view()
	ax2.relim()
	ax2.autoscale_view()
	
	figure_canvas.draw()
	time.sleep(0.01)
	i=i+1
#plt.pause(0.01)
	vv_stp=0
	if(run_index<0):
		vv_stp=.01
	else:
		vv_stp=0.01	
	run_index=run_index+vv_stp
	if run_index<0.6 and warn_flag==0:
		if  pause_plot==0 and stop_flag==0:
			window.after(100, simulation)
		else:
			window.after(0, show_yellow_light)	
			
	else:
		sim_flag=0
		window.after(0, show_red_light)
		save_results()	 

def pause_plots():
	global pause_plot,sim_flag,run_flag,stop_flag
	if(stop_flag==0):
		
		if pause_plot==0:
			pause_plot=1
			pause.config(text='RESUME')
			
		else:
			pause_plot=0
			pause.config(text='PAUSE')
			if sim_flag==1:
				simulation()
			elif run_flag==1:
				auto_run_process()
	else:
		msg.showwarning("warning",'Run is stopped.Can\'t resume. Please start again.')					
def stop_run():
	global pause_flag,stop_flag,run_flag
	pause_plot=1
	stop_flag=1
	sim_flag=0
	pause.config(text='PAUSE')
	time.sleep(1)
	if run_flag==1:
		flag4,step_volt=is_number(step_voltage.get())
		flag5,delay_t=is_number(delay_time.get()) 
		instrument.write("*WAI")

		ramp_down_zero(step_volt,delay_t)
		run_flag=0		

def get_sub(x): 
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    sub_s = "ₐ₈CDₑբGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥwₓᵧZₐ♭꜀ᑯₑբ₉ₕᵢⱼₖₗₘₙₒₚ૧ᵣₛₜᵤᵥwₓᵧ₂₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎"
    res = x.maketrans(''.join(normal), ''.join(sub_s)) 
    return x.translate(res) 	

def get_super(x): 
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    res = x.maketrans(''.join(normal), ''.join(super_s)) 
    return x.translate(res) 
def multicolor_ylabel(axs,list_of_strings,list_of_colors,axis='y',anchorpad=0,xx=0.0,yy=0.0,**kw):
    # x-axis label
    if axis=='x' or axis=='both':
        boxes = [TextArea(text, textprops=dict(color=color, ha='left',va='bottom',**kw)) 
                    for text,color in zip(list_of_strings,list_of_colors) ]
        xbox = HPacker(children=boxes,align="center",pad=0, sep=5)
        anchored_xbox = AnchoredOffsetbox(loc=3, child=xbox, pad=anchorpad,frameon=False,bbox_to_anchor=(0.2, -0.09),
                                          bbox_transform=axs.transAxes, borderpad=0.)
        axs.add_artist(anchored_xbox)

    # y-axis label
    if axis=='y' or axis=='both':
        boxes = [TextArea(text, textprops=dict(color=color, ha='left',va='bottom',rotation=90,**kw)) 
                     for text,color in zip(list_of_strings[::-1],list_of_colors) ]
        ybox = VPacker(children=boxes,align="center", pad=0, sep=5)
        anchored_ybox = AnchoredOffsetbox(loc=3, child=ybox, pad=anchorpad, frameon=False, bbox_to_anchor=(xx,yy), 
                                          bbox_transform=axs.transAxes, borderpad=0.)
        axs.add_artist(anchored_ybox)
	
def plot_VI_graph(voltage_start,voltage_end):
	global figure,figure_canvas,image_label_keithley,ax,ax2
	image_label_keithley.pack_forget()
	plt.subplots_adjust(left=0.1,right=0.87)
	if(sim_flag==0):
		if var.get()==1:
			ax2.set_visible(True)
			color_map = {'TEMP': 'red', 'Humidity': 'green', 'C': 'blue'}
			label ='TEMP in {}C'.format(get_super('o'))
			multicolor_ylabel(ax2,(label,'AND','Humidity in %'),('m','k','b'),axis='y',size=15,xx=1.05, yy=0.2,weight='bold')
			#ax2.set_ylabel(label)#'TEMP in {}C'.format(get_super('o'))+' AND Humidity in %',color='blue')
		else:
			ax2.set_visible(False)	
		multicolor_ylabel(ax,('Current', 'in nA'),('r','r'),axis='y',size=15,xx=-0.1, yy=0.4,weight='bold')	
	else:
		#ax2.set_visible(True)	
		multicolor_ylabel(ax,('Current', 'in μA'),('r','r'),axis='y',size=15,xx=-0.1, yy=0.4,weight='bold')
		ax2.set_ylabel('Current in μA',color='b')
	
	
 	#ax.set_ylabel('Current in nA',color='red')
	
	ax.set_xlabel('Voltage in V',color='green')
	ax.set_title(module_name.get())
	ax.tick_params(colors='red', axis='y')
	ax.tick_params(colors='green', axis='x')
	ax2.set_title(module_name.get())
	ax2.tick_params(colors='blue', axis='y')
	ax.grid(True, which='both', linestyle='--', linewidth=0.5,alpha=0.5, color='gray')
	ax2.grid(True, which='both', linestyle='--', linewidth=0.5,alpha=0.5, color='gray')
	ax2.set_ylim(auto=True)
	ax.set_ylim(auto=True)
	ax2.set_xlim(auto=True)
	ax.set_xlim(auto=True)
	ax2.legend().remove()
	ax.legend().remove()
	ax2.legend_=None
	ax2.legend_=None
	
	if figure_canvas:
		figure_canvas.get_tk_widget().destroy()
		ax.set_xlabel('Voltage in V')
		ax.set_title(module_name.get())
		ax2.set_title(module_name.get())
		ax2.legend().remove()	
		ax.legend().remove()

		ax2.legend_=None
		ax.legend_=None
		

	plot1.set_data([],[])
	plot3.set_data([],[])
	plot4.set_data([],[])	
	
	figure_canvas = FigureCanvasTkAgg(figure, master=canvas_frame)
	figure_canvas.get_tk_widget().pack(anchor="center",fill=Tk.BOTH, expand=True,)

	figure_canvas.draw()

def search_all_words(my_string, words):
  for word in words:
    if word not in my_string:
      return False
  return True


def init_arduino():
	global all_ports ,var,arduino_port_list,ser,ard_flag
	ports = serial.tools.list_ports.comports()
	all_ports = []
	words_to_find = ["USB", "VID", "PID","SER","LOCATION"]
	description=["Arduino"]

	for port, desc, hwid in ports:
			if search_all_words(hwid, words_to_find) or search_all_words(desc, description): 
				print(port,"\t,",desc,"\t,",hwid)
				all_ports.append(port)
				
	if len(all_ports)<1:		
		msg.showwarning("warning", "Arduino is not found")
		var.set(0)
		stop_run()
	elif var.get()==1:
		arduino_ports.set(all_ports[0])
		if ard_flag==0:
			ser = serial.Serial(arduino_ports.get(), baud_rate)
			ard_flag=1


def arduino_port_on_select(event):
    global label8,arduino_port_list,ser	
    arduino_ports.set(arduino_port_list.get())
    print("Selected:", arduino_ports.get())

def check_button_clicked(var):
	global label8,arduino_port_list,all_ports
	all_ports=[]
	init_arduino()
	selected = var.get()
	if selected:
		label8=Label(button_frame,fg='red',width=int(button_frame_width),text='SELECT ARDUINO PORT',font=("arial",11,"bold"))
		label8.grid(row=14, column=0, sticky="n",padx=0,pady=0)

		arduino_port_list=ttk.Combobox(button_frame, values=all_ports)
		arduino_port_list.set(all_ports[0])
		arduino_port_list.grid(row=15, column=0, sticky="n",padx=0,pady=5)

		arduino_port_list.bind("<<ComboboxSelected>>", arduino_port_on_select)
		
		print(arduino_ports.get())
	else:
			
		label8.destroy()
		arduino_port_list.destroy()
		arduino_ports.set('')
	        
def run_arduino():
	global ser
	try:
			ser.write(b"all\n")
			time.sleep(1)  
			l1 = ser.readline().decode('utf-8').strip()
			print("run func::",l1)
			temp='-998'
			humid='-998'
			numbers = re.findall(r'\d+\.\d+', str(l1))
			if len(numbers) >= 2:
				temp,humid=numbers[0],numbers[1]    	
			return str(temp),str(humid)				
	except NameError as ne:
		msg.showerror("Error", f"Please provide a valid arduino port: {ne}")
		return	-999,-999
	
def write_arrays_pickle(filename, arr1, arr2, arr3, arr4): 
  data = (arr1, arr2, arr3, arr4) 
  with open(filename, 'wb') as f:
    pickle.dump(data, f)
	
def save_results():
	global instrument,search_flag,rm,run_time_flag,animation
	global image_label2,photo1,photo2,photo3
	global plot1,xp,yp,run_index,line,ypp,xp_ap,time_arr,temp_arr,humid_arr
	global figure,figure_canvas,image_label_keithley,ax,ax2
	
	user_response = msg.askquestion("Save results", "Do You Want to save results?").lower()
	if user_response in ('no', 'N','NO','N','No','nO'):
		return
	
	outfile=module_name.get()
	directory=''
	outfile=re.sub(r'\s+','', outfile)
	outfile = "".join(outfile.split())

	outfile=outfile.replace(":", "")


	current_datetimes.set( datetime.now().strftime("%d-%m-%Y-%H-%M"))
	directory='./Results/'+str(current_datetimes.get())+'_'+outfile
	
	if os.path.exists(directory)==True:
		user_response = msg.askquestion("Path Clashes", "Same Module \nDo You Want to Continue?").lower()
		if user_response in ('yes', 'y','YES','Y'):
				while os.path.exists(directory)==True:
					directory=directory+'_clone'
					os.makedirs(directory)
				print("File will be saved in clone folder")
		else:
    			return 
	else:
    		os.makedirs(directory) 		
	outfile=directory+'/'+str(current_datetimes.get())+'_'+outfile+'_Result'				
	log_file=outfile+'_Log.csv'
	data_plot=outfile+'.png'
	alldata = pd.DataFrame({"VOLTS": xp, "CURRNT_NAMP": yp, "TEMP_DEGC": temp_arr, "RH_PRCNT": humid_arr,"TIME":time_arr})

	alldata.to_csv(log_file, index=False) 
	plt.savefig(data_plot)

	
	
		
def update_gp(xp,yp):
	global plot1
	global figure,figure_canvas,image_label_keithley,ax
	plot1=ax.scatter(xp, yp,marker='o',color='blue', label="Measured voltage")
		
def plot(xp,yp):
	global plot1,animation,line
	global figure,figure_canvas,image_label_keithley,ax
	line.set_data(xp, yp)
	canvas_frame.grid_rowconfigure(0, weight=1)
	canvas_frame.grid_rowconfigure(1, weight=1)
 
	canvas_frame.grid_columnconfigure(0, weight=1)
	canvas_frame.grid_columnconfigure(1, weight=1)
	
def show_yellow_light():
        # Change image to yellow
	global instrument,search_flag,rm,run_time_flag
	global image_label2,photo1,photo2,photo3
        
	image_label2.config(image=photo2)
	
def show_red_light():
        # Change image to yellow
	global instrument,search_flag,rm,run_time_flag
	global image_label2,photo1,photo2,photo3
        
	image_label2.config(image=photo1)

def show_green_light():
        # Change image to yellow
	global instrument,search_flag,rm,run_time_flag
	global image_label2,photo1,photo2,photo3
        
	image_label2.config(image=photo3)
 	

    


window=Tk.Tk()

photo1=light_images('r1.png')
photo2=light_images('y1.png')
photo3=light_images('g1.png')


datapath=StringVar()
datapath.set("")

p_address=StringVar()
p_address.set("")

module_name=StringVar()
module_name.set("e.g:: Kickoff Module")

current_th=StringVar()
current_th.set("10000")

start_voltage=StringVar()
start_voltage.set('')

end_voltage=StringVar()
end_voltage.set('')

step_voltage=StringVar()
step_voltage.set('5')

down_step_voltage=StringVar()
down_step_voltage.set('10')


delay_time=StringVar()
delay_time.set('1')

light_image=StringVar()
light_image.set('r1.png')

current_datetimes=StringVar()
current_datetimes.set("")

arduino_ports=StringVar()
arduino_ports.set("Choose Option")

p_reading=StringVar()
p_reading.set('VOLTAGE::  V\nCURRENT:: μA')


single_voltage=StringVar()
single_voltage.set('')


user_answer = StringVar() 
user_answer.set('')
answers = ["HV", "IV"]

var = IntVar()


width, height = get_screen_size()
window.geometry(f'{int(width)}x{int(height)}')
height=height*.80
figure=None

window.state('normal')
window.title('NISER CMS GROUP')
window.configure(bg="red")
bold_font = Font(family="arial", weight="bold",size=10)
bold_font2 = Font(family="arial", weight="bold",size=14)


scrollbar = Tk.Scrollbar(window,orient='vertical')
scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)

scrollbarx = Tk.Scrollbar(window, orient='horizontal')
scrollbarx.pack(side=Tk.BOTTOM, fill=Tk.X)



canvas = Tk.Canvas(window,xscrollcommand=scrollbarx.set, yscrollcommand=scrollbar.set,width=width, height=height)
canvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
scrollbarx.config(command=canvas.xview)
scrollbar.config(command=canvas.yview)




master_frame = Tk.Frame(canvas,width=width,height=height)
canvas.create_window((0, 0), window=master_frame, anchor="nw")



Style=ttk.Style()
Style.configure('TNotebook.Tab',padding=(20,8),font=('Helvetica',12,'bold'))
tab_control = ttk.Notebook(master_frame)
tab1 = Tk.Frame(tab_control,width=width)
tab2 = Tk.Frame(tab_control,width=width)
tab_control.add(tab1, text='HV/IV TEST')


tab_control.add(tab2, text='MONITOR')

tab_control.pack(fill=Tk.BOTH, expand=True)

button_frame_width=width*0.2
button_frame_height=height
button_frame = Tk.Frame(tab1,bg='darkslategray', width=button_frame_width, height=button_frame_height)
button_frame.pack(side=Tk.LEFT, fill=Tk.Y)
button_frame.grid_propagate(False)

label1=Label(button_frame,width=int(button_frame_width),text='Keithley 2470 HV Controller',fg='darkblue',bg='linen',relief='solid',font=("arial",12,"bold")) 

label1.grid(row=0, column=0, sticky="new",padx=0,pady=0)

label8=Label(button_frame,bg='white',width=int(button_frame_width),text='SEARCH OR SET SOURCE ADDRESS',relief='solid',font=("arial",11,"bold")) 
label8.grid(row=1, column=0, sticky="ew",padx=0,pady=0)
ps_address_screen=Entry(button_frame,textvar=p_address,font='lucida 15')
ps_address_screen.grid(row=2, column=0, sticky="n",padx=5,pady=0)
ps_address_screen.bind("<FocusIn>", on_enter)
ps_address_screen.bind("<FocusOut>", on_leave)


ps_find=Button(button_frame,text='SEARCH OR SET',bg='tomato',fg='white',relief=GROOVE,font=("arial",13,"bold"),command=search_or_set)
ps_find.grid(row=3, column=0, sticky="ew",padx=5,pady=0)



label2=Label(button_frame,bg='white',width=int(button_frame_width),text='GIVE THE SENSOR/MODULE NAME',relief='solid',font=("arial",11,"bold")) 
label2.grid(row=4, column=0, sticky="new",padx=0,pady=0)
screen=Entry(button_frame,textvar=module_name,font='lucida 15')
screen.grid(row=5, column=0, sticky="n",padx=5,pady=0)
screen.bind("<FocusIn>", on_entry_click)
screen.bind("<FocusOut>", on_focus_out)



label9=Label(button_frame,bg='white',width=int(button_frame_width),text='TEST TYPE HV/IV',relief='solid',font=("arial",11,"bold")) 
label9.grid(row=6, column=0, sticky="new",padx=0,pady=0)


radio_button1 = Radiobutton(button_frame, text='HV TEST', variable=user_answer, value='HV',command=HVTEST)
radio_button1.grid(row=7, column=0, sticky="new",padx=5,pady=0)

radio_button1.bind("<Return>", radioselect1)
radio_button1.deselect()

radio_button2 = Radiobutton(button_frame, text='IV TEST', variable=user_answer, value='IV',command=IVTEST)
radio_button2.grid(row=8, column=0, sticky="new",padx=5,pady=0)
radio_button2.bind("<Return>",radioselect2 )
radio_button2.deselect()


label4=Label(button_frame,bg='white',width=int(button_frame_width),text='SET START VOLTAGE IN VOLT',relief='solid',font=("arial",11,"bold")) 
label4.grid(row=9, column=0, sticky="new",padx=0,pady=0)
start_vol_screen=Entry(button_frame,textvar=start_voltage,font='lucida 15')
start_vol_screen.grid(row=10, column=0, sticky="n",padx=0,pady=0)
start_vol_screen.bind("<FocusIn>", on_enter)
start_vol_screen.bind("<FocusOut>", on_leave)



label5=Label(button_frame,bg='white',width=int(button_frame_width),text='SET END VOLTAGE IN VOLT',relief='solid',font=("arial",11,"bold")) 
label5.grid(row=11, column=0, sticky="new",padx=0,pady=0)
end_vol_screen=Entry(button_frame,textvar=end_voltage,font='lucida 15')
end_vol_screen.grid(row=12, column=0, sticky="n",padx=5,pady=0)
end_vol_screen.bind("<FocusIn>", on_enter)
end_vol_screen.bind("<FocusOut>", on_leave)

label8=Label(button_frame,bg='white',width=int(button_frame_width),text='TEMPERATURE AND HUMIDITY',relief='solid',font=("arial",11,"bold")) 
label8.grid(row=13, column=0, sticky="n",padx=0,pady=0)

check_button = Checkbutton(button_frame, text="STORE TEMP & HUMID DATA", variable=var, command=lambda: check_button_clicked(var))
check_button.grid(row=14, column=0, sticky="n",padx=0,pady=0)

buttondata=Button(button_frame,text='RUN',bg='tomato',fg='white',relief=GROOVE,font=("arial",11,"bold"),command=start_process)
buttondata.grid(row=15, column=0, sticky="ew",padx=0,pady=10)
buttondata.bind("<Return>",start_process)


label3=Label(button_frame,bg='white',width=int(button_frame_width),text='SET CURRENT THRESHOLD IN μA',relief='solid',font=("Tahoma",11,"bold"))
label3.grid(row=16, column=0, sticky="new",padx=0,pady=0)
threshold_screen=Entry(button_frame,textvar=current_th,font='lucida 15')
threshold_screen.bind("<FocusIn>", on_enter)
threshold_screen.bind("<FocusOut>", on_leave)

threshold_screen.grid(row=17, column=0, sticky="n",padx=0,pady=0)

label6=Label(button_frame,bg='white',width=int(button_frame_width),text='SET RAMP-UP STEP IN VOLT',relief='solid',font=("arial",11,"bold")) 
label6.grid(row=18, column=0, sticky="new",padx=0,pady=0)
step_vol_screen=Entry(button_frame,textvar=step_voltage,font='lucida 15')
step_vol_screen.grid(row=19, column=0, sticky="n",padx=0,pady=0)
step_vol_screen.bind("<FocusIn>", on_enter)
step_vol_screen.bind("<FocusOut>", on_leave)


label6=Label(button_frame,bg='white',width=int(button_frame_width),text='SET RAMP-DOWN STEP IN VOLT',relief='solid',font=("arial",11,"bold")) 
label6.grid(row=20, column=0, sticky="new",padx=0,pady=0)
step_vol_screen=Entry(button_frame,textvar=down_step_voltage,font='lucida 15')
step_vol_screen.grid(row=21, column=0, sticky="n",padx=0,pady=0)
step_vol_screen.bind("<FocusIn>", on_enter)
step_vol_screen.bind("<FocusOut>", on_leave)


label7=Label(button_frame,bg='white',width=int(button_frame_width),text='SET DELAY TIME IN SECONDS',relief='solid',font=("arial",11,"bold")) 
label7.grid(row=22, column=0, sticky="new",padx=0,pady=0)
delay_t=Entry(button_frame,textvar=delay_time,font='lucida 15')
delay_t.grid(row=23, column=0, sticky="n",padx=0,pady=0)
delay_t.bind("<FocusIn>", on_enter)
delay_t.bind("<FocusOut>", on_leave)

labelS6=Label(button_frame,bg='white',width=int(button_frame_width),text='SET SINGLE VOLTAGE',relief='solid',font=("arial",11,"bold"))
labelS6.grid(row=24, column=0, sticky="new",padx=0,pady=0)
step_vol_screen=Entry(button_frame,textvar=single_voltage,font='lucida 15')
step_vol_screen.grid(row=25, column=0, sticky="n",padx=0,pady=0)
step_vol_screen.bind("<FocusIn>", on_enter)
step_vol_screen.bind("<FocusOut>", on_leave)

buttonS=Button(button_frame,text='SET VOLTAGE',bg='tomato',fg='white',relief=GROOVE,font=("arial",11,"bold"),command=set_single_voltage)
buttonS.grid(row=26, column=0, sticky="ew",padx=0,pady=0)
buttonS.bind("<Return>",set_single_voltage)

buttonS=Button(button_frame,text='RAMP DOWN',bg='tomato',fg='white',relief=GROOVE,font=("arial",11,"bold"),command=ramp_down_single_voltage)
buttonS.grid(row=27, column=0, sticky="ew",padx=0,pady=0)
buttonS.bind("<Return>",ramp_down_single_voltage)
buttonExit=Button(button_frame,text='EXIT',bg='tomato',fg='white',relief=GROOVE,font=("arial",11,"bold"),command=exits)
buttonExit.grid(row=28, column=0, sticky="ew",padx=0,pady=0)
buttonExit.bind("<Return>",exits)

button_frame.grid_rowconfigure(0, weight=1)
button_frame.grid_rowconfigure(1, weight=1)
button_frame.grid_rowconfigure(2, weight=1)
button_frame.grid_rowconfigure(3, weight=1)
button_frame.grid_rowconfigure(4, weight=1)
button_frame.grid_rowconfigure(5, weight=1)
button_frame.grid_rowconfigure(6, weight=1)
button_frame.grid_rowconfigure(7, weight=1)
button_frame.grid_rowconfigure(8, weight=1)
button_frame.grid_rowconfigure(9, weight=1)
button_frame.grid_rowconfigure(10, weight=1)
button_frame.grid_rowconfigure(11, weight=1)
button_frame.grid_rowconfigure(12, weight=1)
button_frame.grid_rowconfigure(13, weight=1)
button_frame.grid_rowconfigure(14, weight=1)
button_frame.grid_rowconfigure(15, weight=1)
button_frame.grid_rowconfigure(16, weight=1)
button_frame.grid_rowconfigure(17, weight=1)
button_frame.grid_rowconfigure(18, weight=1)
button_frame.grid_rowconfigure(19, weight=1)
button_frame.grid_rowconfigure(20, weight=1)
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
 
Monitor_frame = Tk.Frame(tab1, width=button_frame_width, height=button_frame_height)
Monitor_frame.pack(side=Tk.TOP,anchor="nw")

font = ("Noto Sans", 20,'bold')
labels1 = Label(Monitor_frame,height=3 ,text=p_reading.get(),relief='solid',bg='white',fg='red', font=font)
labels1.grid(row=0, column=0, sticky="new",padx=0,pady=0)

image_label2 = ttk.Label(Monitor_frame, image=photo1)
image_label2.grid(row=0, column=1, sticky="n",padx=0,pady=0)


pause=Button(Monitor_frame,text='PAUSE',bg='tomato',fg='white',relief=GROOVE,font=("arial",11,"bold"),command=pause_plots)
pause.grid(row=0, column=2, sticky="n",padx=0,pady=0)
pause.bind("<Return>",pause_plots)

stop=Button(Monitor_frame,text='STOP',bg='tomato',fg='white',relief=GROOVE,font=("arial",11,"bold"),command=stop_run)
stop.grid(row=0, column=3, sticky="n",padx=0,pady=0)
stop.bind("<Return>",stop_run)

simu=Button(Monitor_frame,text='EXAMPLE',bg='tomato',fg='white',relief=GROOVE,font=("arial",11,"bold"),command=simulation_run)
simu.grid(row=0, column=4, sticky="n",padx=0,pady=0)
simu.bind("<Return>",simulation_run)

name = Label(Monitor_frame,text='Designed By: Dr. Tanay Dey\nContacts::tanay.phys@gmail.com',bg='white',fg='red',font=("arial",11,"bold"))
name.grid(row=0, column=5, sticky="n",padx=20,pady=0)



Monitor_frame.grid_rowconfigure(0, weight=1)
Monitor_frame.grid_columnconfigure(0, weight=1)
Monitor_frame.grid_columnconfigure(1, weight=1)
Monitor_frame.grid_columnconfigure(2, weight=1)
Monitor_frame.grid_columnconfigure(3, weight=1)
Monitor_frame.grid_columnconfigure(4, weight=1)

canvas_frame = Tk.Frame(tab1, width=button_frame_width, height=button_frame_height)
canvas_frame.pack(anchor="center",expand=True)

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
    
image_path_k = Image.os.path.join(base_path,'light_files','keithley.png')
image_keithley = Image.open(image_path_k) 
resized_image_keithley = image_keithley.resize((700, 300))
photo_keithley = ImageTk.PhotoImage(resized_image_keithley)
image_label_keithley = ttk.Label(canvas_frame, image=photo_keithley)
image_label_keithley.pack(fill=Tk.BOTH, expand=True)

style.use('ggplot')

figure, ax = plt.subplots(figsize=((width*0.0078, height*0.008)))
figure_canvas = FigureCanvasTkAgg(figure, master=canvas_frame)

plot1, = ax.plot([], [] ,'kh',linestyle='None',label="I-V w.r.t Measured voltage")
plot2, = ax.plot([], [] ,'ro',linestyle='None',label="I-V w.r.t Set voltage")
plot3, = ax.plot([], [], 'b' ,linestyle='None',label="Set voltage")

ax2 = ax.twinx()

plot4, = ax2.plot([], [], 'ro' ,linestyle='None',label="Set voltage")
plot5, = ax2.plot([], [], 'bd' ,linestyle=':',label="Temperature")
plot6, = ax2.plot([], [], 'ms' ,linestyle='-.',label="Humidity")

canvas_frame.grid_rowconfigure(0, weight=1)
canvas_frame.grid_columnconfigure(1, weight=1)

window.protocol("WM_DELETE_WINDOW", exits)
window.columnconfigure(1, weight=1)
window.rowconfigure(0, weight=1)
master_frame.bind("<Configure>", on_configure)
canvas.bind("<MouseWheel>", on_mousewheel)

window.mainloop()

