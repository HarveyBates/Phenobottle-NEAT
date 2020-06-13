# -------- Imports not needed for testing UI -------- #

# from Adafruit_MotorHAT import Adafruit_MotorHAT
# from twilio.rest import Client
# import serial
# import RPi.GPIO as GPIO

# ---------- Imports needed for testing UI ---------- #
import pymysql.cursors
import matplotlib.pyplot as plt
import datetime
import atexit
import time
import csv
import math
from time import strftime
import random
import datetime as dt
import tkinter as tk
import tkinter.font as tkFont
from functools import partial

# ---------- Phenobottle Imports ---------- #
from PhenoMotors import MotorsAndLights
from PhenoSensors import Sensors, Test
from PhenoExperiment import Experiment
from PhenoData import Database, Excel
from PhenoSMS import Readings

# Graphing Window Imports
#import matplotlib.pyplot as plt

#  ---------------------------------------------- Status Variables --------------------------------------------- #

measure = False
use_sensor_data = False # for testing with random data, keep as False

SERIAL_PORT = '/dev/ttyACM0'
if use_sensor_data is True:
    ser = serial.Serial(SERIAL_PORT, 115200)

if use_sensor_data is True:
    MOTOR_INDEX = Adafruit_MotorHAT(addr=0x60)
    MIXING_MOTOR = MOTOR_INDEX.getMotor(1)
    PERISTALTIC_MOTOR = MOTOR_INDEX.getMotor(2)
    BUBBLING_MOTOR = MOTOR_INDEX.getMotor(3)
    LIGHT_CONTROL = MOTOR_INDEX.getMotor(4)


# -------------------------------------------- Setup Required Below -------------------------------------------- #

PHENOBOTTLE_NUMBER = 1
LIGHT_INTENSITY = 220
INITIAL_OPTICAL_DENSITY = 2003
ARDUINO_FLUORESCENCE_REFERENCE = 3.3

# -------------------------------------------- Testing/Inital Variables -------------------------------------------- #
update_in_progress = False
MEASUREMENT_INTERVAL, BUBBLE_TIME, MIX_TIME, REMOVE_MICROAGLAE_TIME = 0, 3, 2, 2
MIXING_DIRECTION, BUBBLE_DIRECTION, PERISTALTIC_DIRECTION = 0, 0, 0
MIX_ON, BUBBLE_ON, LIGHT_ON, PERI_ON = 0, 0, 0, 0
LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE = 0, 0, 0
RGB_COL = '#000000'


optical_density, transmittance, od_raw, temperature = 0, 0, 0, 0
fo, f_300us, fj, fi, fm, variable_fluorescence, quantum_yield = 0, 0, 0, 0, 0, 0, 0
vj, fm_qa, mo, performance_index = 0, 0, 0, 0
fj_fo, fi_fo, fi_fj, fm_fi = 0, 0, 0, 0
fo_od, fj_od, fi_od, fm_od = 0, 0, 0, 0
variable_fluorescence_od, fm_qa_od = 0, 0
time_ojip, value_ojip, norm_ojip = 0, 0, 0
light_intensity_a = 0

time_now = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
day_night = "N/a"

IP_ADDRESS = "138.25.85.169"
PORT_NUMBER = 3306
USERNAME = "exampleuser"
PASSWORD = "Phenobottle1234"

ACCOUNT_SSID = "ACdac205575b8ee76ccb75c54d2e43a849"
ACCOUNT_TOKEN = "7ed56ee356583ce077d57333db8044b8"
FROM_PHONE = "+12013895981"
TO_PHONE = "+61478515336"
comms_status = "Status: Not Connected"

first_wait_messaged = False
day_night_check = ""
first_day_night_checked = False
experiment_next_reading = ""

# ---------------------------------- Preset Motor and Light Intensity ---------------------------------- #

MIXING_SPEED = 32
BUBBLING_INTENSITY = 60
LIGHT_INTENSITY = 220
PERISTALTIC_SPEED = 160

EXPERIMENT_START_TIME = "07:00" # hours:minutes (:seconds)
DAY_PERIOD_START = '06:00'
DAY_PERIOD_END = '20:00'

# --------- global variables for tkinter (GUI) --------- #
# Change font size based on which operating system is used
FONT_SIZE = 10
BIG_FONT = FONT_SIZE + 2
customFontBig = '{arial bold} %i' %BIG_FONT
customFont = 'arial {}'.format(FONT_SIZE)
buttonFont = '{arial bold} 8'

class Phenobottle_Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.dynamic_update()
        self.update_widget()
        self.initalise_widgets()

    def create_widgets(self):
        global account_ssid_var, account_token_var
        # Setup Database and Communications
        self.label_setup_database = tk.Label(self, text="Setup Database and Communications", font=customFontBig)
        self.label_setup_database.grid(row=0, column=0, columnspan=2)
        self.phenobottle_number_var = tk.StringVar(self, value = PHENOBOTTLE_NUMBER)
        self.label_phenobottle_number = tk.Label(self, text="Phenobottle Number: ", font=customFont)
        self.entry_phenobottle_number = tk.Entry(self, textvariable=self.phenobottle_number_var, width=15)
        self.label_phenobottle_number.grid(row=1, column=0, sticky="w", padx=4)
        self.entry_phenobottle_number.grid(row=1, column=1, sticky="e", padx=4)
        self.serial_port_var = tk.StringVar(self, value = SERIAL_PORT)
        self.label_serial_port = tk.Label(self, text="Serial Port: ", font=customFont)
        self.entry_serial_port = tk.Entry(self, textvariable=self.serial_port_var, width=15)
        self.label_serial_port.grid(row=2, column=0, sticky="w", padx=4)
        self.entry_serial_port.grid(row=2, column=1, sticky="e", padx=4)

        self.label_database = tk.Label(self, text="Database: ", font=customFontBig)
        self.label_database.grid(row=3, column=0, sticky="w")
        self.ip_address_var = tk.StringVar(self, value = IP_ADDRESS)
        self.label_ip_address = tk.Label(self, text="IP Address: ", font=customFont)
        self.entry_ip_address = tk.Entry(self, textvariable=self.ip_address_var, width=15)
        self.label_ip_address.grid(row=4, column=0, sticky="w", padx=4)
        self.entry_ip_address.grid(row=4, column=1, sticky="e", padx=4)
        self.port_number_var = tk.StringVar(self, value = PORT_NUMBER)
        self.label_port_number = tk.Label(self, text="Port Number: ", font=customFont)
        self.entry_port_number = tk.Entry(self, textvariable=self.port_number_var, width=15)
        self.label_port_number.grid(row=5, column=0, sticky="w", padx=4)
        self.entry_port_number.grid(row=5, column=1, sticky="e", padx=4)
        self.username_var = tk.StringVar(self, value = USERNAME)
        self.label_username = tk.Label(self, text="Username", font=customFont)
        self.entry_username = tk.Entry(self, textvariable=self.username_var, width=15)
        self.label_username.grid(row=6, column=0, sticky="w", padx=4)
        self.entry_username.grid(row=6, column=1, sticky="e", padx=4)
        self.password_var = tk.StringVar(self, value = PASSWORD)
        self.label_password = tk.Label(self, text="Password", font=customFont)
        self.entry_password = tk.Entry(self, textvariable=self.password_var, width=15)
        self.entry_password.config(show="*")
        self.label_password.grid(row=7, column=0, sticky="w", padx=4)
        self.entry_password.grid(row=7, column=1, sticky="e", padx=4)

        self.label_messaging = tk.Label(self, text="Messaging: ", font=customFontBig)
        self.label_messaging.grid(row=8, column=0, sticky="w")
        account_ssid_var = tk.StringVar(self, value = ACCOUNT_SSID)
        self.label_account_ssid = tk.Label(self, text="Account SSID", font=customFont)
        self.entry_account_ssid = tk.Entry(self, textvariable=account_ssid_var, width=15)
        self.entry_account_ssid.config(show="*")
        self.label_account_ssid.grid(row=9, column=0, sticky="w", padx=4)
        self.entry_account_ssid.grid(row=9, column=1, sticky="e", padx=4)
        account_token_var = tk.StringVar(self, value = ACCOUNT_TOKEN)
        self.label_account_token = tk.Label(self, text="Account Token", font=customFont)
        self.entry_account_token = tk.Entry(self, textvariable=account_token_var, width=15)
        self.entry_account_token.config(show="*")
        self.label_account_token.grid(row=10, column=0, sticky="w", padx=4)
        self.entry_account_token.grid(row=10, column=1, sticky="e", padx=4)
        self.from_phone_var = tk.StringVar(self, value = FROM_PHONE)
        self.label_from_phone = tk.Label(self, text="From Phone", font=customFont)
        self.entry_from_phone = tk.Entry(self, textvariable=self.from_phone_var, width=15)
        self.label_from_phone.grid(row=11, column=0, sticky="w", padx=4)
        self.entry_from_phone.grid(row=11, column=1, sticky="e", padx=4)
        self.to_phone_var = tk.StringVar(self, value = TO_PHONE)
        self.label_to_phone = tk.Label(self, text="To Phone", font=customFont)
        self.entry_to_phone = tk.Entry(self, textvariable=self.to_phone_var, width=15)
        self.label_to_phone.grid(row=12, column=0, sticky="w", padx=4)
        self.entry_to_phone.grid(row=12, column=1, sticky="e", padx=4)
        self.button_testcomms = tk.Button(self, text="Test Database Connection", font=customFont, background='light grey', command = self.test_database_connection)
        self.comms_status_var = tk.StringVar(self, value = comms_status)
        self.label_comms_status = tk.Label(self, textvariable=self.comms_status_var, font=customFont, fg="red")
        self.button_testcomms.grid(row=13, column=0, sticky="w", padx=4)
        self.label_comms_status.grid(row=14, column=0, sticky="w", padx=4)

        # Setup Experiment
        self.label_setup_experiment = tk.Label(self, text="Setup Experiment", font=customFontBig)
        self.label_setup_experiment.grid(row=0, column=2, sticky="w", padx=4, columnspan=2)
        self.start_time_var = tk.StringVar(self, value = EXPERIMENT_START_TIME)
        self.label_start_time = tk.Label(self, text="Start Time: ", font=customFont)
        self.entry_start_time = tk.Entry(self, textvariable=self.start_time_var, width=15)
        self.label_start_time.grid(row=1, column=2, sticky="w", padx=4)
        self.entry_start_time.grid(row=1, column=3, sticky="e", padx=4)
        self.day_period_start_var = tk.StringVar(self, value = DAY_PERIOD_START)
        self.day_period_end_var = tk.StringVar(self, value = DAY_PERIOD_END)
        self.label_day_period = tk.Label(self, text="Light On (HH:MM)", font=customFont)
        self.label_day_period2 = tk.Label(self, text="Light Off (HH:MM)", font=customFont)
        self.entry_day_period_start = tk.Entry(self, textvariable=self.day_period_start_var, width=15)
        self.entry_day_period_end = tk.Entry(self, textvariable=self.day_period_end_var, width=15)
        self.label_day_period.grid(row=2, column=2, sticky="w", padx=4)
        self.label_day_period2.grid(row=3, column=2, sticky="w", padx=4)
        self.entry_day_period_start.grid(row=2, column=3, sticky="e", padx=4)
        self.entry_day_period_end.grid(row=3, column=3, sticky="e", padx=4)
        self.measurement_interval_var = tk.StringVar(self, value = MEASUREMENT_INTERVAL)
        self.label_measurement_interval = tk.Label(self, text="Interval (min): ", font=customFont)
        self.entry_measurement_interval = tk.Entry(self, textvariable=self.measurement_interval_var, width=15)
        self.label_measurement_interval.grid(row=4, column=2, sticky="w", padx=4)
        self.entry_measurement_interval.grid(row=4, column=3, sticky="e", padx=4)
        self.bubble_time_var = tk.StringVar(self, value = BUBBLE_TIME)
        self.label_bubble_time = tk.Label(self, text="Bubbling Time (s): ", font=customFont)
        self.entry_bubble_time = tk.Entry(self, textvariable=self.bubble_time_var, width=15)
        self.label_bubble_time.grid(row=5, column=2, sticky="w", padx=4)
        self.entry_bubble_time.grid(row=5, column=3, sticky="e", padx=4)
        self.mix_time_var = tk.StringVar(self, value = MIX_TIME)
        self.label_mix_time = tk.Label(self, text="Mixing Time (s): ", font=customFont)
        self.entry_mix_time = tk.Entry(self, textvariable=self.mix_time_var, width=15)
        self.label_mix_time.grid(row=6, column=2, sticky="w", padx=4)
        self.entry_mix_time.grid(row=6, column=3, sticky="e", padx=4)

        # Calibrate Optical Density
        self.label_calibrate = tk.Label(self, text="Calibrate Optical Density", font=customFontBig)
        self.label_calibrate.grid(row=7, column=2, sticky="w", padx=4, columnspan=2)
        self.optical_density_var = tk.StringVar(root, value = optical_density)
        self.optical_density_raw_var = tk.StringVar(self, value = str(od_raw))
        self.label_calibrate_desc = tk.Label(self, text="Use clear culture flask filled with medium to calibrate 100% transmission", font=customFont, wrap=200)
        self.label_calibrate_desc.grid(row=8, column=2, sticky="w", padx=4, columnspan=2, rowspan=2)
        self.label_optical_density_forcal_text = tk.Label(self, text="Optical Density (calibrated):", font=customFont)
        self.label_optical_density_forcal_text.grid(row=10, column=2, sticky="w", padx=4)
        self.label_optical_density_raw_value_text = tk.Label(self, text="Optical Density (real):", font=customFont)
        self.label_optical_density_raw_value_text.grid(row=11, column=2, sticky="w", padx=4)
        self.label_optical_density_forcal = tk.Entry(self, textvariable=self.optical_density_var, font=customFont)
        self.label_optical_density_forcal.grid(row=10, column=3, sticky="w", padx=4)
        self.label_optical_density_raw_value = tk.Entry(self, textvariable=self.optical_density_raw_var, font=customFont)
        self.label_optical_density_raw_value.grid(row=11, column=3, sticky="w", padx=4)
        self.button_calibrate = tk.Button(self, text="Calibrate", font=customFont, background="light gray", command=self.update_optical_density)
        self.button_calibrate.grid(row=12, column=2, sticky="w", padx=4)

        #Motor Speed and Light Intensity (SLiders)
        self.label_speeds_lights = tk.Label(self, text="Motor Speeds and Lights", font=customFontBig)
        self.label_speeds_lights.grid(row=0, column=5, sticky="w", padx=4, columnspan=3)
        self.mix_speed_var = tk.DoubleVar(self, value = int(MIXING_SPEED))
        self.mix_speed_scale = tk.Scale(self, variable=self.mix_speed_var, from_ = 0, to =50, orient=tk.HORIZONTAL, length=220)
        self.entry_mix_speed = tk.Entry(self, textvariable=self.mix_speed_var, width=6)
        self.label_mix_speed = tk.Label(self, text="Mixing Speed:", font=customFont)
        self.label_mix_speed.grid(row=1, column=5, sticky="w", padx=4)
        self.entry_mix_speed.grid(row=1, column=8, sticky="e", padx=4)
        self.mix_speed_scale.grid(row=2, column=5, sticky="nsew", padx=4, columnspan=4, rowspan=2)
        self.check_mix_speed = tk.Button(self, text = "Test", font=customFont, background="light gray", command=self.test_mix_speed)
        self.check_mix_speed.grid(row=1, column=6, sticky="w", padx=4)
        self.mix_speed_direction = tk.IntVar(self, value=int(MIXING_DIRECTION))
        self.mix_speed_checkbox = tk.Checkbutton(self, text="Reverse", font=customFont, variable=self.mix_speed_direction)
        self.mix_speed_checkbox.grid(row=1, column=7, sticky="w", padx=4)

        self.bubble_intensity_var = tk.DoubleVar(self, value = int(BUBBLING_INTENSITY))
        self.bubble_intensity_scale = tk.Scale(self,variable =self.bubble_intensity_var, from_ = 0, to =255, orient=tk.HORIZONTAL, length=220)
        self.entry_bubble_intensity = tk.Entry(self, textvariable=self.bubble_intensity_var, width=6)
        self.label_bubble_intensity = tk.Label(self, text="Bubbling Intensity:", font=customFont)
        self.label_bubble_intensity.grid(row=4, column=5, sticky="w", padx=4)
        self.entry_bubble_intensity.grid(row=4, column=8, sticky="e", padx=4)
        self.bubble_intensity_scale.grid(row=5, column=5, sticky="nsew", padx=4, columnspan=4, rowspan=2)
        self.check_bubble_intensity = tk.Button(self, text = "Test", font=customFont, background="light gray", command=self.test_bubble_intensity)
        self.check_bubble_intensity.grid(row=4, column=6, sticky="w", padx=4)
        self.bubble_direction = tk.IntVar(self, value=int(BUBBLE_DIRECTION))
        self.bubble_checkbox = tk.Checkbutton(self, text="Reverse", font=customFont, variable=self.bubble_direction)
        self.bubble_checkbox.grid(row=4, column=7, sticky="w", padx=4)

        self.peristaltic_speed_var = tk.DoubleVar(self, value = int(PERISTALTIC_SPEED))
        self.peristaltic_speed_scale = tk.Scale(self, variable = self.peristaltic_speed_var, from_ = 0, to =255, orient=tk.HORIZONTAL, length=220)
        self.entry_peristaltic_speed = tk.Entry(self, textvariable=self.peristaltic_speed_var, width=6)
        self.label_peristaltic_speed = tk.Label(self, text="Peristaltic Speed:", font=customFont)
        self.label_peristaltic_speed.grid(row=7, column=5, sticky="w", padx=4)
        self.entry_peristaltic_speed.grid(row=7, column=8, sticky="e", padx=4)
        self.peristaltic_speed_scale.grid(row=8, column=5, sticky="nsew", padx=4, columnspan=4, rowspan=2)
        self.check_peristaltic_speed = tk.Button(self, text = "Test", font=customFont, background="light gray", command=self.test_peristaltic_speed)
        self.check_peristaltic_speed.grid(row=7, column=6, sticky="w", padx=4)
        self.peristaltic_direction = tk.IntVar(self, value=int(PERISTALTIC_DIRECTION))
        self.peristaltic_checkbox = tk.Checkbutton(self, text="Reverse", font=customFont, variable=self.peristaltic_direction)
        self.peristaltic_checkbox.grid(row=7, column=7, sticky="w", padx=4)

        self.light_intensity_var = tk.DoubleVar(self, value = int(LIGHT_INTENSITY))
        self.light_intensity_scale = tk.Scale(self, variable = self.light_intensity_var, from_ = 0, to =255, orient=tk.HORIZONTAL, length=220, troughcolor=RGB_COL)
        self.entry_light_intensity = tk.Entry(self, textvariable = self.light_intensity_var, width=6)
        self.label_light_intensity = tk.Label(self, text="Light Intensity:", font=customFont)
        self.label_light_intensity.grid(row=10, column=5, sticky="w", padx=4)
        self.entry_light_intensity.grid(row=10, column=8, sticky="e", padx=4)
        self.light_intensity_scale.grid(row=11, column=5, sticky="nsew", padx=4, columnspan=4, rowspan=2)

        self.check_light_intensity = tk.Button(self, text = "Test", font=customFont, background="light gray", command=self.test_light_intensity)
        self.check_light_intensity.grid(row=10, column=6, sticky="w", padx=4)

        self.light_col_red_var = tk.DoubleVar(self, value = int(LIGHT_RED))
        self.light_col_red_scale = tk.Scale(self, variable = self.light_col_red_var, from_ = 0, to =255, orient=tk.HORIZONTAL, length=220)
        self.entry_light_col_red = tk.Entry(self, textvariable = self.light_col_red_var, width=6)
        self.label_light_col_red = tk.Label(self, text="Red:", font=customFont, fg=RGB_COL)
        self.label_light_col_red.grid(row=13, column=5, sticky="w", padx=4)
        self.entry_light_col_red.grid(row=13, column=8, sticky="e", padx=4)
        self.light_col_red_scale.grid(row=14, column=5, sticky="nsew", padx=4, columnspan=4, rowspan=2)
        self.light_col_green_var = tk.DoubleVar(self, value = int(LIGHT_GREEN))
        self.light_col_green_scale = tk.Scale(self, variable = self.light_col_green_var, from_ = 0, to =255, orient=tk.HORIZONTAL, length=220)
        self.entry_light_col_green = tk.Entry(self, textvariable = self.light_col_green_var, width=6)
        self.label_light_col_green = tk.Label(self, text="Green:", font=customFont, fg=RGB_COL)
        self.label_light_col_green.grid(row=16, column=5, sticky="w", padx=4)
        self.entry_light_col_green.grid(row=16, column=8, sticky="e", padx=4)
        self.light_col_green_scale.grid(row=17, column=5, sticky="nsew", padx=4, columnspan=4, rowspan=2)
        self.light_col_blue_var = tk.DoubleVar(self, value = int(LIGHT_BLUE))
        self.light_col_blue_scale = tk.Scale(self, variable = self.light_col_blue_var, from_ = 0, to =255, orient=tk.HORIZONTAL, length=220)
        self.entry_light_col_blue = tk.Entry(self, textvariable = self.light_col_blue_var, width=6)
        self.label_light_col_blue = tk.Label(self, text="Blue:", font=customFont, fg=RGB_COL)
        self.label_light_col_blue.grid(row=19, column=5, sticky="w", padx=4)
        self.entry_light_col_blue.grid(row=19, column=8, sticky="e", padx=4)
        self.light_col_blue_scale.grid(row=20, column=5, sticky="nsew", padx=4, columnspan=4, rowspan=2)

        #Graph Button
        self.new_win_button = tk.Button(self, text="Graph Data", background='light grey', command=self.graphing_window)
        self.new_win_button.grid(row=14, column=2, sticky="w")

        # Start, Stop and Quit
        self.button_start = tk.Button(self, text="Start", font=customFont, command=self.start_measuring, background='#00B200')
        self.button_start.grid(row=22,column=6, sticky="nsew", padx=2, pady=2)
        self.button_stop = tk.Button(self, text="Stop", font=customFont, command=self.stop_measuring, background = '#FF1919')
        self.button_stop.grid(row=22,column=7, sticky="nsew", padx=2, pady=2)
        self.button_quit = tk.Button(self, text="Exit", background= "light gray", font=customFont, command=self.master.destroy)
        self.button_quit.grid(row=22,column=8, sticky="nsew", padx=2, pady=2)

    def update_widget(self, state = tk.NORMAL):
        self.entry_phenobottle_number.config(state = state)
        self.entry_serial_port.config(state = state)
        self.entry_ip_address.config(state = state)
        self.entry_port_number.config(state = state)
        self.entry_username.config(state = state)
        self.entry_password.config(state = state)
        self.entry_account_ssid.config(state = state)
        self.entry_account_token.config(state = state)
        self.entry_from_phone.config(state = state)
        self.entry_to_phone.config(state = state)
        self.entry_start_time.config(state = state)
        self.entry_day_period_start.config(state = state)
        self.entry_day_period_end.config(state = state)
        self.entry_measurement_interval.config(state = state)
        self.entry_bubble_time.config(state = state)
        self.entry_mix_time.config(state = state)
        self.mix_speed_scale.config(state = state)
        self.entry_mix_speed.config(state = state)
        self.bubble_intensity_scale.config(state = state)
        self.entry_bubble_intensity.config(state = state)
        self.peristaltic_speed_scale.config(state = state)
        self.entry_peristaltic_speed.config(state = state)
        self.light_intensity_scale.config(state = state)
        self.entry_light_intensity.config(state = state)
        self.light_col_red_scale.config(state = state)
        self.entry_light_col_red.config(state = state)
        self.light_col_green_scale.config(state = state)
        self.entry_light_col_green.config(state = state)
        self.light_col_blue_scale.config(state = state)
        self.entry_light_col_blue.config(state = state)
        self.mix_speed_checkbox.config(state = state)
        self.bubble_checkbox.config(state = state)
        self.peristaltic_checkbox.config(state = state)

    def update_phenobottle_number(self, *args):
        global update_in_progress
        global PHENOBOTTLE_NUMBER
        if update_in_progress: return
        try:
            phenobottle_number_input_val = self.entry_phenobottle_number.get()
            old_val = PHENOBOTTLE_NUMBER
        except ValueError:
            return
        update_in_progress = True
        self.phenobottle_number_var.set(phenobottle_number_input_val)
        try:
            PHENOBOTTLE_NUMBER = phenobottle_number_input_val
        except ValueError:
            pass
        update_in_progress = False
        print("Phenobottle Number: ", PHENOBOTTLE_NUMBER)

    def update_serial_port(self, *args):
        global update_in_progress
        global SERIAL_PORT
        if update_in_progress: return
        try:
            serial_port_input_val = self.entry_serial_port.get()
            old_val = SERIAL_PORT
        except ValueError:
            return
        update_in_progress = True
        self.serial_port_var.set(serial_port_input_val)
        try:
            SERIAL_PORT = serial_port_input_val
        except ValueError:
            pass
        update_in_progress = False
        print("Serial Port: ", SERIAL_PORT)

    def update_ip_address(self, *args):
        global update_in_progress
        global IP_ADDRESS
        if update_in_progress: return
        try:
            ip_address_input_val = self.entry_ip_address.get()
            old_val = IP_ADDRESS
        except ValueError:
            return
        update_in_progress = True
        self.ip_address_var.set(ip_address_input_val)
        try:
            IP_ADDRESS = ip_address_input_val
        except ValueError:
            pass
        update_in_progress = False
        print("IP Address: ", IP_ADDRESS)

    def update_port_number(self, *args):
        global update_in_progress
        global PORT_NUMBER
        if update_in_progress: return
        try:
            port_number_input_val = self.entry_port_number.get()
            old_val = PORT_NUMBER
        except ValueError:
            return
        update_in_progress = True
        self.port_number_var.set(port_number_input_val)
        PORT_NUMBER = port_number_input_val
        update_in_progress = False
        print("Port Number: ", PORT_NUMBER)

    def update_username(self, *args):
        global update_in_progress
        global USERNAME
        if update_in_progress: return
        try:
            username_input_val = self.entry_username.get()
            old_val = USERNAME
        except ValueError:
            return
        update_in_progress = True
        self.username_var.set(username_input_val)
        USERNAME = username_input_val
        update_in_progress = False
        print("Username: ", USERNAME)

    def update_password(self, *args):
        global update_in_progress
        global PASSWORD
        if update_in_progress: return
        try:
            password_input_val = self.entry_password.get()
            old_val = PASSWORD
        except ValueError:
            return
        update_in_progress = True
        self.password_var.set(password_input_val)
        PASSWORD = password_input_val
        update_in_progress = False

    def update_account_ssid(self, *args):
        global update_in_progress
        global ACCOUNT_SSID
        if update_in_progress: return
        try:
            account_ssid_input_val = self.entry_account_ssid.get()
            old_val = ACCOUNT_SSID
        except ValueError:
            return
        update_in_progress = True
        account_ssid_var.set(account_ssid_input_val)
        ACCOUNT_SSID = account_ssid_input_val
        update_in_progress = False

    def update_account_token(self, *args):
        global update_in_progress
        global ACCOUNT_TOKEN
        if update_in_progress: return
        try:
            account_token_input_val = self.entry_account_token.get()
            old_val = ACCOUNT_TOKEN
        except ValueError:
            return
        update_in_progress = True
        account_token_var.set(account_token_input_val)
        ACCOUNT_TOKEN = account_token_input_val
        update_in_progress = False

    def update_from_phone(self, *args):
        global update_in_progress
        global FROM_PHONE
        if update_in_progress: return
        try:
            from_phone_input_val = self.entry_from_phone.get()
            old_val = FROM_PHONE
        except ValueError:
            return
        update_in_progress = True
        self.from_phone_var.set(from_phone_input_val)
        FROM_PHONE = from_phone_input_val
        update_in_progress = False
        print("From Phone: ", FROM_PHONE)

    def update_to_phone(self, *args):
        global update_in_progress
        global TO_PHONE
        if update_in_progress: return
        try:
            to_phone_input_val = self.entry_to_phone.get()
            old_val = TO_PHONE
        except ValueError:
            return
        update_in_progress = True
        self.to_phone_var.set(to_phone_input_val)
        try:
            TO_PHONE = to_phone_input_val
        except ValueError:
            pass
        update_in_progress = False
        print("To Phone: ", TO_PHONE)

    def check_time_hms(self, time_str):
        current_date = datetime.datetime.now().date()
        if time_str.count(":") == 1:
            try:
                time = datetime.datetime.strptime(time_str, '%H:%M').time()
                date_and_time = datetime.datetime.combine(current_date, time)
            except:
                date_and_time = time_str

        elif time_str.count(":") == 2:
            try:
                time = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
                date_and_time = datetime.datetime.combine(current_date, time)
            except:
                date_and_time = time_str
        elif time_str.count(":") == 0 and time_str.isdigit():
            if float(time_str) >= 0 and float(time_str) <= 24:
                try:
                    time = datetime.datetime.strptime(time_str, '%H').time()
                    date_and_time = datetime.datetime.combine(current_date, time)
                except:
                    date_and_time = time_str
            else:
                date_and_time = time_str
        else:
            date_and_time = time_str

        return date_and_time

    def update_start_time(self, *args):
        global update_in_progress
        global EXPERIMENT_START_TIME
        # global experiment_start_time_time
        if update_in_progress: return
        try:
            start_time_input_val = self.entry_start_time.get()
            old_val = EXPERIMENT_START_TIME
        except ValueError:
            return
        update_in_progress = True
        self.start_time_var.set(start_time_input_val)
        EXPERIMENT_START_TIME = start_time_input_val
        if self.check_time_hms(EXPERIMENT_START_TIME) != EXPERIMENT_START_TIME:
            self.experiment_start_time_time = self.check_time_hms(EXPERIMENT_START_TIME)
        update_in_progress = False
        print("Start Time: ", EXPERIMENT_START_TIME)

    def update_day_period_start(self, *args):
        global update_in_progress
        global DAY_PERIOD_START
        # global day_period_start_time
        if update_in_progress: return
        try:
            day_period_start_input_val = self.entry_day_period_start.get()
            old_val = DAY_PERIOD_START
        except ValueError:
            return
        update_in_progress = True
        self.day_period_start_var.set(day_period_start_input_val)
        DAY_PERIOD_START = day_period_start_input_val
        if self.check_time_hms(DAY_PERIOD_START) != DAY_PERIOD_START:
            self.day_period_start_time = self.check_time_hms(DAY_PERIOD_START)
        update_in_progress = False
        print("Day Start Time: ", DAY_PERIOD_START)

    def update_day_period_end(self, *args):
        global update_in_progress
        global DAY_PERIOD_END
        # global day_period_end_time
        if update_in_progress: return
        try:
            day_period_end_input_val = self.entry_day_period_end.get()
            old_val = DAY_PERIOD_END
        except ValueError:
            return
        update_in_progress = True
        self.day_period_end_var.set(day_period_end_input_val)
        DAY_PERIOD_END = day_period_end_input_val
        if self.check_time_hms(DAY_PERIOD_END) != DAY_PERIOD_END:
            self.day_period_end_time = self.check_time_hms(DAY_PERIOD_END)
        update_in_progress = False
        print("Day End Time: ", DAY_PERIOD_END)

    def update_measurement_interval(self, *args):
        global update_in_progress
        global MEASUREMENT_INTERVAL
        global measurement_interval_time
        if update_in_progress: return
        try:
                measurement_interval_input_val = self.entry_measurement_interval.get()
                old_val = MEASUREMENT_INTERVAL
        except ValueError:
                return
        update_in_progress = True
        self.measurement_interval_var.set(measurement_interval_input_val)
        try:
                MEASUREMENT_INTERVAL = int(measurement_interval_input_val)
        except ValueError:
                pass
        update_in_progress = False
        print("Measurment Interval: ", MEASUREMENT_INTERVAL)

    def update_bubble_time(self, *args):
        global update_in_progress
        global BUBBLE_TIME
        if update_in_progress: return
        try:
            bubble_time_input_val = self.entry_bubble_time.get()
            old_val = BUBBLE_TIME
        except ValueError:
            return
        update_in_progress = True
        self.bubble_time_var.set(bubble_time_input_val)
        try:
            BUBBLE_TIME = int(bubble_time_input_val)
        except ValueError:
            pass
        update_in_progress = False

    def update_mix_time(self, *args):
        global update_in_progress
        global MIX_TIME
        if update_in_progress: return
        try:
            mix_time_input_val = self.entry_mix_time.get()
            old_val = MIX_TIME
        except ValueError:
            return
        update_in_progress = True
        self.mix_time_var.set(mix_time_input_val)
        try:
            MIX_TIME = int(mix_time_input_val)
        except ValueError:
            pass
        update_in_progress = False

    def update_mix_speed(self, *args):
        global update_in_progress
        global MIXING_SPEED
        if update_in_progress: return
        try:
            mix_speed_input_val_entry = self.entry_mix_speed.get()
            mix_speed_input_val_scale = self.mix_speed_scale.get()
            old_val = MIXING_SPEED
        except ValueError:
            return
        update_in_progress = True
        if float(mix_speed_input_val_entry) != float(old_val):
            self.mix_speed_var.set(mix_speed_input_val_entry)
            self.mix_speed_scale.set(float(mix_speed_input_val_entry))
            MIXING_SPEED = mix_speed_input_val_entry
            if MIX_ON == 1:
                MotorsAndLights.mixing_motor_on()
        elif float(mix_speed_input_val_scale) != float(old_val):
            self.mix_speed_var.set(mix_speed_input_val_scale)
            self.mix_speed_scale.set(float(mix_speed_input_val_scale))
            MIXING_SPEED = mix_speed_input_val_scale
            if MIX_ON == 1:
                MotorsAndLights.mixing_motor_on()
        update_in_progress = False

    def update_bubble_intensity(self, *args):
        global update_in_progress
        global BUBBLING_INTENSITY
        if update_in_progress: return
        try:
            bubble_intensity_input_val_entry = self.entry_bubble_intensity.get()
            bubble_intensity_input_val_scale = self.bubble_intensity_scale.get()
            old_val = BUBBLING_INTENSITY
        except ValueError:
            return
        update_in_progress = True
        if float(bubble_intensity_input_val_entry) != float(old_val):
            self.bubble_intensity_var.set(bubble_intensity_input_val_entry)
            self.bubble_intensity_scale.set(float(bubble_intensity_input_val_entry))
            BUBBLING_INTENSITY = bubble_intensity_input_val_entry
            if BUBBLE_ON == 1:
                MotorsAndLights.bubbling_motor_on()
        elif float(bubble_intensity_input_val_scale) != float(old_val):
            self.bubble_intensity_var.set(bubble_intensity_input_val_scale)
            self.bubble_intensity_scale.set(float(bubble_intensity_input_val_scale))
            BUBBLING_INTENSITY = bubble_intensity_input_val_scale
            if BUBBLE_ON == 1:
                MotorsAndLights.bubbling_motor_on()

        update_in_progress = False

    def update_peristaltic_speed(self, *args):
        global update_in_progress
        global PERISTALTIC_SPEED
        if update_in_progress: return
        try:
            peristaltic_speed_input_val_entry = self.entry_peristaltic_speed.get()
            peristaltic_speed_input_val_scale = self.peristaltic_speed_scale.get()
            old_val = PERISTALTIC_SPEED
        except ValueError:
            return
        update_in_progress = True
        if float(peristaltic_speed_input_val_entry) != float(old_val):
            self.peristaltic_speed_var.set(peristaltic_speed_input_val_entry)
            self.peristaltic_speed_scale.set(float(peristaltic_speed_input_val_entry))
            PERISTALTIC_SPEED = peristaltic_speed_input_val_entry
            if PERI_ON == 1:
                MotorsAndLights.peristaltic_motor_on()
        elif float(peristaltic_speed_input_val_scale) != float(old_val):
            self.peristaltic_speed_var.set(peristaltic_speed_input_val_scale)
            self.peristaltic_speed_scale.set(float(peristaltic_speed_input_val_scale))
            PERISTALTIC_SPEED = peristaltic_speed_input_val_scale
            if PERI_ON == 1:
                MotorsAndLights.peristaltic_motor_on()
        update_in_progress = False

    def update_light_intensity(self, *args):
        global update_in_progress
        global LIGHT_INTENSITY
        if update_in_progress: return
        try:
            light_intensity_input_val_entry = self.entry_light_intensity.get()
            light_intensity_input_val_scale = self.light_intensity_scale.get()
            old_val = LIGHT_INTENSITY
        except ValueError:
            return
        update_in_progress = True
        if float(light_intensity_input_val_entry) != float(old_val):
            self.light_intensity_var.set(light_intensity_input_val_entry)
            self.light_intensity_scale.set(float(light_intensity_input_val_entry))
            LIGHT_INTENSITY = light_intensity_input_val_entry
            if LIGHT_ON == 1:
                MotorsAndLights.light_on()
        elif float(light_intensity_input_val_scale) != float(old_val):
            self.light_intensity_var.set(light_intensity_input_val_scale)
            self.light_intensity_scale.set(float(light_intensity_input_val_scale))
            LIGHT_INTENSITY = light_intensity_input_val_scale
            if LIGHT_ON == 1:
                MotorsAndLights.light_on()
        update_in_progress = False

    def update_display_colour(self, *args):
        self.label_light_col_red.config(fg=RGB_COL)
        self.label_light_col_green.config(fg=RGB_COL)
        self.label_light_col_blue.config(fg=RGB_COL)
        self.light_intensity_scale.config(troughcolor=RGB_COL)

    def update_light_red(self, *args):
        global update_in_progress
        global LIGHT_RED
        global RGB_COL
        if update_in_progress: return
        try:
            light_col_red_input_val_entry = self.entry_light_col_red.get()
            light_col_red_input_val_scale = self.light_col_red_scale.get()
            old_val = LIGHT_RED
        except ValueError:
            return
        update_in_progress = True
        if float(light_col_red_input_val_entry) != float(old_val):
            self.light_col_red_var.set(light_col_red_input_val_entry)
            self.light_col_red_scale.set(float(light_col_red_input_val_entry))
            LIGHT_RED = int(light_col_red_input_val_entry)
            RGB_COL = self.rgb_to_hex((LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE))
            self.update_display_colour()
            if LIGHT_ON == 1:
                MotorsAndLights.light_on()
        elif float(light_col_red_input_val_scale) != float(old_val):
            self.light_col_red_var.set(light_col_red_input_val_scale)
            self.light_col_red_scale.set(float(light_col_red_input_val_scale))
            LIGHT_RED = int(light_col_red_input_val_scale)
            RGB_COL = self.rgb_to_hex((LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE))
            self.update_display_colour()
            if LIGHT_ON == 1:
                MotorsAndLights.light_on()
        update_in_progress = False

    def update_light_green(self, *args):
        global update_in_progress
        global LIGHT_GREEN
        global RGB_COL
        if update_in_progress: return
        try:
            light_col_green_input_val_entry = self.entry_light_col_green.get()
            light_col_green_input_val_scale = self.light_col_green_scale.get()
            old_val = LIGHT_GREEN
        except ValueError:
            return
        update_in_progress = True
        if float(light_col_green_input_val_entry) != float(old_val):
            self.light_col_green_var.set(light_col_green_input_val_entry)
            self.light_col_green_scale.set(float(light_col_green_input_val_entry))
            LIGHT_GREEN = int(light_col_green_input_val_entry)
            RGB_COL = self.rgb_to_hex((LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE))
            self.update_display_colour()

            if LIGHT_ON == 1:
                MotorsAndLights.light_on()
        elif float(light_col_green_input_val_scale) != float(old_val):
            self.light_col_green_var.set(light_col_green_input_val_scale)
            self.light_col_green_scale.set(float(light_col_green_input_val_scale))
            LIGHT_GREEN = int(light_col_green_input_val_scale)
            RGB_COL = self.rgb_to_hex((LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE))
            self.update_display_colour()

            if LIGHT_ON == 1:
                MotorsAndLights.light_on()
        update_in_progress = False

    def update_light_blue(self, *args):
        global update_in_progress
        global LIGHT_BLUE
        global RGB_COL
        if update_in_progress: return
        try:
            light_col_blue_input_val_entry = self.entry_light_col_blue.get()
            light_col_blue_input_val_scale = self.light_col_blue_scale.get()
            old_val = LIGHT_BLUE
        except ValueError:
            return
        update_in_progress = True
        if float(light_col_blue_input_val_entry) != float(old_val):
            self.light_col_blue_var.set(light_col_blue_input_val_entry)
            self.light_col_blue_scale.set(float(light_col_blue_input_val_entry))
            LIGHT_BLUE = int(light_col_blue_input_val_entry)
            RGB_COL = self.rgb_to_hex((LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE))
            self.update_display_colour()

            if LIGHT_ON == 1:
                MotorsAndLights.light_on()

        elif float(light_col_blue_input_val_scale) != float(old_val):
            self.light_col_blue_var.set(light_col_blue_input_val_scale)
            self.light_col_blue_scale.set(float(light_col_blue_input_val_scale))
            LIGHT_BLUE = int(light_col_blue_input_val_scale)
            RGB_COL = self.rgb_to_hex((LIGHT_RED, LIGHT_GREEN, LIGHT_BLUE))
            self.update_display_colour()

            if LIGHT_ON == 1:
                MotorsAndLights.light_on()
        update_in_progress = False

    def update_optical_density(self, *args):
        global update_in_progress
        global INITIAL_OPTICAL_DENSITY
        global optical_density
        Sensors.measure_optical_density()
        if update_in_progress: return
        try:
            optical_density_input_raw_val = od_raw
            optical_density_input_val = optical_density
        except ValueError:
            return
        update_in_progress = True
        self.optical_density_var.set(optical_density_input_raw_val)
        self.optical_density_raw_var.set(optical_density_input_val)
        try:
            INITIAL_OPTICAL_DENSITY = int(optical_density_input_raw_val)
            optical_density = float(round(optical_density_input_val, 3))
        except ValueError:
            pass
        update_in_progress = False

    def test_bubble_intensity(self, *args):
        global BUBBLE_ON
        if BUBBLE_ON == 0:
            BUBBLE_ON = 1
            MotorsAndLights.bubbling_motor_on()
            self.check_bubble_intensity.config(background = 'orange')
        else:
            BUBBLE_ON = 0
            MotorsAndLights.bubbling_motor_off()
            self.check_bubble_intensity.config(background = 'light gray')

    def test_peristaltic_speed(self, *args):
        global PERI_ON
        if PERI_ON == 0:
            PERI_ON = 1
            MotorsAndLights.peristaltic_motor_on()
            self.check_peristaltic_speed.config(background = 'orange')
        else:
            PERI_ON = 0
            MotorsAndLights.peristaltic_motor_off()
            self.check_peristaltic_speed.config(background = 'light gray')

    def test_light_intensity(self, *args):
        global LIGHT_ON
        if LIGHT_ON == 0:
            LIGHT_ON = 1
            MotorsAndLights.light_on()
            self.check_light_intensity.config(background = 'orange')
        else:
            LIGHT_ON = 0
            MotorsAndLights.light_off()
            self.check_light_intensity.config(background = 'light gray')

    def test_mix_speed(self, *args):
        global MIX_ON
        if MIX_ON == 0:
            MIX_ON = 1
            MotorsAndLights.mixing_motor_on()
            self.check_mix_speed.config(background = 'orange')
        else:
            MIX_ON = 0
            MotorsAndLights.mixing_motor_off()
            self.check_mix_speed.config(background = 'light gray')

    def rgb_to_hex(self, rgb):
        #translates an rgb tuple of int to a tkinter friendly color code
        return "#%02x%02x%02x" % rgb

    def update_mixing_direction(self, *args):
        global update_in_progress
        global MIXING_DIRECTION
        if update_in_progress: return
        try:
            mix_speed_val = self.mix_speed_direction.get()
            old_val = MIXING_DIRECTION
        except ValueError:
            return
        update_in_progress = True
        self.mix_speed_direction.set(mix_speed_val)
        try:
            MIXING_DIRECTION = mix_speed_val
        except ValueError:
            pass
        update_in_progress = False
        print("MIXING DIRECTION: ", MIXING_DIRECTION)

    def update_bubble_direction(self, *args):
        global update_in_progress
        global BUBBLE_DIRECTION
        if update_in_progress: return
        try:
            bubble_val = self.bubble_direction.get()
            old_val = BUBBLE_DIRECTION
        except ValueError:
            return
        update_in_progress = True
        self.bubble_direction.set(bubble_val)
        try:
            BUBBLE_DIRECTION = bubble_val
        except ValueError:
            pass
        update_in_progress = False
        print("BUBBLE DIRECTION: ", BUBBLE_DIRECTION)

    def update_peristaltic_direction(self, *args):
        global update_in_progress
        global PERISTALTIC_DIRECTION
        if update_in_progress: return
        try:
            peristaltic_val = self.peristaltic_direction.get()
            old_val = PERISTALTIC_DIRECTION
        except ValueError:
            return
        update_in_progress = True
        self.peristaltic_direction.set(peristaltic_val)
        try:
            PERISTALTIC_DIRECTION = peristaltic_val
        except ValueError:
            pass
        update_in_progress = False
        print("PERISTALTIC DIRECTION: ", PERISTALTIC_DIRECTION)

    def initalise_widgets(self):
        self.update_phenobottle_number()
        self.update_serial_port()
        self.update_ip_address()
        self.update_port_number()
        self.update_username()
        self.update_password()
        self.update_account_ssid()
        self.update_account_token()
        self.update_from_phone()
        self.update_to_phone()
        self.update_start_time()
        self.update_day_period_start()
        self.update_day_period_end()
        self.update_measurement_interval()
        self.update_bubble_time()
        self.update_mix_time()
        self.update_mix_speed()
        self.update_bubble_intensity()
        self.update_peristaltic_speed()
        self.update_light_intensity()
        self.update_light_red()
        self.update_light_green()
        self.update_light_blue()
        self.update_mixing_direction()
        self.update_bubble_direction()
        self.update_peristaltic_direction()

    def dynamic_update(self):
        self.phenobottle_number_var.trace("w", self.update_phenobottle_number)
        self.serial_port_var.trace("w", self.update_serial_port)
        self.ip_address_var.trace("w", self.update_ip_address)
        self.port_number_var.trace("w", self.update_port_number)
        self.username_var.trace("w", self.update_username)
        self.password_var.trace("w", self.update_password)
        account_ssid_var.trace("w", self.update_account_ssid)
        account_token_var.trace("w", self.update_account_token)
        self.from_phone_var.trace("w", self.update_from_phone)
        self.to_phone_var.trace("w", self.update_to_phone)
        self.start_time_var.trace("w", self.update_start_time)
        self.day_period_start_var.trace("w", self.update_day_period_start)
        self.day_period_end_var.trace("w", self.update_day_period_end)
        self.measurement_interval_var.trace("w", self.update_measurement_interval)
        self.bubble_time_var.trace("w", self.update_bubble_time)
        self.mix_time_var.trace("w", self.update_mix_time)
        self.mix_speed_var.trace("w", self.update_mix_speed)
        self.bubble_intensity_var.trace("w", self.update_bubble_intensity)
        self.peristaltic_speed_var.trace("w", self.update_peristaltic_speed)
        self.light_intensity_var.trace("w", self.update_light_intensity)
        self.light_col_red_var.trace("w", self.update_light_red)
        self.light_col_green_var.trace("w", self.update_light_green)
        self.light_col_blue_var.trace("w", self.update_light_blue)
        self.mix_speed_direction.trace("w", self.update_mixing_direction)
        self.bubble_direction.trace("w", self.update_bubble_direction)
        self.peristaltic_direction.trace("w", self.update_peristaltic_direction)


    def check_time(self):
        self.current_time = datetime.datetime.now().time()
        time.sleep(1)
        print(self.current_time)

    def experiment_schedule(self, morning_time, night_time):
        self.current_time = datetime.datetime.now().time()
        if morning_time < night_time:
            print(self.current_time)
            return morning_time <= self.current_time <= night_time
        else:
            return self.current_time >= morning_time or self.current_time <= night_time

    def test_database_connection(self):
        print("Testing database connections")
        global comms_status
        global connection
        if IP_ADDRESS != "" and PORT_NUMBER != "" and USERNAME != "" and PASSWORD != "" and PHENOBOTTLE_NUMBER != "":
            try:
                connection = pymysql.connect(host=str(IP_ADDRESS),
                                         port=int(PORT_NUMBER),
                                         user=str(USERNAME),
                                         password=str(PASSWORD),
                                         db='Phenobottle No.%s' %PHENOBOTTLE_NUMBER,
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
                comms_status = "Status: Connected"
                self.label_comms_status.config(fg="green")
            except:
                comms_status = "Status: Bad Inputs"
                self.label_comms_status.config(fg="red")
        else:
            comms_status = "Status: Blank Inputs"
            self.label_comms_status.config(fg="red")
        self.comms_status_var.set(comms_status)

    def start_measuring(self):
        global measure
        print("Started Experiment")
        self.test_database_connection()
        self.update_widget(state = tk.DISABLED)
        self.update()
        measure = True
        # set all Entry Widgets to disabled
        self.run_experiment()

    def stop_measuring(self):
        global measure
        print("Stopped Experiment")
        measure = False
        # set all Entry Widgets to enabled
        self.update()
        try:
            self.after_cancel(self.loop_experiment)
        except AttributeError:
            pass
        self.update_widget(state = tk.NORMAL)

    def run_experiment(self):
        global first_wait_messaged
        global first_day_night_checked
        global day_night_check
        global experiment_next_reading
        if measure:
            NOW = datetime.datetime.now()
            experiment_datetime = self.check_time_hms(EXPERIMENT_START_TIME)
            experiment_datetime = NOW.replace(hour=experiment_datetime.time().hour, minute=experiment_datetime.time().minute,
                                              second=experiment_datetime.time().second, microsecond=0)

            # check every second, but only message every minute
            if experiment_datetime > NOW:
                if first_wait_messaged == False:
                    print("Current time is: ", NOW)
                    print("Experiment starting at: ", EXPERIMENT_START_TIME)
                    first_wait_messaged = True
                else:
                    if NOW.second == 0:
                        print("Current time is: ", NOW)
                        print("Experiment starting at: ", EXPERIMENT_START_TIME)

            else:
                ## first check if we start in 'daytime' or 'nighttime' ##
                ## and get the 'real' experiment start time // 'next reading time' (if START is pushed after EXPERIMENT_START_TIME has already begun)
                if first_day_night_checked == False:
                    if self.experiment_schedule(self.day_period_start_time.time(), self.day_period_end_time.time()):
                        day_night_check = "DAY"
                    else:
                        day_night_check = "NIGHT"
                    first_day_night_checked = True
                    experiment_next_reading = NOW

                # otherwise check every 10 minutes if we need to switch from 'daytime' to 'nightime'
                elif NOW.minute % 10 == 0 and NOW.second < 5:
                    if self.experiment_schedule(self.day_period_start_time.time(), self.day_period_end_time.time()):
                        if day_night_check == "NIGHT":
                            day_night_check = "DAY"
                            print("Daytime routine initiated at: ", NOW)

                    else:
                        if day_night_check == "DAY":
                            day_night_check = "NIGHT"
                            print("Nighttime routine initiated at: ", NOW)

                ## Then, run routine if measurement interval is correct
                if experiment_next_reading <= NOW:
                    # if daytime ..\
                    if day_night_check == "DAY":
                        Experiment.day_routine()
                    # if nighttime ..
                    else:
                        Experiment.night_routine()

                    # when to do next reading
                    experiment_next_reading = experiment_next_reading + datetime.timedelta(minutes = MEASUREMENT_INTERVAL)

        # if experiment hasn't started yet, get sensor measurements instead
        else:
            Test.sensors()
        # Loops over experiment to run continuiously unless stop button is pressed
        self.loop_experiment = self.after(1000, self.run_experiment)
        self.update()

    def run_experiment_test(self):
        if measure == True:
            NOW = datetime.datetime.now()
            print(NOW)
            experiment_datetime = self.check_time_hms(EXPERIMENT_START_TIME)
            experiment_datetime = NOW.replace(hour=experiment_datetime.time().hour, minute=experiment_datetime.time().minute,
                                              second=experiment_datetime.time().second, microsecond=0)

            if experiment_datetime > NOW:
                NOW = datetime.datetime.now()
                print("Current time is: ", NOW)
                print("Experiment starting at: ", EXPERIMENT_START_TIME)

            else:
                Experiment.day_routine_test()
        else:
            Test.sensors()

        self.after(3000, self.run_experiment_test)

    '''
Second window for basic graphing of ojip fluorescence
I have some scripts that would allow plotting from the SQL database or alternativly data could be accessed from
the csv file as it would be nice to see how parameters are changing overtime rather than current data only
'''
    def graphing_window(self):
        self.graph_window = tk.Toplevel(self.master)
        self.graph_window.geometry()
        self.graph_window.resizable()
        self.display = tk.Label(self.graph_window, text="Potential For Graphing Window Buttons")
        self.display.grid()
        self.button_quantum_yield = tk.Button(self.graph_window, text="Plot Quantum Yield", command=self.graph_ojip)
        self.button_quantum_yield.grid()

    def graph_ojip(self):
        global PHENOBOTTLE_NUMBER
        PHENOBOTTLE_VALUES = []
        INDEX = []
        PHENOBOTTLE_NUMBER = PHENOBOTTLE_NUMBER
        connection = pymysql.connect(host=str(IP_ADDRESS),
                                 port=int(PORT_NUMBER),
                                 user=str(USERNAME),
                                 password=str(PASSWORD),
                                 db='Phenobottle No.%s' %PHENOBOTTLE_NUMBER,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            query = '`Fv/Fm`'
            sql = 'SELECT' + query + 'FROM `Advanced Parameters`'
            cursor.execute(sql)
            for row in cursor.fetchall():
                PHENOBOTTLE_VALUES.append(*row.values())
                INDEX.append(row)
        connection.close()
        plt.plot(PHENOBOTTLE_VALUES)
        plt.show()

def _destroy(event):
    if use_sensor_data is True:
        GPIO.cleanup()
    pass


root = tk.Tk()
root.bind("<Destroy>", _destroy)
root.title("Phenobottle Dashboard")
root.resizable(False, False)
root.geometry()
app = Phenobottle_Application(master=root)
app.mainloop()
