import logging
import os
from sys import platform
import yaml
import igibson
from igibson.envs.igibson_env import iGibsonEnv
from igibson.render.profiler import Profiler
from igibson.utils.assets_utils import download_assets, download_demo_data
import keyboard  # Make sure to install the 'keyboard' library

def main(selection="user", headless=False, short_exec=False):
    """
    Creates an iGibson environment from a config file with a turtlebot in Rs (not interactive).
    It steps the environment 100 times with random actions sampled from the action space,
    using the Gym interface, resetting it 10 times.
    """
    print("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)
    # If they have not been downloaded before, download assets and Rs Gibson (non-interactive) models
    download_assets()
    download_demo_data()
    config_filename = os.path.join(igibson.configs_path, "turtlebot_static_nav.yaml")
    config_data = yaml.load(open(config_filename, "r"), Loader=yaml.FullLoader)
    # Reduce texture scale for Mac.
    if platform == "darwin":
        config_data["texture_scale"] = 0.5

    # Shadows and PBR do not make much sense for a Gibson static mesh
    config_data["enable_shadow"] = False
    config_data["enable_pbr"] = False

    env = iGibsonEnv(config_file=config_data, mode="gui_interactive" if not headless else "headless")
    max_iterations = 10 if not short_exec else 1
    env.reset()
    while (1):
        for i in range(100):
            with Profiler("Environment action step"):
                if keyboard.is_pressed('w'):
                    action = [1.0, 0.0]  # Move forward
                elif keyboard.is_pressed('s'):
                    action = [-1.0, 0.0]  # Move backward
                elif keyboard.is_pressed('a'):
                    action = [0.0, 1.0]  # Turn left
                elif keyboard.is_pressed('d'):
                    action = [0.0, -1.0]  # Turn right
                else:
                    action = [0.0, 0.0]  # No action

                state, reward, done, info = env.step(action)
                if done:
                    print("Episode finished after {} timesteps".format(i + 1))
                    break
    env.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
