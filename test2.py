from deap import base, creator, tools
import evaluate
from scoop import futures
import random

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

nb_inputs = 9
nb_hiddens = 10
nb_outputs = 2
genome_size = (nb_inputs * nb_hiddens) + (nb_hiddens * nb_outputs)

toolbox = base.Toolbox()
toolbox.register("attribute", random.uniform, a=-1, b=1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=genome_size)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("map", futures.map)

if __name__ == "__main__":

  population = toolbox.population(n=20)

  fitnesses = toolbox.map(evaluate.run, population)

  for f in fitnesses:
    print(f)
