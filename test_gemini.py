import os
from dotenv import load_dotenv

load_dotenv()

class DummyItem:
    def __init__(self, title, description, location, date_lost, category):
        self.title = title
        self.description = description
        self.location = location
        self.date_lost = date_lost
        self.category = category

import utils

lost = DummyItem("iPhone 13", "Blue case, slight scratch on screen", "Library", "2023-10-01", "Electronics")
found = DummyItem("Apple Phone", "Blue cover, has a scratch", "Library 2nd floor", "2023-10-02", "Electronics")

print("Evaluating match...")
is_match = utils.evaluate_match_with_ai(lost, found)
print(f"Is match? {is_match}")
