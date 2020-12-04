"""
The main code for the bot object to use for web task automation.
"""

from typing import Dict, List

from info import chromedriver_location
import os
from selenium import webdriver
from time import sleep

full_path = os.path.realpath(__file__)
parent_dir, current_filename = os.path.split(full_path)

class WebBot:
    """
    Main parent class to define a WebBot.
    """
    driver: webdriver
    windows: Dict[str, str]

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=parent_dir + "\\chromedriver.exe")
        self.windows = {}
    
    # more user specific functions go here

if __name__ == "__main__":
    bot = WebBot()
    #Task script of what to do with the WebBot goes here
