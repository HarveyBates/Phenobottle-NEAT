import os
import neat
import datetime as dt
import serial
import math
from Adafruit_MotorHAT import Adafruit_MotorHAT


SERIAL_PORT = '/dev/ttyACM0'
SER = serial.Serial(SERIAL_PORT, 115200)
MOTOR_INDEX = Adafruit_MotorHAT(addr=0x60)
LIGHT_CONTROL = MOTOR_INDEX.getMotor(4)
light_intensity = 5

class Bottle:
    def __init__(self):
        self.light_intensity = []
        self.get_optical_density()
        self.get_OJIP()

    def get_optical_density(self):
        global optical_density
        SER.flush()
        SER.write(b'MeasureOpticalDensity')
        optical_density_bytes = SER.readline(20)
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
            optical_density = 0
        return optical_density
    
    def lights_on(self):
        LIGHT_CONTROL.run(Adafruit_MotorHAT.BACKWARD)
        LIGHT_CONTROL.setSpeed(int(light_intensity))

def eval_genomes(genomes, config):
    nets = [] # I think this is the Bottles
    genome = 0 # This is the genomes that we are trying to optimise
    net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)
    nets.append(net)

    genome.fitness = 0

    while True:
        Bottle.get_optical_density()
        if od_array.length() > 0:
            if od_array[-1] == od_array[-2]: #OD is the same
                genome.fitness += 0.2
            if od_array[-1] > od_array[-2]: # OD is the higher
                genome.fitness += 1
            if od_array[-1] < od_array[-2]: # OD is lower
                genome.fitness -= 1

    output = nets.activate((optical_density)) #takes a list or input vakyes
    
    if output >= 0.5:
        light_intensity += 1
    if output < 0: 
        light_intensity -= 1


def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    pop = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    # Run for up to 300 generations.
    winner = pop.run(eval_genomes, 50)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'NEAT-Config.txt')
    run(config_path)

