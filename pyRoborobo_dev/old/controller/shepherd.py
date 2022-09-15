import numpy as np
import functions.categorise as categorise
import functions.util as util

class ShepherdController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.set_color(*[255, 0, 0])
    self.agent.genome = None
    self.logged = False

  def nb_inputs(self):
    return (
      1 # bias
      + self.agent.nb_sensors * 4 # sensor inputs
      + 2 # landmark inputs
    )

  def nb_hiddens(self):
    return 10

  def nb_outputs(self):
    return 2 # translation + rotation

  def get_dimensions(self):
    return (self.nb_inputs(), self.nb_hiddens(), self.nb_outputs())

  def get_inputs(self):
    dists = self.agent.get_all_distances()
    robot_ids = self.agent.get_all_robot_ids()
    max_robots = self.agent.config.get("pRobotNumber", "int")
    is_walls = self.agent.get_all_walls()
    is_objects = self.agent.get_all_objects() != -1

    bias = [1]

    shepherds_dist = list(map(lambda i: dists[i] if categorise.is_shepherd(robot_ids[i], max_robots) else 0, range(len(robot_ids))))
    cattles_dist = list(map(lambda i: dists[i] if categorise.is_cattle(robot_ids[i], max_robots) else 0, range(len(robot_ids))))
    walls_dist = np.where(is_walls, dists, 0)
    objects_dist = np.where(is_objects, dists, 0)

    landmark_dist = self.agent.get_closest_landmark_dist()
    landmark_orient = self.agent.get_closest_landmark_orientation()

    #inputs = np.concatenate([bias, shepherds_dist, cattles_dist, walls_dist, objects_dist, [landmark_dist, landmark_orient]])
    inputs = np.concatenate((bias, shepherds_dist, cattles_dist, walls_dist, objects_dist, [landmark_dist, landmark_orient]))
    assert(len(inputs) == self.nb_inputs())
    return inputs

  def get_genome(self):
    return self.agent.genome

  def set_genome(self, genome):
    self.agent.genome = genome

  def run_genome(self):
    outputs = self.agent.genome.evaluate_network(self.get_inputs())
    # ensure translation output in allowed range
    if outputs[0] >= 0:
      outputs[0] = util.clamp(outputs[0], self.agent.config.get("sMinTranslationSpeed", "float"), self.agent.config.get("sMaxTranslationSpeed", "float"))
    else:
      outputs[0] = util.clamp(outputs[0], -self.agent.config.get("sMaxTranslationSpeed", "float"), -self.agent.config.get("sMinTranslationSpeed", "float"))
    # ensure rotation output in allowed range
    if outputs[1] >= 0:
      outputs[1] = util.clamp(outputs[1], self.agent.config.get("sMinRotationSpeed", "float"), self.agent.config.get("sMaxRotationSpeed", "float"))
    else:
      outputs[1] = util.clamp(outputs[1], -self.agent.config.get("sMaxRotationSpeed", "float"), -self.agent.config.get("sMinRotationSpeed", "float"))
    return outputs

  def reset(self):
    pass

  def step(self, fitness):
    [translation, rotation] = self.run_genome()
    self.agent.set_translation(translation)  # Let's go forward
    self.agent.set_rotation(rotation)
    #score = fitness.score(self.agent)
    #if score != 0.5:
    #  print("Shepherd #" + str(self.agent.id) + ": Fitness = " + str(score))