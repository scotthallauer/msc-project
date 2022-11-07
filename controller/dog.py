import torch
import util.categorise as categorise
import numpy as np
import globals
from controller.radar import RadarSensor
from torch import nn

torch.manual_seed(0) # ensure bias is consistent


class DogController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.set_color(*[255, 0, 0])
    self.nb_inputs = 1 + (3 * 2) + 2 # bias + radar sensors (dogs, sheep & walls) + landmark
    self.nb_hiddens = 10
    self.nb_outputs = 2
    self.sensor_fov = (-90, 90)
    self.sensor_range = globals.config.get("dSensorRange", "int")
    self.dog_sensor = RadarSensor(self.agent, "dog", self.sensor_range, self.sensor_fov)
    self.sheep_sensor = RadarSensor(self.agent, "sheep", self.sensor_range, self.sensor_fov)
    self.wall_sensor = RadarSensor(self.agent, "wall", self.sensor_range, self.sensor_fov)
    self.network = NeuralNetwork(self.nb_inputs, self.nb_hiddens, self.nb_outputs)
    self.genome = None

  def reset(self):
    pass

  def step(self):
    #globals.ds_interaction_monitor.track(self.agent)
    output = self.network(torch.FloatTensor(self.get_inputs().reshape((1, self.nb_inputs))))
    self.agent.set_translation(output[0,0])
    self.agent.set_rotation(output[0,1])

  def get_inputs(self):
    bias = [1]

    # distance inputs are normalised between 0 and 1 (where 0 is undetected and 1 is as close as possible)
    wall_detection = self.wall_sensor.detect()
    dog_detection = self.dog_sensor.detect()
    sheep_detection = self.sheep_sensor.detect()

    landmark_dist = 1 - self.agent.get_closest_landmark_dist() # distance to the closest landmark -- normalized btw 0 and 1 (1 = close as possible)
    landmark_orient = self.agent.get_closest_landmark_orientation() # angle to closest landmark -- normalized btw -1 and +1
    
    inputs = np.concatenate((bias, wall_detection, dog_detection, sheep_detection, [landmark_dist, landmark_orient]))
    return inputs

  def set_genome(self, genome):
    self.genome = genome
    self.network.set_weights(genome)


class NeuralNetwork(nn.Module):
  
  def __init__(self, nb_inputs, nb_hiddens, nb_outputs):
    super(NeuralNetwork, self).__init__()
    self.nb_inputs = nb_inputs
    self.nb_hiddens = nb_hiddens
    self.nb_outputs = nb_outputs
    self.flatten = nn.Flatten()
    self.network = nn.Sequential(
      nn.Linear(nb_inputs, nb_hiddens),
      nn.Tanh(),
      nn.Linear(nb_hiddens, nb_outputs),
      nn.Tanh(),
    )

  def forward(self, input):
    input = self.flatten(input)
    return self.network(input)

  def set_weights(self, weights):
    with torch.no_grad():
      for hidden_node in range(self.nb_hiddens):
        start_idx = hidden_node * self.nb_inputs
        end_idx = start_idx + self.nb_inputs
        self.network[0].weight[hidden_node] = nn.Parameter(torch.FloatTensor(weights[start_idx:end_idx]))
      for output_node in range(self.nb_outputs):
        start_idx = (self.nb_inputs * self.nb_hiddens) + output_node * self.nb_hiddens
        end_idx = start_idx + self.nb_hiddens
        self.network[2].weight[output_node] = nn.Parameter(torch.FloatTensor(weights[start_idx:end_idx]))