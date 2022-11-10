from pyroborobo import Pyroborobo
from deap import base, creator, tools
from controller.base import BaseController
from util.result_logger import ResultLogger
from time import time
import numpy as np
import evolution
import globals
import pickle
import random
import sys
import os

# create fitness and individual objects
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

if __name__ == "__main__":

  try:

    # get command type flag
    COMMAND_FLAG = sys.argv[1]

    # load configuration and checkpoint files
    if COMMAND_FLAG == "-s":
      CHECKPOINT_FILENAME = None
      CHECKPOINT = None
      RUN_ID = sys.argv[3] if len(sys.argv) == 4 else str(int(time()))
      CONFIG_FILENAME = sys.argv[2]
    else:
      CHECKPOINT_FILENAME = sys.argv[2]
      with open(CHECKPOINT_FILENAME, "rb") as cp_file:
        CHECKPOINT = pickle.load(cp_file)
      RUN_ID = CHECKPOINT["rid"]
      CONFIG_FILENAME = CHECKPOINT["cfg"]
    globals.init(CONFIG_FILENAME, RUN_ID)
    
    # get neural network dimensions 
    nb_inputs = globals.config.get("dInputNodes", "int")
    nb_hiddens = globals.config.get("dHiddenNodes", "int")
    nb_outputs = globals.config.get("dOutputNodes", "int")
    genome_size = (nb_inputs * nb_hiddens) + (nb_hiddens * nb_outputs)

    # define genetic operators to use
    toolbox = base.Toolbox()
    toolbox.register("attribute", random.uniform, a=-1, b=1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=genome_size)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evolution.evaluators[globals.config.get("pEvolutionAlgorithm", "str")])

    # define statistics to track
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)

    # start a new evolution simulation
    if COMMAND_FLAG == "-s":
      population        = toolbox.population(n=globals.config.get("pPopulationSize", "int"))
      start_generation  = 0
      hall_of_fame      = tools.HallOfFame(maxsize=1)
      logbook           = tools.Logbook()

    # resume a previous evolution simulation
    elif COMMAND_FLAG == "-r":
      population        = CHECKPOINT["pop"]
      start_generation  = CHECKPOINT["gen"] + 1
      hall_of_fame      = CHECKPOINT["hof"]
      logbook           = CHECKPOINT["log"]
      random.setstate(CHECKPOINT["rnd"])

    # export all statistic results from checkpoint
    elif COMMAND_FLAG == "-e":
      logbook = CHECKPOINT["log"]
      results = logbook.select("gen", "avg", "max")
      logger = ResultLogger("results", ["generation", "average fitness", "max fitness"])
      for i in range(len(results[0])):
        logger.append([results[0][i], results[1][i], results[2][i]])
      print("Results exported.")
      exit(0)

    # view simulation of elite individual from a checkpoint
    elif COMMAND_FLAG == "-v":
      TEMP_FILENAME = "config/temp.properties"
      with open(CHECKPOINT["cfg"], "r") as orig_file, open(TEMP_FILENAME, "w") as temp_file:
        for line in orig_file:
          if line.find("gBatchMode") == -1:
            temp_file.write(line)
          else:
            temp_file.write("gBatchMode = false")
      globals.init(TEMP_FILENAME, CHECKPOINT["rid"])
      elite = CHECKPOINT["hof"].items[0]
      simulator = Pyroborobo.create(globals.config_filename, controller_class=BaseController)
      simulator.start()
      globals.set_simulator(simulator)
      fitness = evolution.evaluators["SSGA"](elite)[0]
      print("Fitness = " + str(fitness))
      simulator.close()
      os.remove(TEMP_FILENAME)
      exit(0)

  except SystemExit:
    exit(0)

  except Exception as e:
    print("*" * 10, "Error Message", "*" * 10)
    print(e)
    print("*" * 10, "Usage Instructions", "*" * 10)
    print("Start Evolution:\tpython run.py -s <config file> <run id>")
    print("Resume Evolution:\tpython run.py -r <checkpoint file>")
    print("Export Results:\t\tpython run.py -e <checkpoint file>")
    print("View Simulation:\tpython run.py -v <checkpoint file>")
    exit(1)

  # load config and start simulator
  simulator = Pyroborobo.create(globals.config_filename, controller_class=BaseController)
  simulator.start()
  globals.set_simulator(simulator)

  # run all generation simulations
  for generation in range(start_generation, globals.config.get("pSimulationGenerations", "int")):

    # start generation
    start_time = time()
    globals.current_evaluations = 0
    print("Progress: 0%", end="\r", flush=True)
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

    # evaluate all individuals
    globals.set_offspring(offspring)
    fitnesses = map(toolbox.evaluate, offspring)
    for ind, fit in zip(offspring, fitnesses):
      ind.fitness.values = fit

    # replace the whole population with the offspring
    population[:] = offspring
    globals.set_population(population)

    # record stats
    hall_of_fame.update(population)
    record = stats.compile(population)
    logbook.record(gen=generation, **record)
    print("Average Fitness: " + str(record["avg"]))
    print("Maximum Fitness: " + str(record["max"]))

    # save checkpoint
    if generation % globals.config.get("pCheckpointInterval", "int") == 0:
      cp = dict(
        rid=globals.run_id,
        pop=population, 
        gen=generation, 
        hof=hall_of_fame, 
        log=logbook, 
        rnd=random.getstate(), 
        cfg=globals.config_filename
      )
      cp_dir = "./output/run_" + globals.run_id + "/checkpoints"
      if not os.path.exists(cp_dir):
        os.makedirs(cp_dir)
      with open(cp_dir + "/gen_" + str(generation) + ".pkl", "wb") as cp_file:
        pickle.dump(cp, cp_file)

    # end generation
    end_time = time()
    print("Elapsed Time: " + str(end_time - start_time) + " seconds")

  simulator.close()