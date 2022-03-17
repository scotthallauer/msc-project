import numpy as np
import functions.categorise as categorise

class ShepherdController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.set_color(*[255, 0, 0])
    self.agent.weights = [np.random.normal(0, 1, (self.nb_inputs(), self.nb_hiddens())),
                          np.random.normal(0, 1, (self.nb_hiddens(), self.nb_outputs()))] 
    self.agent.tot_weights = np.sum([np.prod(layer.shape) for layer in self.agent.weights])

  def nb_inputs(self):
    return (
      1 # bias
      + self.agent.nb_sensors * 3 # sensor inputs
      + 2 # landmark inputs
    )

  def nb_hiddens(self):
    return 10

  def nb_outputs(self):
    return 2 # translation + rotation

  def get_inputs(self):
    dists = self.agent.get_all_distances()
    is_robots = self.agent.get_all_robot_ids() != -1
    is_walls = self.agent.get_all_walls()
    is_objects = self.agent.get_all_objects() != -1

    robots_dist = np.where(is_robots, dists, 1)
    walls_dist = np.where(is_walls, dists, 1)
    objects_dist = np.where(is_objects, dists, 1)

    landmark_dist = self.agent.get_closest_landmark_dist()
    landmark_orient = self.agent.get_closest_landmark_orientation()

    inputs = np.concatenate([[1], robots_dist, walls_dist, objects_dist, [landmark_dist, landmark_orient]])
    assert(len(inputs) == self.nb_inputs())
    return inputs

  def get_flat_weights(self):
    all_layers = []
    for layer in self.weights:
      all_layers.append(layer.reshape(-1))
    flat_layers = np.concatenate(all_layers)
    assert (flat_layers.shape == (self.tot_weights,))
    return flat_layers

  def evaluate_network(inputs, network):
    out = np.concatenate([[1], inputs])
    for elem in network[:-1]:
        out = np.tanh(out @ elem)
    out = out @ network[-1]  # linear output for last layer
    return out

  def reset(self):
    pass

  def step(self):
    self.agent.set_translation(0.25)  # Let's go forward
    self.agent.set_rotation(0)

    camera_dist = self.agent.get_all_distances()
    camera_wall = self.agent.get_all_walls()
    camera_robot_id = self.agent.get_all_robot_ids()
    camera_angle_rad = self.agent.get_all_sensor_angles()
    camera_angle_deg = camera_angle_rad * 180 / np.pi

    for sensor_id in np.argsort(camera_dist): # get the index from the closest to the farthest
      # object is out of range
      if camera_angle_deg[sensor_id] < -270 or camera_angle_deg[sensor_id] > 270:
        continue
      # object is a wall
      if camera_wall[sensor_id] and camera_dist[sensor_id] < self.agent.config.get("sWallAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break
      # object is a shepherd
      if categorise.is_shepherd(camera_robot_id[sensor_id], self.agent.config.get("pMaxRobotNumber", "int")) and camera_dist[sensor_id] < self.agent.config.get("sShepherdAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break
      # object is a cattle
      if categorise.is_cattle(camera_robot_id[sensor_id], self.agent.config.get("pMaxRobotNumber", "int")) and camera_dist[sensor_id] < self.agent.config.get("sCattleAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break