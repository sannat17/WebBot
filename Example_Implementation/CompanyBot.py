"""
The main code for CompanyBot that automates Instagram data interaction.
 (Borrows some features I implemented for an actual business)

Bot can:
  - Track followers and following data
  - Script can write this data to a json file by dates and can be used to track 
  follower retention and data between dates

Shortcomings:
  - cannot recognize users who have changed username (and will show them as 
  unfollowed and new follower)
  - Certain glitches (with pages not loading in expected times) can cause bot
  to fail and needs a programmer's supervision.


Potential:
  - Make it a full fledged bot incorporating my other projects. 
  (of automatic Excel and PDF generation, invoice management etc.)

Developed by Sannat Bhasin.
"""

from typing import Dict, List
from selenium import webdriver
import json
import datetime
from time import sleep
import os

full_path = os.path.realpath(__file__)
parent_dir, current_filename = os.path.split(full_path)


class CompanyBot:
    """
    The main class for initiating the CompanyBot object.

    Initializing an instance opens a new chrome window where the various
    class methods carry out automated tasks.
    """

    driver: webdriver
    insta_username: str
    email: str
    insta_open: bool
    gmail_open: bool
    windows: Dict[str, str]

    def __init__(self, insta_username: str, email: str) -> None:
        """Start a chrome session and Initialize the account variables for
         Pioneer Honey.
        """
        self.driver = webdriver.Chrome(executable_path=parent_dir+"\\chromedriver.exe")
        self.insta_username = insta_username
        self.email = email
        self.insta_open = False
        self.gmail_open = False
        self.windows = {}

    def insta_login(self, password: str) -> None:
        """Log into your instagram account."""
        self.driver.execute_script('window.open("https://instagram.com");')
        self.windows["insta"] = self.driver.window_handles[1]

        self.driver.switch_to.window(self.windows["insta"])

        sleep(3)

        self.driver.find_element_by_xpath('//input[@name="username"]').\
            send_keys(self.insta_username)
        self.driver.find_element_by_xpath('//input[@name="password"]'). \
            send_keys(password)
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()

        sleep(3)

        self.driver.find_element_by_xpath(
            "//button[contains(text(), 'Not Now')]").click()
        sleep(1)
        self.driver.find_element_by_xpath(
            "//button[contains(text(), 'Not Now')]").click()
        sleep(1)

        self.insta_open = True

    def _collect_list(self, pause: int):
        """Helper method for self.insta_follower_data."""
        result = []

        # Find the last element currently loaded in the scrollbox
        _list = self.driver.find_element_by_css_selector(
            'div[role=\'dialog\'] ul')
        last_list_element = _list.find_elements_by_css_selector('li')[-1]

        # Scroll to the last element, pause and repeat till no more elements load
        while True:
            self.driver.execute_script('arguments[0].scrollIntoView()',
                                       last_list_element)

            sleep(pause)

            _list = self.driver.find_element_by_css_selector(
                'div[role=\'dialog\'] ul')
            new_last = _list.find_elements_by_css_selector('li')[-1]

            if new_last == last_list_element:
                break

            last_list_element = new_last

        _list = _list.find_elements_by_css_selector('li')

        for element in _list:
            links = element.find_elements_by_css_selector('a')
            name = links[-1].text
            result.append(name)

        return result

    def insta_follower_data(self, pause: int) -> List[List[str]]:
        """Collect the list of followers and following from your instagram profile.

        Note:   <pause> should depend on speed of your internet and
                how fast pages and links load)
        """
        if not self.insta_open:
            msg = "Instagram window is not open. Use insta_login method first"
            raise Exception(msg)

        self.driver.get(f"https://instagram.com/{self.insta_username}")

        sleep(pause)

        self.driver.find_element_by_xpath(
            f"//a[contains(@href, '/{self.insta_username}/followers')]").click()
        sleep(pause)
        followers = self._collect_list(pause)

        close_button = self.driver.find_element_by_xpath(
            '/html/body/div[4]/div/div/div[1]/div/div[2]/button')
        close_button.click()

        sleep(pause)

        self.driver.find_element_by_xpath(
            f"//a[contains(@href, '/{self.insta_username}/following')]").click()
        sleep(pause)
        following = self._collect_list(pause)

        return [followers, following]


# 
# ----- Functions -----
#
def update_followers(input_list: str) -> None:
    """Update followers from <input_list> to followers.json."""
    file_name = parent_dir + "\\followers.json"

    with open(file_name) as data_file:
        data = json.load(data_file)
        date = datetime.date.today()
        date = str(date)

        if date in data:
            data[date]["followers"] = input_list
        else:
            data[date] = {}
            data[date]["followers"] = input_list

    with open(file_name, "w") as out:
        json.dump(data, out, indent=4)


def update_following(input_list: str) -> None:
    """Update followers from <input_list> to followers.json."""
    file_name = parent_dir + "\\followers.json"

    with open(file_name) as data_file:
        data = json.load(data_file)
        date = datetime.date.today()
        date = str(date)

        if date in data:
            data[date]["following"] = input_list
        else:
            data[date] = {}
            data[date]["following"] = input_list

    with open(file_name, "w") as out:
        json.dump(data, out, indent=4)


def track_followers_between_dates(date0=None, date1=None):
    """Track followers between <date0> and <date1>.

    If no input is provided, then take the most recent two dates

    Preconditions: <date0> and <date1> have format "YYYY-MM-DD"
    """
    file_name = parent_dir + "\\followers.json"

    with open(file_name) as data_file:
        data = json.load(data_file)
        dates = list(data.keys())

        if date0 is None:
            date0 = dates[-2]
        if date1 is None:
            date1 = dates[-1]

        # Check if the input dates actually exist in followers.json
        if date0 not in dates or date1 not in dates:
            print("The record for one of the dates you tried is missing.")
            print("Pick from the following dates instead: ")
            for d in dates:
                print("    " + d)

            return None

        # Continue with main code if the dates exist in followers.json
        unfollowers = [i for i in data[date0]["followers"] if i not in data[date1]["followers"]]
        new_followers = [i for i in data[date1]["followers"] if i not in data[date0]["followers"]]

        # Now comes printing and styling of the found data
        print("\n===================================\n")
        print(f"People who unfollowed you between {date0} and {date1}: ")
        for name in unfollowers:
            print("    " + name)

        print("\n===================================\n")

        print(f"Your new followers {date0} and {date1}: ")
        for name in new_followers:
            print("    " + name)

        return [unfollowers, new_followers]


if __name__ == "__main__":

    # -- Run the main script here --

    bot = CompanyBot("<insta_username>", "<email>")
    bot.insta_login("<insta_password>")
    followers, following = bot.insta_follower_data(3)

    print("Don't follow you back: ", [i for i in followers if i not in following])
    
    update_followers(followers)
    update_following(following)

    # track_followers_between_dates(date0="YYYY-MM-DD", date1="YYYY-MM-DD")
