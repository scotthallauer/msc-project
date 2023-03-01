import multiprocessing
from util.suppress import suppressor
import util.calculate as calculate
import util.categorise as categorise
import util.globals as globals
from util.config_reader import ConfigReader
from monitor.progress import ProgressMonitor
import pickle
import random

def execute(population: list, config_filename: str, run_id: int, nb_generations: int, start_generation: int, current_generation: int):
  manager = multiprocessing.Manager()
  config = ConfigReader(config_filename)
  nb_processes = multiprocessing.cpu_count()
  processes = []
  process_output = manager.dict()
  process_output.clear()
  portions = apportion(population, nb_processes)
  for i in range(nb_processes):
    is_homogenous = config.get("pEvolutionAlgorithm", "str").endswith("HOM")
    is_allocation = config.get("pEvolutionAlgorithm", "str").startswith("A")
    process = IndividualEvaluator(i, config_filename, run_id, start_generation, portions[i], process_output, is_homogenous, is_allocation)
    processes.append(process)
    process.start()
  if config.get("pDynamicProgressOutput", "bool"):
    process = ProgressMonitor(nb_processes, len(population), nb_generations, current_generation, process_output)
    processes.append(process)
    process.start()
  for p in processes:
    p.join()
  fitnesses = []
  for i in range(nb_processes):
    fitnesses.extend(process_output[i])
  return fitnesses

# helper function to distribute individual evaluation to different processes
def apportion(population: list, nb_processes: int):
  allocation = len(population) // nb_processes
  overflow = len(population) % nb_processes
  portions = []
  total = 0
  for i in range(nb_processes):
    portion = population[total : total + allocation]
    total += allocation
    if i < overflow:
      portion.append(population[total])
      total += 1
    portions.append(portion)
  return portions


class IndividualEvaluator(multiprocessing.Process):

  def __init__(self, id: int, config_filename: str, run_id: str, start_generation: int, individuals: list, process_output: dict, is_homogenous: bool, is_allocation: bool):
    multiprocessing.Process.__init__(self)
    self.id = id
    self.config_filename = config_filename
    self.controllers = None
    self.run_id = run_id
    self.start_generation = start_generation
    self.individuals = individuals
    self.process_output = process_output
    self.is_homogenous = is_homogenous
    self.is_allocation = is_allocation

  def run(self):
    self.process_output[self.id] = []
    with suppressor():
      globals.init(self.config_filename, self.run_id, self.start_generation)
      if self.is_allocation:
        ar_filename = globals.config.get("pSolutionArchiveFilename", "str")
        with open(ar_filename, "rb") as ar_file:
          archive = pickle.load(ar_file)
        self.controllers = archive["sol"]
      for individual in self.individuals:
        self.process_output[self.id] = self.process_output[self.id] + [self.__evaluate(individual)]
      globals.simulator.close()

  def __evaluate(self, individual):
    if self.is_homogenous:
      for dog in categorise.get_dogs():
        dog.controller.set_genome(individual)
    else:
      genomes = self.__individual_to_genomes(individual, globals.config.get("pNumberOfDogs", "int"))
      for dog in categorise.get_dogs():
        if self.is_allocation:
          dog.controller.set_genome(self.controllers[genomes.pop()[0]])
        else:
          dog.controller.set_genome(genomes.pop())
    trial_scores = []
    behaviour_features = globals.config.get("pBehaviourFeatures", "[str]")
    trial_pen_behaviours = []
    trial_dog_behaviours = []
    trial_sheep_behaviours = []
    for _ in range(globals.config.get("pEvaluationTrials", "int")):
      self.__reset()
      globals.simulator.update(globals.config.get("pSimulationLifetime", "int"))
      trial_scores.append(globals.fitness_monitor.score())
      if "PEN" in behaviour_features:
        trial_pen_behaviours.append(globals.pen_behaviour_monitor.get_average())
      if "DOG" in behaviour_features:
        trial_dog_behaviours.append(globals.dog_behaviour_monitor.get_average())
      if "SHEEP" in behaviour_features:
        trial_sheep_behaviours.append(globals.sheep_behaviour_monitor.get_average())
    fitness = (sum(trial_scores) / len(trial_scores)),
    if len(behaviour_features) > 0:
      features = []
      if "PEN" in behaviour_features:
        features.append(sum(trial_pen_behaviours) / len(trial_pen_behaviours))
      if "DOG" in behaviour_features:
        features.append(sum(trial_dog_behaviours) / len(trial_dog_behaviours))
      if "SHEEP" in behaviour_features:
        features.append(sum(trial_sheep_behaviours) / len(trial_sheep_behaviours))
      return (fitness, features)
    else:
      return fitness
  
  def __individual_to_genomes(self, individual: list, nb_genomes: int):
    genome_size = int(len(individual) / nb_genomes)
    genomes = []
    for i in range(0, len(individual), genome_size):
      genomes.append(individual[i : i + genome_size])
    return genomes

  def __reset(self):
    # reset robot positions
    for controller in globals.simulator.controllers:
      padding = 20 # distance from sides of arena to avoid placing robots inside walls
      arena_width = globals.config.get("gArenaWidth", "int")
      arena_height = globals.config.get("gArenaHeight", "int")
      pen_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
      pen_radius = globals.config.get("pTargetZoneRadius", "int")
      pen_spawning = globals.config.get("pTargetZoneSpawning", "bool")
      while True:
        x = random.randint(padding, arena_width - padding)
        y = random.randint(padding, arena_height - padding)
        if pen_spawning or calculate.distance_from_target_zone([x, y], pen_coords, pen_radius) > 0:
          controller.set_position(x, y)
          break
    # reset monitors
    globals.fitness_monitor.reset()
    globals.pen_behaviour_monitor.reset()
    globals.dog_behaviour_monitor.reset()
    globals.sheep_behaviour_monitor.reset()