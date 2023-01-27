from deap import base, creator, tools
from util.config_reader import ConfigReader
from util.result_logger import ResultLogger
from evaluator.homogenous import HomogenousEvaluator
from evaluator.heterogenous import HeterogenousEvaluator
import util.convert as convert
import numpy as np
import time
import evaluator.base as evaluate
import multiprocessing
import pickle
import random
import sys
import os
import util.mapelites as mapelites
import process.plot_solutions as plts
import process.plot_fitness as pltf
import process.plot_archive as plta

# create fitness and individual objects
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

if __name__ == "__main__":

  try:

    # get command type flag
    COMMAND_FLAG = sys.argv[1]

    if COMMAND_FLAG != "-p":

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
      if CONFIG.get("pEvolutionAlgorithm", "str").endswith("HET"):
        GENOME_SIZE = GENOME_SIZE * CONFIG.get("pNumberOfDogs", "int")

      # define genetic operators to use
      toolbox = base.Toolbox()
      toolbox.register("attribute", random.uniform, a=-1, b=1)
      toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=GENOME_SIZE)
      toolbox.register("population", tools.initRepeat, list, toolbox.individual)
      toolbox.register("mate", tools.cxTwoPoint)
      toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.05)
      toolbox.register("select", tools.selTournament, tournsize=3)
      toolbox.register("evaluate", evaluate.evaluator)

      # define statistics to track
      fitness_stats = tools.Statistics(lambda ind: ind.fitness.values)
      fitness_stats.register("avg", np.mean)
      fitness_stats.register("std", np.std)
      fitness_stats.register("min", np.min)
      fitness_stats.register("max", np.max)
      pen_bc_stats = tools.Statistics(lambda ind: ind.features[0])
      pen_bc_stats.register("avg", np.mean)
      pen_bc_stats.register("std", np.std)
      pen_bc_stats.register("min", np.min)
      pen_bc_stats.register("max", np.max)
      dog_bc_stats = tools.Statistics(lambda ind: ind.features[1])
      dog_bc_stats.register("avg", np.mean)
      dog_bc_stats.register("std", np.std)
      dog_bc_stats.register("min", np.min)
      dog_bc_stats.register("max", np.max)
      sheep_bc_stats = tools.Statistics(lambda ind: ind.features[2])
      sheep_bc_stats.register("avg", np.mean)
      sheep_bc_stats.register("std", np.std)
      sheep_bc_stats.register("min", np.min)
      sheep_bc_stats.register("max", np.max)

    # start a new evolution simulation
    if COMMAND_FLAG == "-s":
      population         = toolbox.population(n=CONFIG.get("pPopulationSize", "int"))
      hall_of_fame       = tools.HallOfFame(maxsize=1)
      fitness_logbook    = tools.Logbook()
      pen_bc_logbook     = tools.Logbook()
      dog_bc_logbook     = tools.Logbook()
      sheep_bc_logbook   = tools.Logbook()
      if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M"):
        mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]")) 

    # resume a previous evolution simulation
    elif COMMAND_FLAG == "-r":
      population         = CHECKPOINT["pop"]
      hall_of_fame       = CHECKPOINT["hof"]
      fitness_logbook    = CHECKPOINT["lgf"]
      pen_bc_logbook     = CHECKPOINT["lgp"]
      dog_bc_logbook     = CHECKPOINT["lgd"]
      sheep_bc_logbook   = CHECKPOINT["lgs"]
      random.setstate(CHECKPOINT["rnd"])
      if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M"):
        mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), population)

    # export all statistic results from checkpoint
    elif COMMAND_FLAG == "-e":
      fitness_logbook = CHECKPOINT["lgf"]
      fitness_results = fitness_logbook.select("gen", "avg", "std", "min", "max")
      fitness_logger = ResultLogger(RUN_ID, "results_fitness", ["gen", "avg", "std", "min", "max"])
      for i in range(len(fitness_results[0])):
        fitness_logger.append([fitness_results[0][i], fitness_results[1][i], fitness_results[2][i], fitness_results[3][i], fitness_results[4][i]])
      pen_bc_logbook = CHECKPOINT["lgp"]
      pen_bc_results = pen_bc_logbook.select("gen", "avg", "std", "min", "max")
      pen_bc_logger = ResultLogger(RUN_ID, "results_pen-bc", ["gen", "avg", "std", "min", "max"])
      for i in range(len(pen_bc_results[0])):
        pen_bc_logger.append([pen_bc_results[0][i], pen_bc_results[1][i], pen_bc_results[2][i], pen_bc_results[3][i], pen_bc_results[4][i]])
      dog_bc_logbook = CHECKPOINT["lgd"]
      dog_bc_results = dog_bc_logbook.select("gen", "avg", "std", "min", "max")
      dog_bc_logger = ResultLogger(RUN_ID, "results_dog-bc", ["gen", "avg", "std", "min", "max"])
      for i in range(len(dog_bc_results[0])):
        dog_bc_logger.append([dog_bc_results[0][i], dog_bc_results[1][i], dog_bc_results[2][i], dog_bc_results[3][i], dog_bc_results[4][i]])
      sheep_bc_logbook = CHECKPOINT["lgs"]
      sheep_bc_results = sheep_bc_logbook.select("gen", "avg", "std", "min", "max")
      sheep_bc_logger = ResultLogger(RUN_ID, "results_sheep-bc", ["gen", "avg", "std", "min", "max"])
      for i in range(len(sheep_bc_results[0])):
        sheep_bc_logger.append([sheep_bc_results[0][i], sheep_bc_results[1][i], sheep_bc_results[2][i], sheep_bc_results[3][i], sheep_bc_results[4][i]])
      print("Results exported.")
      exit(0)

    elif COMMAND_FLAG == "-p":
      GRAPH_TYPE = sys.argv[2] # archive, fitness, solutions
      if GRAPH_TYPE == "archive":
        AGGREGATE_PREFIX = sys.argv[3]
        plta.graph(AGGREGATE_PREFIX)
      elif GRAPH_TYPE == "fitness":
        AGGREGATE_PREFIX = sys.argv[3]
        pltf.graph(AGGREGATE_PREFIX)
      elif GRAPH_TYPE == "solutions":
        plts.graph()
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
      if CONFIG.get("pEvolutionAlgorithm", "str").endswith("HET"):
        process = HeterogenousEvaluator(0, TEMP_FILENAME, CHECKPOINT["rid"], 1, [elite], process_output)
      else:
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
    print("Plot Figures:\t\tpython run.py -p <graph type> [aggregate prefix]")
    print("View Simulation:\tpython run.py -v <checkpoint file>")
    exit(1)

  # run all generation simulations
  NB_GENERATIONS = CONFIG.get("pSimulationGenerations", "int")
  for generation in range(START_GENERATION, NB_GENERATIONS + 1):

    # start generation
    generation_start = time.time()
    print("*" * 10, generation, "*" * 10)
    if CONFIG.get("pDynamicProgressOutput", "bool"):
      print("Starting...", end="\r", flush=True)

    # select the next generation individuals
    if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M") and generation != 1:
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
      ind.fitness.values = fit[0]
      ind.features = fit[1]

    # update the MAP-Elites grid or replace population with offspring
    if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M"):
      mapelites.grid.update(offspring)
    else:
      population[:] = offspring

    # record stats
    if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M"):
      hall_of_fame.update(mapelites.grid)
      fitness_record = fitness_stats.compile(mapelites.grid)
      pen_bc_record = pen_bc_stats.compile(mapelites.grid)
      dog_bc_record = dog_bc_stats.compile(mapelites.grid)
      sheep_bc_record = sheep_bc_stats.compile(mapelites.grid)
    else:
      hall_of_fame.update(population)
      fitness_record = fitness_stats.compile(population)
      pen_bc_record = pen_bc_stats.compile(population)
      dog_bc_record = dog_bc_stats.compile(population)
      sheep_bc_record = sheep_bc_stats.compile(population)
    fitness_logbook.record(gen=generation, **fitness_record)
    pen_bc_logbook.record(gen=generation, **pen_bc_record)
    dog_bc_logbook.record(gen=generation, **dog_bc_record)
    sheep_bc_logbook.record(gen=generation, **sheep_bc_record)
    if CONFIG.get("pDynamicProgressOutput", "bool"):
      print(end='\x1b[2K') # clear line
    print("Average Fitness: " + str(fitness_record["avg"]))
    print("Maximum Fitness: " + str(fitness_record["max"]))
    print("Average Pen Distance: " + str(pen_bc_record["avg"]))
    print("Maximum Pen Distance: " + str(pen_bc_record["max"]))
    print("Average Dog Distance: " + str(dog_bc_record["avg"]))
    print("Maximum Dog Distance: " + str(dog_bc_record["max"]))
    print("Average Sheep Distance: " + str(sheep_bc_record["avg"]))
    print("Maximum Sheep Distance: " + str(sheep_bc_record["max"]))

    # save checkpoint
    if generation % CONFIG.get("pCheckpointInterval", "int") == 0:
      cp = dict(
        rid=RUN_ID,
        pop=(mapelites.grid if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M") else population), 
        gen=generation, 
        hof=hall_of_fame, 
        lgf=fitness_logbook, 
        lgp=pen_bc_logbook,
        lgd=dog_bc_logbook,
        lgs=sheep_bc_logbook,
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