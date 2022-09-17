from pyroborobo import Pyroborobo
from deap import base, creator, tools
from controller.base import BaseController
import util.categorise as categorise
import numpy as np
import globals
import pickle
import random
import sys
import os

NB_INPUTS = 1 + (12 * 3) + 2
NB_HIDDENS = 10
NB_OUTPUTS = 2
GENOME_SIZE = (NB_INPUTS * NB_HIDDENS) + (NB_HIDDENS * NB_OUTPUTS)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attribute", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=GENOME_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

def evaluate(individual):

  # reset robot positions
  for controller in globals.controllers:
    controller.set_position(random.randint(0, globals.config.get("gArenaWidth", "int")), random.randint(0, globals.config.get("gArenaHeight", "int")))

  # reset fitness monitor
  globals.swarm_fitness_monitor.reset()

  # assign genome to dogs
  dogs = categorise.get_dogs(globals.controllers)
  for dog in dogs:
    dog.controller.set_genome(individual)
  
  # run simulation
  globals.simulator.update(globals.config.get("pSimulationLifetime", "int"))

  # report fitness results
  # globals.swarm_fitness_monitor.report()

  return globals.swarm_fitness_monitor.score(),

toolbox.register("evaluate", evaluate)

stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("max", np.max)

if __name__ == "__main__":

  try:
    RUN_TYPE = "resume" if sys.argv[1] == "-r" else "start"
    # start a new evolution simulation
    if RUN_TYPE == "start":
      globals.init(_config_filename=sys.argv[2])
      population = toolbox.population(n=globals.config.get("pPopulationSize", "int"))
      start_gen = 0
      halloffame = tools.HallOfFame(maxsize=1)
      logbook = tools.Logbook()
    # resume a previous evolution simulation
    elif RUN_TYPE == "resume":
      CHECKPOINT_FILENAME = sys.argv[2]
      with open(CHECKPOINT_FILENAME, "rb") as cp_file:
        cp = pickle.load(cp_file)
      globals.init(_config_filename=cp["configfile"])
      population = cp["population"]
      start_gen = cp["generation"]
      halloffame = cp["halloffame"]
      logbook = cp["logbook"]
      random.setstate(cp["rndstate"])
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
      if random.random() < globals.config.get("pCrossoverProbability", "float"):
        toolbox.mate(child1, child2)
        del child1.fitness.values
        del child2.fitness.values

    for mutant in offspring:
      if random.random() < globals.config.get("pMutationProbability", "float"):
        toolbox.mutate(mutant)
        del mutant.fitness.values

    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
      ind.fitness.values = fit

    population[:] = offspring

    # log fitness results
    halloffame.update(population)
    record = stats.compile(population)
    globals.fitness_logger.append([generation, record["avg"], record["max"]])
    logbook.record(gen=generation, evals=len(invalid_ind), **record)
    print(len(invalid_ind), "evaluations")

    # report fitness results
    #globals.individual_fitness_monitor.report()
    #globals.swarm_fitness_monitor.report()

    if generation % globals.config.get("pCheckpointInterval", "int") == 0:
      cp = dict(population=population, generation=generation, halloffame=halloffame, logbook=logbook, rndstate=random.getstate(), configfile=globals.config_filename)
      cp_dir = "./checkpoints"
      if not os.path.exists(cp_dir):
        os.makedirs(cp_dir)
      with open(cp_dir + "/checkpoint" + globals.run_id + ".pkl", "wb") as cp_file:
        pickle.dump(cp, cp_file)

    # reset fitness monitors
    #globals.individual_fitness_monitor.reset()
    #globals.swarm_fitness_monitor.reset()

    #for controller in simulator.controllers:
    #  controller.set_position(random.randint(0, globals.config.get("gArenaWidth", "int")), random.randint(0, globals.config.get("gArenaHeight", "int")))

  simulator.close()