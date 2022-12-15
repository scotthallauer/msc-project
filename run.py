from deap import base, creator, tools
from util.config_reader import ConfigReader
from util.result_logger import ResultLogger
from evaluator.homogenous import HomogenousEvaluator
import util.convert as convert
import numpy as np
import time
import evaluate
import multiprocessing
import pickle
import random
import sys
import os
import mapelites

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
      RUN_ID = sys.argv[3] if len(sys.argv) == 4 else str(int(time.time()))
      CONFIG_FILENAME = sys.argv[2]
      START_GENERATION = 1
    else:
      CHECKPOINT_FILENAME = sys.argv[2]
      with open(CHECKPOINT_FILENAME, "rb") as cp_file:
        CHECKPOINT = pickle.load(cp_file)
      RUN_ID = CHECKPOINT["rid"]
      CONFIG_FILENAME = CHECKPOINT["cfg"]
      START_GENERATION = CHECKPOINT["gen"] + 1
    CONFIG = ConfigReader(CONFIG_FILENAME)
    
    # get neural network dimensions 
    NB_INPUTS = CONFIG.get("dInputNodes", "int")
    NB_HIDDENS = CONFIG.get("dHiddenNodes", "int")
    NB_OUTPUTS = CONFIG.get("dOutputNodes", "int")
    GENOME_SIZE = (NB_INPUTS * NB_HIDDENS) + (NB_HIDDENS * NB_OUTPUTS)

    # define genetic operators to use
    toolbox = base.Toolbox()
    toolbox.register("attribute", random.uniform, a=-1, b=1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=GENOME_SIZE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate.evaluators[CONFIG.get("pEvolutionAlgorithm", "str")])

    # define statistics to track
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    # start a new evolution simulation
    if COMMAND_FLAG == "-s":
      population        = toolbox.population(n=CONFIG.get("pPopulationSize", "int"))
      hall_of_fame      = tools.HallOfFame(maxsize=1)
      logbook           = tools.Logbook()
      if CONFIG.get("pEvolutionAlgorithm", "str") == "MAPE":
        mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]")) 

    # resume a previous evolution simulation
    elif COMMAND_FLAG == "-r":
      population        = CHECKPOINT["pop"]
      hall_of_fame      = CHECKPOINT["hof"]
      logbook           = CHECKPOINT["log"]
      random.setstate(CHECKPOINT["rnd"])
      if CONFIG.get("pEvolutionAlgorithm", "str") == "MAPE":
        mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), population)

    # export all statistic results from checkpoint
    elif COMMAND_FLAG == "-e":
      logbook = CHECKPOINT["log"]
      results = logbook.select("gen", "avg", "std", "min", "max")
      logger = ResultLogger(RUN_ID, "results", ["generation", "avg", "std", "min", "max"])
      for i in range(len(results[0])):
        logger.append([results[0][i], results[1][i], results[2][i], results[3][i], results[4][i]])
      print("Results exported.")
      exit(0)

    elif COMMAND_FLAG == "-g":
      if CONFIG.get("pEvolutionAlgorithm", "str") != "MAPE":
        print("Cannot export grid when evolutionary algorithm is not MAP-Elites.")
        exit(0)
      grid_filename = "/".join(CHECKPOINT_FILENAME.split("/")[0:-2]) + "/performance_gen_" + str(CHECKPOINT["gen"]) + ".pdf"
      mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), CHECKPOINT["pop"])
      mapelites.plot(grid_filename)
      print("Graph exported.")
      exit(0)

    # view simulation of elite individual from a checkpoint
    elif COMMAND_FLAG == "-v":
      TEMP_FILENAME = "config/temp.properties"
      with open(CHECKPOINT["cfg"], "r") as orig_file, open(TEMP_FILENAME, "w") as temp_file:
        for line in orig_file:
          if line.find("gBatchMode") >= 0:
            temp_file.write("gBatchMode = false\n")
          elif line.find("pEvaluationTrials") >= 0:
            temp_file.write("pEvaluationTrials = 1\n")
          else:
            temp_file.write(line)
      elite = CHECKPOINT["hof"].items[0]
      manager = multiprocessing.Manager()
      process_output = manager.dict()
      process = HomogenousEvaluator(0, TEMP_FILENAME, CHECKPOINT["rid"], 1, [elite], process_output)
      process.start()
      process.join()
      print(end='\x1b[2K') # clear line
      print("Fitness = " + str(process_output[0][0][0]))
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
    print("Export MAP-Elites Grid:\t\tpython run.py -g <checkpoint file>")
    print("View Simulation:\tpython run.py -v <checkpoint file>")
    exit(1)

  # run all generation simulations
  NB_GENERATIONS = CONFIG.get("pSimulationGenerations", "int")
  for generation in range(START_GENERATION, NB_GENERATIONS + 1):

    # start generation
    generation_start = time.time()
    print("*" * 10, generation, "*" * 10)
    print("Starting...", end="\r", flush=True)

    # select the next generation individuals
    if CONFIG.get("pEvolutionAlgorithm", "str") == "MAPE" and generation != 1:
      offspring = toolbox.select(mapelites.grid, CONFIG.get("pPopulationSize", "int"))
    else:
      offspring = toolbox.select(population, CONFIG.get("pPopulationSize", "int"))

    # clone the selected individuals
    offspring = list(map(toolbox.clone, offspring))

    # apply crossover on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
      if random.random() < CONFIG.get("pCrossoverProbability", "float"):
        toolbox.mate(child1, child2)
        del child1.fitness.values
        del child2.fitness.values

    # apply mutation on the offspring
    for mutant in offspring:
      if random.random() < CONFIG.get("pMutationProbability", "float"):
        toolbox.mutate(mutant)
        del mutant.fitness.values

    # evaluate all individuals
    fitnesses = toolbox.evaluate(offspring, CONFIG_FILENAME, RUN_ID, NB_GENERATIONS, START_GENERATION, generation)
    for ind, fit in zip(offspring, fitnesses):
      if CONFIG.get("pEvolutionAlgorithm", "str") == "MAPE":
        ind.fitness.values = fit[0]
        ind.features = fit[1]
      else:
        ind.fitness.values = fit

    # update the MAP-Elites grid or replace population with offspring
    if CONFIG.get("pEvolutionAlgorithm", "str") == "MAPE":
      mapelites.grid.update(offspring)
    else:
      population[:] = offspring

    # record stats
    if CONFIG.get("pEvolutionAlgorithm", "str") == "MAPE":
      hall_of_fame.update(mapelites.grid)
      record = stats.compile(mapelites.grid)
    else:
      hall_of_fame.update(population)
      record = stats.compile(population)
    logbook.record(gen=generation, **record)
    print(end='\x1b[2K') # clear line
    print("Average Fitness: " + str(record["avg"]))
    print("Maximum Fitness: " + str(record["max"]))

    # save checkpoint
    if generation % CONFIG.get("pCheckpointInterval", "int") == 0:
      cp = dict(
        rid=RUN_ID,
        pop=(mapelites.grid if CONFIG.get("pEvolutionAlgorithm", "str") == "MAPE" else population), 
        gen=generation, 
        hof=hall_of_fame, 
        log=logbook, 
        rnd=random.getstate(), 
        cfg=CONFIG_FILENAME
      )
      cp_dir = "./output/run_" + RUN_ID + "/checkpoints"
      if not os.path.exists(cp_dir):
        os.makedirs(cp_dir)
      with open(cp_dir + "/gen_" + str(generation) + ".pkl", "wb") as cp_file:
        pickle.dump(cp, cp_file)

    # end generation
    print("Elapsed Time: " + convert.seconds_to_readable_duration(time.time() - generation_start))