from pyroborobo import Pyroborobo
from deap import base, creator, tools
from controller.base import BaseController
import numpy as np
import util.categorise as categorise
import globals
import pickle
import random
import sys
import os

#NB_INPUTS = 1 + (12 * 4) + 2
NB_INPUTS = 1 + (12 * 3) + 2
NB_HIDDENS = 10
NB_OUTPUTS = 2
GENOME_SIZE = (NB_INPUTS * NB_HIDDENS) + (NB_HIDDENS * NB_OUTPUTS)
POPULATION_SIZE = 10
CXPB, MUTPB = 0.5, 0.2
FREQ = 10

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attribute", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=GENOME_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

#stats = tools.Statistics(lambda ind: ind.fitness.values)
#stats.register("avg", np.mean)
#stats.register("max", np.max)

if __name__ == "__main__":

  try:
    RUN_TYPE = "resume" if sys.argv[1] == "-r" else "start"
    # start a new evolution simulation
    if RUN_TYPE == "start":
      population = toolbox.population(n=POPULATION_SIZE)
      start_gen = 0
      halloffame = tools.HallOfFame(maxsize=1)
      logbook = tools.Logbook()
      globals.init(_config_filename=sys.argv[2])
    # resume a previous evolution simulation
    elif RUN_TYPE == "resume":
      CHECKPOINT_FILENAME = sys.argv[2]
      with open(CHECKPOINT_FILENAME, "rb") as cp_file:
        cp = pickle.load(cp_file)
      population = cp["population"]
      start_gen = cp["generation"]
      halloffame = cp["halloffame"]
      logbook = cp["logbook"]
      random.setstate(cp["rndstate"])
      globals.init(_config_filename=cp["configfile"])
  except:
    print("*" * 10, "Usage Instructions", "*" * 10)
    print("Start Simulation:\tpython run.py -s <config file>")
    print("Resume Simulation:\tpython run.py -r <checkpoint file>")
    exit(1)

  # load config and start simulator
  simulator = Pyroborobo.create(globals.config_filename, controller_class=BaseController)
  simulator.start()
  globals.set_simulator(simulator)

  # add target zone to environment
  target_zone = simulator.add_landmark()
  target_zone.radius = globals.config.get("pTargetZoneRadius", "int")
  target_zone.set_coordinates(globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int"))
  target_zone.show()

  # run all generation simulations
  for generation in range(start_gen, globals.config.get("pSimulationGenerations", "int")):
    print("*" * 10, generation, "*" * 10)

    # select the next generation individuals
    offspring = toolbox.select(population, len(population))
    # clone the selected individuals
    offspring = list(map(toolbox.clone, offspring))

    # Apply crossover and mutation on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
      if random.random() < CXPB:
        toolbox.mate(child1, child2)
        del child1.fitness.values
        del child2.fitness.values

    for mutant in offspring:
      if random.random() < MUTPB:
        toolbox.mutate(mutant)
        del mutant.fitness.values

    # assign genomes to dogs
    dogs = categorise.get_dogs(simulator.controllers)
    for dog, genome in zip(dogs, offspring):
      dog.controller.set_genome(genome)

    # run single generation simulation
    stop = simulator.update(globals.config.get("pSimulationLifetime", "int"))
    if stop:
      break

    # update genome fitness
    for dog, genome in zip(dogs, population):
      genome.fitness.values = globals.individual_fitness_monitor.score(dog),

    population[:] = offspring

    halloffame.update(population)

    # log fitness results
    globals.fitness_logger.append([generation, globals.swarm_fitness_monitor.score(), globals.individual_fitness_monitor.avg_score()])
    #record = stats.compile(population)
    #logbook.record(gen=generation, **record)

    # report fitness results
    globals.individual_fitness_monitor.report()
    globals.swarm_fitness_monitor.report()

    if generation % FREQ == 0:
      cp = dict(population=population, generation=generation, halloffame=halloffame, logbook=logbook, rndstate=random.getstate(), configfile=globals.config_filename)
      cp_dir = "./checkpoints"
      if not os.path.exists(cp_dir):
        os.makedirs(cp_dir)
      with open(cp_dir + "/checkpoint" + globals.run_id + ".pkl", "wb") as cp_file:
        pickle.dump(cp, cp_file)

    # reset fitness monitors
    globals.individual_fitness_monitor.reset()
    globals.swarm_fitness_monitor.reset()

    for controller in simulator.controllers:
      controller.set_position(random.randint(0, globals.config.get("gArenaWidth", "int")), random.randint(0, globals.config.get("gArenaHeight", "int")))

  simulator.close()