import numpy as np
import functions.boid as boid
import functions.categorise as categorise

class CattleController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.set_color(*[0, 255, 0])

  def reset(self):
    pass

  def step(self, fitness):
    self.agent.set_translation(1)  # Let's go forward
    self.agent.set_rotation(0)

    fitness.track(self.agent)

    boid.fly_towards_center(self.agent)
    boid.match_velocity(self.agent)

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
      if camera_wall[sensor_id] and camera_dist[sensor_id] < self.agent.config.get("cWallAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break
      # object is a shepherd
      if categorise.is_shepherd(camera_robot_id[sensor_id], self.agent.config.get("pMaxRobotNumber", "int")) and camera_dist[sensor_id] < self.agent.config.get("cShepherdAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break
      # object is a cattle
      if categorise.is_cattle(camera_robot_id[sensor_id], self.agent.config.get("pMaxRobotNumber", "int")) and camera_dist[sensor_id] < self.agent.config.get("cCattleAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break