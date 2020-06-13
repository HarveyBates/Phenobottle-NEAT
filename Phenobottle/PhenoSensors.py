class Sensors:
    @staticmethod
    def measure_light_intensity(quiet = False):
        global light_intensity_a
        if use_sensor_data is True:
            ser.flush()
            root.after(1000)
            ser.write(b'MeasureLightIntensity')
            if quiet is False:
                print("Waiting for response...")
            ser_bytes = ser.readline(20)
            light_intensity_a = str(ser_bytes[0:len(ser_bytes) - 2].decode("utf-8"))
        else:
            light_intensity_a = random.randint(0, 100)
        if quiet is False:
            print("Light Intensity = ", light_intensity_a)

    @staticmethod
    def measure_optical_density():
        global od_raw, transmittance, optical_density
        ser.flush()
        ser.write(b'MeasureOpticalDensity')
        optical_density_bytes = ser.readline(20)
        decoded_optical_density_bytes = str(optical_density_bytes[0:len(optical_density_bytes) - 2].decode("utf-8"))
        try:
            data_split = [float(s) for s in decoded_optical_density_bytes.split(",")]
            od_raw = data_split[0]
            initial_transmittance = od_raw / INITIAL_OPTICAL_DENSITY
            transmittance = initial_transmittance * 100
            transmittance = round(transmittance, 2)
            calc_optical_density = (-math.log10(initial_transmittance))
            optical_density = round(calc_optical_density, 3)
        except (ZeroDivisionError, ValueError) as e:
            od_raw = 0
            transmittance = 0
            optical_density = 0
        return optical_density



    @staticmethod
    def measure_temperature(quiet = False):
        global temperature
        if use_sensor_data is True:
            ser.flush()
            root.after(1000)
            ser.write(b'MeasureTemperature')
            temperature_bytes = ser.readline(20)
            decoded_temperature_bytes = str(temperature_bytes[0:len(temperature_bytes) - 2].decode("utf-8"))
            data_split = [float(s) for s in decoded_temperature_bytes.split(",")]
            temperature = data_split[0]
        else:
            temperature = 25 + (random.randint(0, 100) / 10)
        if quiet is False:
            print("Temperature = ", temperature)

    @staticmethod
    def measure_fluorescence():
        ser.write(b'MeasureFluorescence')
        value_ojip = []
        norm_ojip = []
        for _ in range(2000):
            fluorescence_bytes = ser.readline()
            decoded_fluorescence_bytes = str(fluorescence_bytes[0:len(fluorescence_bytes) - 2].decode("utf-8"))
            data_split = [float(s) for s in decoded_fluorescence_bytes.split("\t")]
            y_data = float(data_split[1])
            y_data = ((y_data * 3.3) / 4096)
            value_ojip.append(round(y_data, 3))
        fo = value_ojip[4]
        fm = max(value_ojip[10:]) 
        try:
            for e in range(len(value_ojip)):
                rvf = ((value_ojip[e] - fo) / (fm - fo))
                norm_ojip.append(round(rvf, 3))
        except ZeroDivisionError:
            norm_ojip = 0
        return norm_ojip


class Test:
    @staticmethod
    def motors_and_lights():
        MotorsAndLights.mixing_motor_on()
        root.after(30*1000)
        MotorsAndLights.mixing_motor_off()
        MotorsAndLights.bubbling_motor_on()
        root.after(10*1000)
        MotorsAndLights.bubbling_motor_off()
        MotorsAndLights.peristaltic_motor_on()
        root.after(10*1000)
        MotorsAndLights.peristaltic_motor_off()

    @staticmethod
    def sensors():
        global od_raw, transmittance, optical_density
        global fluroscence
        global temperature
        global light_intensity_a
        Sensors.measure_fluorescence(quiet = True)
        Sensors.measure_optical_density(quiet = True)
        Sensors.measure_temperature(quiet = True)
        Sensors.measure_light_intensity(quiet = True)

    @staticmethod
    def dilute_to_od():
        MotorsAndLights.light_on()
        MotorsAndLights.mixing_motor_on()
        MotorsAndLights.peristaltic_motor_on()
        root.after(10*1000)
        MotorsAndLights.mixing_motor_off()
        MotorsAndLights.peristaltic_motor_off()
        MotorsAndLights.light_off()
        root.after(2*1000)
        Sensors.measure_optical_density()
        root.after(1*1000)

