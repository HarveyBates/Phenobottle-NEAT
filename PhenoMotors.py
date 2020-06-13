class MotorsAndLights:
    @staticmethod
    def peristaltic_motor_on():
        if PERISTALTIC_DIRECTION == 1:
            PERISTALTIC_MOTOR.run(Adafruit_MotorHAT.BACKWARD)
        else:
            PERISTALTIC_MOTOR.run(Adafruit_MotorHAT.FORWARD)
        PERISTALTIC_MOTOR.setSpeed(int(PERISTALTIC_SPEED))

    @staticmethod
    def peristaltic_motor_off():
        PERISTALTIC_MOTOR.run(Adafruit_MotorHAT.RELEASE)

    @staticmethod
    def bubbling_motor_on():
        if BUBBLE_DIRECTION == 1:
            BUBBLING_MOTOR.run(Adafruit_MotorHAT.BACKWARD)
            #print("BACK")
        else: 
            BUBBLING_MOTOR.run(Adafruit_MotorHAT.BACKWARD)
            #print("FORWARD")
        BUBBLING_MOTOR.setSpeed(int(BUBBLING_INTENSITY))

    @staticmethod
    def bubbling_motor_off():
        BUBBLING_MOTOR.run(Adafruit_MotorHAT.RELEASE)
        #print("OFF")
    @staticmethod
    def mixing_motor_on():
        if MIXING_DIRECTION == 1: 
            MIXING_MOTOR.run(Adafruit_MotorHAT.BACKWARD)
        else:
            MIXING_MOTOR.run(Adafruit_MotorHAT.FORWARD)
        MIXING_MOTOR.setSpeed(int(MIXING_SPEED))

    @staticmethod
    def mixing_motor_off():
        MIXING_MOTOR.run(Adafruit_MotorHAT.RELEASE)
        
    @staticmethod
    def light_off(color=None):
        LIGHT_CONTROL.run(Adafruit_MotorHAT.RELEASE)
        ser.flush()
        if color == "Red":
            ser.write(b'LED_light_OFF;%s' %"36".encode("utf-8"))
        root.after(50)
        if color == "Green":
            ser.write(b'LED_light_OFF;%s' %"37".encode("utf-8"))
        root.after(50)
        if color == "Blue":
            ser.write(b'LED_light_OFF;%s' %"38".encode("utf-8"))
        root.after(50)
        if color is None:
            pass
        
    @staticmethod
    def light_on():
        LIGHT_CONTROL.run(Adafruit_MotorHAT.BACKWARD)
        LIGHT_CONTROL.setSpeed(int(LIGHT_INTENSITY))
        ser.flush()
        str_red = bytes(str(LIGHT_RED), "utf-8")
        str_green = bytes(str(LIGHT_GREEN), "utf-8")
        str_blue = bytes(str(LIGHT_BLUE), "utf-8")
        ser.write(b'LED_light_ON;%s;%s;%s;%s;%s;%s' %("36".encode("utf-8"), str_red, "37".encode("utf-8"), str_green, "38".encode("utf-8"), str_blue))
        root.after(100)