from voetsch import VT4002
from KeithleyV15 import SMU26xx
from setupElab import eLabFTW
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np


# define connection parameters
ip_address = "129.27.158.42"
username = "simpacuser"   # fill in the username on the front of the climate chamber
password = "u1s2e3r4"   # fill in the password on the front of the climate chamber

# Connect to eLab and create an experiment
#exp_title = "S2_Solar_Cell"
#exp_description = "I-V Measurement"
#exp_date = datetime.datetime.now().strftime("%Y_%m_%d")
#
#elab = eLabFTW()
#elab.set_experiment(exp_title, exp_date,  exp_description)
# you can add an extra tag for your group, e.g., #SS22S3 or #WS23S1
# elab.add_tag(exp_title,"#tagname")



#sweep_function

def sweep_voltage(temperature):
    """ ******* For saving the data ******** """

    # Create unique filenames for saving the data
    time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    filename_csv = 'IV_light' + time_for_name + '_' + str(temperature) +'.csv'
    filename_pdf = 'IV_light' + time_for_name  + '_' +  str(temperature)+'.pdf'
    

    # Header for csv
    with open(filename_csv, 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
            writer.writerow(["Voltage / V", "Current / A"])

    """ ******* Connect to the Sourcemeter ******** """

    # initialize the Sourcemeter and connect to it
    # you may need to change the IP address depending on which sourcemeter you are using
    sm = SMU26xx("TCPIP0::129.27.158.13::inst0::INSTR")

    # get one channel of the Sourcemeter (we only need one for this measurement)
    smu = sm.get_channel(sm.CHANNEL_B)

    """ ******* Configure the SMU Channel B ******** """

    # reset to default settings
    smu.reset()
    # setup the operation mode
    smu.set_mode_voltage_source()
    # set the voltage and current parameters
    smu.set_voltage_range(2)
    smu.set_voltage_limit(2)
    smu.set_voltage(0)
    smu.set_current_range(1E-5)
    smu.set_current_limit(1E-5)
    smu.set_current(0)

    # enable the output
    smu.enable_output()
    """ ******* Make a voltage-sweep and do some measurements ******** """

    # define sweep parameters
    sweep_start = 0
    sweep_end = 2
    sweep_step = 0.01
    steps = int((sweep_end - sweep_start) / sweep_step)

    # define variables we store the measurement in
    data_current = []
    data_voltage = []
    data_power = []

    

    # step through the voltages and get the values from the device
    for nr in range(steps):
        # calculate the new voltage we want to set
        voltage_to_set = sweep_start + (sweep_step * nr)
        # set the new voltage to the SMU
        smu.set_voltage(voltage_to_set)
        # get current and voltage from the SMU and append it to the list so we can plot it later
        [current, voltage] = smu.measure_current_and_voltage()
        if (voltage*current) < 0:
            data_power.append(voltage*current)
            data_voltage.append(voltage)
            data_current.append(current)
        print(str(voltage)+' V; '+str(current)+' A; '+ str(voltage*current)+' W; ') 
        # Write the data in a csv
        with open(filename_csv, 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
            writer.writerow([voltage, current, voltage*current])

    

    #initialise max power
    
    max_power = 0
    
    if len(data_power) >= 1:

        max_power = abs(min(np.array(data_power)))
        
        """ ******* Plot the Data we obtained ******** """

        fig, axs = plt.subplots(2, 1)


        axs[0].semilogy(data_voltage, np.abs(np.array(data_power)),'x-', linewidth=2)

        # set labels and a title
        axs[0].set_xlabel('Voltage / V', fontsize=14)
        axs[0].set_ylabel('Power / W', fontsize=14)
        axs[0].set_title('Power Voltage plot', fontsize=14)
        axs[0].tick_params(labelsize = 14)
        #plt.tight_layout()


        axs[1].semilogy(data_voltage, np.abs(np.array(data_current)),'x-', linewidth=2)

        # set labels and a title
        axs[1].set_xlabel('Voltage / V', fontsize=14)
        axs[1].set_ylabel('Current / A', fontsize=14)
        axs[1].set_title('Characteristic curve of a diode', fontsize=14)
        axs[1].tick_params(labelsize = 14)
        #plt.tight_layout()
        fig.savefig(filename_pdf)

    # Upload files to eLab
    #elab.upload_file(filename_csv)
    #elab.upload_file(filename_pdf)
    #elab.upload_script(__file__)

    # disable the output
    smu.disable_output()

    # properly disconnect from the device
    sm.disconnect()

    return max_power



# connect to the climate chamber
climate_chamber = VT4002(ip_address, username, password)

climate_chamber.enable()

max_power_array = []
temperature_array = np.arange(5,45,5)

for T in temperature_array:
    climate_chamber.go_to_temperature(T, 0.2, 60)

    #Read out the current temperature and print the result to the console
    temp = climate_chamber.get_actual_temperature()
    print('Current temperature (°C): ' + str(temp))

    # make some measurement at each temperature
    max_power = sweep_voltage(T)
    max_power_array.append(max_power)

#Plot max power temperature curve

# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
filename_csv = 'PT_light' + time_for_name  +'.csv'
filename_pdf = 'PT_light' + time_for_name +'.pdf'

# Header for csv
with open(filename_csv, 'a') as csvfile:
    writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
    writer.writerow(["Temperature / C", "Max power / W"])

for T,P in zip(temperature_array, max_power_array):

    with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
        writer.writerow([T,P])
        
fig3, ax3 = plt.subplots(1, 1)
ax3.plot(temperature_array, max_power_array,'x-', linewidth=2)

# set labels and a title
ax3.set_xlabel('Temperature / C', fontsize=14)
ax3.set_ylabel('Max Power / W', fontsize=14)
ax3.set_title('Max power temperature plot', fontsize=14)
ax3.tick_params(labelsize = 14)
#plt.tight_layout()
fig3.savefig(filename_pdf)

#Bring the climate chamber to room temperture so you can safely open it
climate_chamber.go_to_temperature(20, 2, 60)

climate_chamber.disable()
 
