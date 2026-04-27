import os
from dotenv import load_dotenv

load_dotenv()

import utils

print("Testing Africa's Talking API...")
# I will use a dummy number. In Sandbox, if the number is not registered, it should give an error response, but we will see what the API returns.
utils.send_alert('+254711123456', 'Macbook Tracker Test')
