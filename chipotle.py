"""
This is a web scraper for Chipotle Restaurants 
"""

# Importing required modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import csv
import os

# Setting options for Chrome Webdriver
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("−−lang=en-US")
driver = webdriver.Chrome(chrome_options)
driver.maximize_window()

driver.get("https://chipotle.com/order/build/burrito")

wait = WebDriverWait(driver, 30) # Sets a wait time for driver before throwing an exception
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'text-input-container'))) # Waits till the element with specified class name appears on the page

# Search for the given address
address_search = driver.find_element(By.CLASS_NAME, 'text-input-container') # Finding an element with provided class name
address_search.click()

# Enter the search keyword and click search 
address_search_input = address_search.find_element(By.TAG_NAME, 'input') # Finds the input box in the form
address_search_input.send_keys("Austin, TX 78750, USA") # Enters the keyword for search
wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="result-item-0"]'))) # Wait until the search results load

# Clicking on the address result
address_result = driver.find_element(By.XPATH, '//*[@id="result-item-0"]') # Finds element using Xpath 
address_result.click()

# Selecting a nearby restaurant
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'restaurant-address')))
near_address_result = driver.find_elements(By.CLASS_NAME, 'restaurant-address')
near_address_result[0].click()

# Selecting a pickup slot
pickup_detail = driver.find_element(By.CLASS_NAME, 'details-view')
pickup_button = pickup_detail.find_elements(By.CLASS_NAME, 'slot-wrapper')
pickup_button[0].click()
time.sleep(1)

# List containing the name of foods and URLs
url_data_list = [
    ['BURRITO', 'https://chipotle.com/order/build/burrito'],
    ['BURRITO-BOWL', 'https://chipotle.com/order/build/burrito-bowl'],
    ['LIFESTYLE BOWL', 'https://chipotle.com/order/build/lifestyle-bowl'],
    ['QUESADILLA', 'https://chipotle.com/order/build/quesadilla'],
    ['SALAD', 'https://chipotle.com/order/build/salad'],
    ['TACOS', 'https://chipotle.com/order/build/tacos'],
    ['SIDES & DRINKS','https://chipotle.com/order/build/sides-&-drinks'],
    ["KID'S BUILD YOUR OWN","https://chipotle.com/order/build/kid's-build-your-own"],
    ["KID'S QUESADILLA", "https://chipotle.com/order/build/kid's-quesadilla"]
]

# Loops through url_data_list, with each pass providing index number and the actual url_data
for index, url_data in enumerate(url_data_list):
    
    # Initialize a list to store output data
    output_data = []
    
    # Wait until the specified content is detected on the page
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="cmg-app-content"]/div[1]/div/div/div[1]/div[1]/div')))
    
    # Navigate to each URL present in url_data_list
    driver.get(url_data[1])

    # Get HTML content of the page
    html = driver.page_source
    
    # Convert HTML to BeautifulSoup object for parsing
    soup = BeautifulSoup(html, 'html.parser')

    # Special case when index is 2, scraping different details
    if (index == 2):

        # Adding the title of food group to output data
        output_data.append(['Title', url_data[0]])

        # Find the text strings of each meal name and price
        card_names = soup.find_all('div', class_='meal-name')
        card_cost = soup.find_all('span', class_='meal-price')

        # Check if there is a cost for each card, and add each to output data
        if len(card_names) == len(card_cost):
            for ca_index, card_item in enumerate(card_names):
                output_data.append([card_item.get_text(), card_cost[ca_index].get_text()])

    # Main case, when index is not 2
    else:

        # Adding the title of food group to output data and an empty string for consistency
        output_data.append(['Title', url_data[0], ''])

        # Identify all categories of food items using their shared class name and loop through each one
        card_sections = soup.find_all('div', class_='item-category')

        # Iterating over all the card sections
        for ca_index, card_section in enumerate(card_sections):

            # For each food category, find all food items
            card_items = card_section.find_all('div', class_='cards')

            # Find the title associated with the section
            card_header = card_section.select(f"div > div > div.title-container > div.title")

            # Add the title of food group to output data with title 'Category'
            output_data.append(['Category', card_header[0].get_text(), ''])

            # Loop through the items, adding each food item's name and cost to output data
            for it_index, item in enumerate(card_items[0]):
                try:
                    header = item.select(f"div.card > div.item-details > div.item-name-container > div.item-name")
                    cost = item.select("div.card > div.item-details > div.cost-and-calories > div.item-cost")

                    if len(cost) == 0:
                        continue
                    output_data.append(['', header[0].get_text(), cost[0].get_text()])

                except Exception as e:
                    # Move on to the next item or category if an error occurs during the process
                    continue

    # Determine the directory where files will be saved
    directory = os.getcwd()

    # Collect the path for the file that the output data will be written to
    filename = os.path.join(directory, f"{url_data[0]}.csv")

    # Open the file with permissions to write, and specify formatting details
    with open(filename, 'w', newline='', encoding='utf-8') as file:

        # Create a writing object
        writer = csv.writer(file)

        # Write output data to the CSV file
        writer.writerows(output_data)