from pyroborobo import Pyroborobo
from deap import base, creator, tools
from controller.base import BaseController
from time import time
import evolution
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

stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("max", np.max)

if __name__ == "__main__":

  # load command line parameters
  try:

    RUN_TYPE = "resume" if sys.argv[1] == "-r" else "start"

    # start a new evolution simulation
    if RUN_TYPE == "start":
      run_id = sys.argv[3] if len(sys.argv) == 4 else str(int(time()))
      globals.init(_config_filename=sys.argv[2], _run_id=run_id)
      population = toolbox.population(n=globals.config.get("pPopulationSize", "int"))
      start_gen = 0
      halloffame = tools.HallOfFame(maxsize=1)
      logbook = tools.Logbook()

    # resume a previous evolution simulation
    elif RUN_TYPE == "resume":
      CHECKPOINT_FILENAME = sys.argv[2]
      with open(CHECKPOINT_FILENAME, "rb") as cp_file:
        cp = pickle.load(cp_file)
      globals.init(_config_filename=cp["configfile"], _run_id=cp["rid"])
      population = cp["population"]
      start_gen = cp["generation"]
      halloffame = cp["halloffame"]
      logbook = cp["logbook"]
      random.setstate(cp["rndstate"])

  except:
    print("*" * 10, "Usage Instructions", "*" * 10)
    print("Start Simulation:\tpython run.py -s <config file> <run id>")
    print("Resume Simulation:\tpython run.py -r <checkpoint file>")
    exit(1)

  # set evaluation method based on selected algorithm
  toolbox.register("evaluate", evolution.evaluators[globals.config.get("pEvolutionAlgorithm", "str")])

  # load config and start simulator
  simulator = Pyroborobo.create(globals.config_filename, controller_class=BaseController)
  simulator.start()
  globals.set_simulator(simulator)

  # run all generation simulations
  for generation in range(start_gen, globals.config.get("pSimulationGenerations", "int")):
    print("*" * 10, generation, "*" * 10)

    # select the next generation individuals
    offspring = toolbox.select(population, len(population))
    # clone the selected individuals
    offspring = list(map(toolbox.clone, offspring))

    # apply crossover on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
      if random.random() < globals.config.get("pCrossoverProbability", "float"):
        toolbox.mate(child1, child2)
        del child1.fitness.values
        del child2.fitness.values

    # apply mutation on the offspring
    for mutant in offspring:
      if random.random() < globals.config.get("pMutationProbability", "float"):
        toolbox.mutate(mutant)
        del mutant.fitness.values

    # evaluate all new individuals
    globals.set_offspring(offspring)
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
      ind.fitness.values = fit

    # replace the whole population with the offspring
    population[:] = offspring
    globals.set_population(population)

    # record stats
    halloffame.update(population)
    record = stats.compile(population)
    globals.fitness_logger.append([generation, record["avg"], record["max"]])
    logbook.record(gen=generation, evals=len(invalid_ind), **record)
    print(len(invalid_ind), "evaluations")

    # save checkpoint
    if generation % globals.config.get("pCheckpointInterval", "int") == 0:
      cp = dict(
        rid=globals.run_id,
        population=population, 
        generation=generation, 
        halloffame=halloffame, 
        logbook=logbook, 
        rndstate=random.getstate(), 
        configfile=globals.config_filename
      )
      cp_dir = "./output/run_" + globals.run_id + "/checkpoints"
      if not os.path.exists(cp_dir):
        os.makedirs(cp_dir)
      with open(cp_dir + "/gen_" + str(generation) + ".pkl", "wb") as cp_file:
        pickle.dump(cp, cp_file)

  simulator.close()