import logging
import os
from sys import platform
import yaml
import igibson
from igibson.envs.igibson_env import iGibsonEnv
from igibson.render.profiler import Profiler
from igibson.utils.assets_utils import download_assets, download_demo_data
from pynput import keyboard

# Global variable to store the currently pressed keys
pressed_keys = set()

def on_press(key):
    try:
        pressed_keys.add(key.char)
    except AttributeError:
        # Handle special keys here if needed
        pass

def on_release(key):
    try:
        pressed_keys.remove(key.char)
    except KeyError:
        pass

def main(selection="user", headless=False, short_exec=False):
    """
    Creates an iGibson environment from a config file with a turtlebot in Rs (not interactive).
    It steps the environment 100 times with random actions sampled from the action space,
    using the Gym interface, without resetting it during the iterations.
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
    
    # Determine the action space dimension dynamically
    action_space_dimension = env.action_space.shape[0]

    max_iterations = 10 if not short_exec else 1
    
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    env.reset()
    while (1):
        
        
        for i in range(100):
            with Profiler("Environment action step"):
                # Modify the action based on the determined action space dimension
                action = [0.0] * action_space_dimension

                if 'w' in pressed_keys and action_space_dimension > 0:
                    action[0] = 1.0  # Move forward
                elif 's' in pressed_keys and action_space_dimension > 0:
                    action[0] = -1.0  # Move backward

                if 'a' in pressed_keys and action_space_dimension > 2:
                    action[2] = 1.0  # Turn left
                elif 'd' in pressed_keys and action_space_dimension > 2:
                    action[2] = -1.0  # Turn right

                state, reward, done, info = env.step(action)
                if done:
                    print("Episode finished after {} timesteps".format(i + 1))
                    break
    env.close()

    # Stop the listener when done
    listener.stop()
    listener.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
