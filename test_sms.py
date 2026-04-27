import os
from dotenv import load_dotenv

load_dotenv()

import utils

print("Testing Africa's Talking API for +254798498664 ...")
utils.send_alert('+254798498664', 'Manual SMS Test System Verification')
