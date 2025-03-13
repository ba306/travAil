from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up Selenium (make sure you have the right driver for your browser)
options = Options()

'''
# Add the headless argument
options.add_argument("--headless")  # Ensure the browser runs in headless mode
options.add_argument("--disable-gpu")  # Optional: to avoid GPU usage issues
options.add_argument("--no-sandbox")  # Optional: helps avoid some sandbox issues on Linux

options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options) #TODO add general function to open chrome and add arguments
'''

driver = webdriver.Chrome()

# Open your Django app URL
driver.get('http://127.0.0.1:8000')  # Change the URL to your local Django app

# Capture a screenshot
screenshot_path = 'snapshots/app_screenshot.png'
driver.save_screenshot(screenshot_path)

# Close the browser
driver.quit()

print(f'Screenshot saved to {screenshot_path}')
