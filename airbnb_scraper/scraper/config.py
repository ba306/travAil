
from datetime import datetime

# Configuration settings (could also be loaded dynamically if needed)
START_DATE = "2025-03-19"
END_DATE = "2025-03-26"

# Convert date strings to datetime objects
start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
end_date = datetime.strptime(END_DATE, "%Y-%m-%d")


NUMBER_OF_ADULTS = 1
MAX_PRICE = 80
NE_LAT = 27.769176892555794
NE_LNG = -15.562498809278736
SW_LAT = 27.740574440423774
SW_LNG = -15.589469845163336
