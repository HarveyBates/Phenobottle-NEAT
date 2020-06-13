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
    def measure_optical_density(quiet = False):
        global od_raw, transmittance, optical_density
        increment = 0
        if use_sensor_data is True:
            ser.flush()
            root.after(1000)
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
        else:
            try:
                od_raw = random.randint(0, 4096)
                initial_transmittance = od_raw / INITIAL_OPTICAL_DENSITY
                transmittance = initial_transmittance * 100
                transmittance = round(transmittance, 2)
                calc_optical_density = (-math.log10(initial_transmittance))
                optical_density = round(calc_optical_density, 3)
            except (ZeroDivisionError, ValueError) as e:
                od_raw = 0
                transmittance = 0
                optical_density = 0

        if quiet is False:
            print("Bit Count OD = ", od_raw)
            print("Transmittance (%) = ", transmittance)
            print("Optical Density = ", optical_density)

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
    def measure_fluorescence(quiet = False):
        global fo, f_300us, fj, fi, fm, variable_fluorescence, quantum_yield, vj, fm_qa, mo, performance_index, fj_fo
        global fi_fo, fi_fj, fm_fi, fo_od, fj_od, fi_od, fm_od, variable_fluorescence_od, fm_qa_od, time_ojip, value_ojip, norm_ojip
        if use_sensor_data is True:
            ser.flush()
            root.after(1000)
            ser.write(b'MeasureFluorescence')
        time_ojip = []
        value_ojip = []
        norm_ojip = []
        for _ in range(2000):
            if use_sensor_data is True:
                fluorescence_bytes = ser.readline()
                decoded_fluorescence_bytes = str(fluorescence_bytes[0:len(fluorescence_bytes) - 2].decode("utf-8"))
                data_split = [float(s) for s in decoded_fluorescence_bytes.split("\t")]
                x_data = data_split[0]
                y_data = float(data_split[1])
            else:
                x_data = (random.randint(0, 100) / 10)
                y_data = float((random.randint(0, 100) / 10))

            y_data = ((y_data * ARDUINO_FLUORESCENCE_REFERENCE) / 4096)
            time_ojip.append(x_data)
            value_ojip.append(round(y_data, 3))
        fo = value_ojip[4]
        f_300us = value_ojip[36]
        fj = value_ojip[248]
        fi = value_ojip[1023]
        fm = max(value_ojip[10:]) # Ignores the first few values as there can be a peak at 1us due to the amplifier
        fm_fi = (fm - fi)
        fi_fj = (fi - fj)
        fj_fo = (fj - fo)
        fm_fj = (fm - fj)
        fi_fo = (fi - fo)
        variable_fluorescence = (fm - fo)

        try:
            vj = (fj - fo) / variable_fluorescence
            vj = round(vj, 2)
        except ZeroDivisionError:
            vj = 0

        try:
            quantum_yield = variable_fluorescence / fm
            quantum_yield = round(quantum_yield, 2)
        except ZeroDivisionError:
            quantum_yield = 0

        try:
            mo = 4 * ((f_300us - fo) / variable_fluorescence)
            mo = round(mo, 3)
        except ZeroDivisionError:
            mo = 0

        try:
            performace_index = ((1 - (fo / fm)) / (mo / vj)) * (variable_fluorescence / fo) * ((1 - vj) / vj)
            performace_index = round(performace_index, 3)
        except ZeroDivisionError:
            performace_index = 0

        try:
            fm_qa = (fj - fo) / fj
            fm_qa = round(fm_qa, 3)
        except ZeroDivisionError:
            fm_qa = 0

        try:
            for e in range(len(value_ojip)):
                rvf = ((value_ojip[e] - fo) / (fm - fo))
                norm_ojip.append(round(rvf, 3))
        except ZeroDivisionError:
            norm_ojip = 0

        try:
            fo_od = round((fo / optical_density), 3)
        except ZeroDivisionError:
            fo_od = 0

        try:
            fj_od = round((fj / optical_density), 3)
        except ZeroDivisionError:
            fj_od = 0

        try:
            fi_od = round((fi / optical_density), 3)
        except ZeroDivisionError:
            fi_od = 0

        try:
            fm_od = round((fm / optical_density), 3)
        except ZeroDivisionError:
            fm_od = 0

        try:
            variable_fluorescence_od = round((variable_fluorescence / optical_density), 3)
        except:
            variable_fluorescence_od = 0

        try:
            fm_qa_od = round((fm_qa / optical_density), 3)
        except ZeroDivisionError:
            fm_qa_od = 0


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

