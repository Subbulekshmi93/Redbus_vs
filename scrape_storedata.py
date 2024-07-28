from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import mysql.connector
import re
from mysql.connector import errorcode

driver = webdriver.Chrome()
driver.get('https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile');
time.sleep(10)

route_elements = driver.find_elements(By.XPATH, "//div[@class='route_details']/a")

# Extract href attributes
links = [element.get_attribute('href') for element in route_elements]
# for link in links: 
# print(links[0])
for link in links:
    print("link routes ",link)
    driver.get(link);
    time.sleep(10)
    bus_routelink = driver.find_elements(By.XPATH,"//div[@class='D136_heading']")
    time.sleep(10)
    driver.maximize_window()
    search_buses = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='button']")))
    search_buses.click()
    time.sleep(15)
    scroll=True
    count=0
    print('opened')
    actions = ActionChains(driver)
    while scroll:
        old_page=driver.page_source
        body=driver.find_element(By.TAG_NAME,"body")
        body.send_keys(Keys.ARROW_DOWN)
        time.sleep(5)
        actions.key_down(Keys.CONTROL).send_keys(Keys.END).key_up(Keys.CONTROL).perform()  
        time.sleep(2)
        new_page=driver.page_source
        print(count)
        count = count +1
        if new_page == old_page:
            scroll=False
            print('condition') 
    time.sleep(2)
    busnames=driver.find_elements(By.XPATH,"//div[@class='travels lh-24 f-bold d-color']")
    arriving_times=driver.find_elements(By.XPATH,"//div[@class='dp-time f-19 d-color f-bold']")
    departure_times=driver.find_elements(By.XPATH,"//div[@class='bp-time f-19 d-color disp-Inline']")
    time_durations=driver.find_elements(By.XPATH,"//div[@class='dur l-color lh-24']")
    prices = driver.find_elements(By.XPATH,"//div[@class='fare d-block']")
    seats_available = driver.find_elements(By.XPATH,"//div[@class='column-eight w-15 fl']")
    bus_types = driver.find_elements(By.XPATH, "//div[@class='bus-type f-12 m-top-16 l-color evBus']")
    ratings = driver.find_elements(By.XPATH, "//div[@class='column-six p-right-10 w-10 fl']")
    print('busname' ,len(busnames))
    print('arriving_time' ,len(arriving_times))
    print('departure_time' ,len(departure_times))
    print('time_duration' ,len(time_durations))
    print('price' ,len(prices))
    print('seat_available' ,len(seats_available))
    print('bus_type' ,len(bus_types))
    print('rating' ,len(ratings))
    min_length = min(len(busnames),len(arriving_times), len(departure_times), len(time_durations),len(prices), len(seats_available), len(bus_types), len(ratings))
    count=0
    buses = []
    for i in range(min_length):
        bus = {
            #'government_bus' : government_bus[i].text,
            'busname' : busnames[i].text, 
            'arriving_time': arriving_times[i].text,
            'departure_time': departure_times[i].text,
            'time_duration': time_durations[i].text,
            'bus_routelink' : bus_routelink[0].text,
            'price' : prices[i].text,
            'seat_available' : seats_available[i].text,
            'bus_type' : bus_types[i].text,
            'rating' : ratings[i].text ,
            }
        buses.append(bus)
    for bus in buses:
        print(bus)
        
    db_config = {
        'user': 'yourusername',  
        'password': 'yourpassword',  
        'host': '127.0.0.1',  
    }
    def preprocess_price(price_str):
        return float(price_str.replace('INR ', ''))
    def extract_seat_count(seat_str):
        match = re.search(r'\d{1,3}', seat_str)
        if match:
            return int(match.group(0))
        else:
            return 0  
    def preprocess_rating(rating_str):
        match = re.search(r'\d+(\.\d+)', rating_str)
        if match:
            return float(match.group(0))
        else:
            return 0        
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS  redbus_p2")
        cursor.execute("USE redbus_P2")
        conn.database = 'redbus_p2'
        cursor.execute('''CREATE TABLE IF NOT EXISTS redbus_p2.bus_routes(
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            busname VARCHAR(80) NULL,
            arriving_time TIME NULL,
            departure_time TIME NULL,
            time_duration  VARCHAR(20) NULL DEFAULT NULL,
            bus_routelink VARCHAR(100) NULL,
            price FLOAT NULL,
            seat_available INT NULL,
            bus_type VARCHAR(80) NULL,
            rating FLOAT NULL);
            ''')
        insert_query = '''
            INSERT INTO bus_routes (
                busname, arriving_time, departure_time, time_duration, bus_routelink, price, seat_available, bus_type, rating
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        bus_routes_data = [
            ( 
                bus['busname'],
                bus['arriving_time'],
                bus['departure_time'],
                bus['time_duration'],
                bus['bus_routelink'],
                preprocess_price(bus['price']),
                extract_seat_count(bus['seat_available']),
                bus['bus_type'],
                preprocess_rating(bus['rating'])  #if bus['rating'] is not None else '0'

            ) 
        for bus in buses
        ]
        
        cursor.executemany(insert_query, bus_routes_data)
        conn.commit() 
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database already exists")
        else:
            print(err)
    finally:
            cursor.close()
            conn.close()
driver.quit()
         
