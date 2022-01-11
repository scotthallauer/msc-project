from pyroborobo import Pyroborobo, Controller
import numpy as np
from configparser import ConfigParser


def principal_value(deg):
    deg_mod = np.mod(deg, 360)
    if deg_mod > 180:
        return deg_mod - 360
    else:
        return deg_mod


def angle_diff(x, y):
    return principal_value(x - y)

def is_robot(id, props):
  return id < props["cMaxRobotNumber"]

def is_cattle(id, props):
  return not is_robot(id, props)

class CattleController(Controller):

    def __init__(self, world_model):
        # It is *mandatory* to call the super constructor before any other operation to
        # link the python object to its C++ counterpart
        Controller.__init__(self, world_model)
        self.rob = Pyroborobo.get()
        self.camera_max_range = 0
        self.repulse_radius = 0
        self.orientation_radius = 0
        self.props = {}
        config = ConfigParser()
        with open("config/cattle.properties") as stream:
          config.read_string("[root]\n" + stream.read())
        self.props["gInitialNumberOfRobots"] = int(config.get("root", "gInitialNumberOfRobots"))
        self.props["cMaxRobotNumber"] = int(config.get("root", "cMaxRobotNumber"))
        self.props["cMaxCattleNumber"] = int(config.get("root", "cMaxCattleNumber"))
        if is_robot(self.get_id(), self.props):
          self.type = "robot"
          self.set_color(*[255, 0, 0])
        else:
          self.type = "cattle"
          self.set_color(*[0, 255, 0])

    def reset(self):
        self.repulse_radius = 0.2
        self.orientation_radius = 0.6

    def step(self):  # step is called at each time step
        if is_robot(self.get_id(), self.props):
          self.set_translation(0.25)  # Let's go forward
        else:
          self.set_translation(1)  # Let's go forward
        self.set_rotation(0)
        camera_dist = self.get_all_distances()
        camera_id = self.get_all_robot_ids()
        camera_angle_rad = self.get_all_sensor_angles()
        camera_angle = camera_angle_rad * 180 / np.pi
        own_orientation = self.absolute_orientation
        for i in np.argsort(camera_dist):  # get the index from the closest to the farthest
            if camera_angle[i] < -270 or camera_angle[i] > 270:
                continue
            else:
                dist = camera_dist[i]
                if dist < self.repulse_radius:
                    if camera_angle[i] != 0:
                        self.set_rotation(-camera_angle_rad[i] / np.pi)
                    else:
                        self.set_rotation(1)
                elif is_cattle(self.get_id(), self.props):
                  if dist < self.orientation_radius and camera_id[i] != -1 and is_cattle(self.get_robot_id_at(i), self.props):
                    orient_angle = self.get_robot_relative_orientation_at(i)
                    self.set_rotation(orient_angle / np.pi)
                  elif dist < self.camera_max_range and camera_id[i] != -1:
                    self.set_rotation(camera_angle_rad[i] / np.pi)
                break  # stop


if __name__ == "__main__":
    rob = Pyroborobo.create("config/cattle.properties",
                            controller_class=CattleController)
    rob.start()
    rob.update(100000)
    rob.close()
