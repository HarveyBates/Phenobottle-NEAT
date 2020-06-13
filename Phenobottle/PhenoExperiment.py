class Experiment:
    @staticmethod
    def day_routine_test():
        global day_night, optical_density, od_raw, quantum_yield
        day_night = "Day"
        print('waiting for MIX_TIME')
        root.after(MIX_TIME * 1000)

        Sensors.measure_optical_density()
        Sensors.measure_fluorescence()
        Database.upload()
        Excel.upload()
        print('waiting for REMOVE_MICROAGLAE_TIME')

        root.after(REMOVE_MICROAGLAE_TIME * 1000)
        print('waiting for BUBBLE_TIME')
        root.after(BUBBLE_TIME * 1000)

    @staticmethod
    def day_routine():
        global day_night, optical_density, od_raw, quantum_yield
        day_night = "Day"
        if use_sensor_data is True:
            MotorsAndLights.light_on()
            MotorsAndLights.mixing_motor_on()
        root.after(MIX_TIME*1000)

        if use_sensor_data is True:
            MotorsAndLights.mixing_motor_off()
            MotorsAndLights.light_off()
        Sensors.measure_optical_density()
        Sensors.measure_fluorescence()

        if use_sensor_data is True:
            MotorsAndLights.light_on()
            MotorsAndLights.peristaltic_motor_on()
        Database.upload()
        Excel.upload()
        root.after(REMOVE_MICROAGLAE_TIME*1000)

        if use_sensor_data is True:
            MotorsAndLights.peristaltic_motor_off()
            MotorsAndLights.bubbling_motor_on()
            MotorsAndLights.mixing_motor_on()
        root.after(BUBBLE_TIME*1000)

        if use_sensor_data is True:
            MotorsAndLights.bubbling_motor_off()
            MotorsAndLights.mixing_motor_off()

    @staticmethod
    def night_routine():
        global day_night
        day_night = "Night"
        if use_sensor_data is True:
            MotorsAndLights.light_off()
            MotorsAndLights.mixing_motor_on()
        root.after(MIX_TIME * 1000)
        if use_sensor_data is True:
            MotorsAndLights.mixing_motor_off()

        Sensors.measure_optical_density()
        Sensors.measure_fluorescence()
        if use_sensor_data is True:
            MotorsAndLights.peristaltic_motor_on()
        Database.upload()
        Excel.upload()
        root.after(REMOVE_MICROAGLAE_TIME * 1000)

        if use_sensor_data is True:
            MotorsAndLights.peristaltic_motor_off()
            MotorsAndLights.bubbling_motor_on()
            MotorsAndLights.mixing_motor_on()
        root.after(BUBBLE_TIME * 1000)

        if use_sensor_data is True:
            MotorsAndLights.bubbling_motor_off()
            MotorsAndLights.mixing_motor_off()