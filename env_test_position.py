import logging
import os
from sys import platform

import yaml

import igibson
from igibson.envs.igibson_env import iGibsonEnv
from igibson.render.profiler import Profiler
from igibson.utils.assets_utils import download_assets, download_demo_data

def main(selection="user", headless=False, short_exec=False):
    print("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)
    download_assets()
    download_demo_data()
    config_filename = os.path.join(igibson.configs_path, "turtlebot_static_nav.yaml")
    config_data = yaml.load(open(config_filename, "r"), Loader=yaml.FullLoader)
    if platform == "darwin":
        config_data["texture_scale"] = 0.5
    config_data["enable_shadow"] = False
    config_data["enable_pbr"] = False

    env = iGibsonEnv(config_file=config_data, mode="gui_interactive" if not headless else "headless")
    max_iterations = 10 if not short_exec else 1
    for j in range(max_iterations):
        print("Resetting environment")
        env.reset()
        for i in range(100):
            with Profiler("Environment action step"):
                # Get keyboard input
                key_input = input("Enter control command (e.g., w/a/s/d): ")

                # Map keyboard input to control command
                if key_input == 'w':
                    action = [0.0, 1.0]  # Forward motion
                elif key_input == 's':
                    action = [0.0, -1.0]  # Backward motion
                elif key_input == 'a':
                    action = [-1.0, 0.0]  # Left motion
                elif key_input == 'd':
                    action = [1.0, 0.0]  # Right motion
                else:
                    action = [0.0, 0.0]  # No motion

                state, reward, done, info = env.step(action)
                env.render()

                if done:
                    print("Episode finished after {} timesteps".format(i + 1))
                    break

    env.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

