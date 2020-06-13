import neat
import time
import os
import random

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
    neat.DefaultSpeciesSet, neat.DefaultStagnation, "Hello")

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    neat_config_path = os.path.join(local_dir, "NEAT-Config.txt")
    run(neat_config_path)