import csv
import multiprocessing
import os
from selenium.webdriver import Chrome
from time import sleep, time


ZIPCODE_URL = "https://www.zipcodestogo.com"
REP_URL = "https://www.house.gov/representatives/find-your-representative"
CHROME_DRIVER_PATH = os.getcwd() + '/driver/chromedriver'
OUTPUT_CSV_DATA_PATH = os.getcwd() + '/data/zipcode_data.csv'
NUM_CPUS = multiprocessing.cpu_count()
STATE_NAMES = [
    "Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado",
    "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii",
    "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana",
    "Massachusetts", "Maryland", "Maine",  "Michigan", "Minnesota", "Missouri", "Mississippi",
    "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico",
    "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia",
    "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"
]
TOTAL_STATES = len(STATE_NAMES)


def persist_info_to_csv(shared_state_rep_map):
    """Persist the gathered information to a CSV file"""
    with open(OUTPUT_CSV_DATA_PATH, 'w', newline='') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(("Zip Code", "City", "State", "Representative"))
        for state in STATE_NAMES:
            for index, state_zipcode_data in enumerate(shared_state_rep_map[state]):
                if len(state_zipcode_data) == 4:
                    print('(persist_info_to_csv) state_zipcode_data:',
                          state_zipcode_data)
                    row_tuple = (
                        state_zipcode_data[0], state_zipcode_data[1], state_zipcode_data[2], state_zipcode_data[3].strip())
                    csv_out.writerow(row_tuple)


def gather_zip_codes(start_end_tuple):
    """Scrape web for U.S. Zip Codes"""
    print(f"Process {os.getpid()}: ***gather_zip_codes***")
    start = start_end_tuple[0]
    end = start_end_tuple[1]
    shared_state_zipcode_data_map = start_end_tuple[2]
    sns = STATE_NAMES[start:end]
    browser = Chrome(executable_path=CHROME_DRIVER_PATH)
    for state in sns:
        print(f"Process {os.getpid()}: State: {state}")
        url = ZIPCODE_URL + f"/{state}/"
        browser.get(url)
        sleep(2.5)
        zipcode_anchor_tags = browser.find_elements_by_css_selector(
            '.inner_table > tbody > tr > td > a')
        buffer_pair_data = []
        for anchor_tag in zipcode_anchor_tags:
            if anchor_tag.text == "View Map":
                continue
            # print("anchor_tag.text:", anchor_tag.text)
            if len(buffer_pair_data) == 2:
                buffer_pair_data.append(state)
                shared_state_zipcode_data_map[state].append(
                    list(buffer_pair_data))
                buffer_pair_data = []
                # Remove when not debugging
                # break
            buffer_pair_data.append(anchor_tag.text)
        if len(buffer_pair_data) == 2:
            buffer_pair_data.append(state)
            shared_state_zipcode_data_map[state].append(list(buffer_pair_data))
        # Remove when not debugging
        # break
        print(
            f"Process {os.getpid()}: The total # of gathered zip codes for {state}: {len(shared_state_zipcode_data_map[state])}")
    print("DONE")
    browser.close()


def map_zc_to_rep(start_end_tuple):
    """Map Zip Codes to U.S. Representatives"""
    print(f"Process {os.getpid()}: ***map_zc_to_rep***")
    start = start_end_tuple[0]
    end = start_end_tuple[1]
    shared_state_zipcode_data_map = start_end_tuple[2]
    sns = STATE_NAMES[start:end]
    browser = Chrome(executable_path=CHROME_DRIVER_PATH)
    print(f"Process {os.getpid()}: States to evaluate: {sns}")
    for state in sns:
        print(f"Process {os.getpid()}: State: {state}")
        if len(shared_state_zipcode_data_map[state]) != 0:
            for index, zip_code_city_pair in enumerate(shared_state_zipcode_data_map[state]):
                zip_code = zip_code_city_pair[0]
                browser.get(REP_URL)
                sleep(2.5)
                find_rep_input_field = browser.find_elements_by_css_selector(
                    '#Find_Rep_by_Zipcode')
                find_rep_input_field[0].send_keys(zip_code)
                find_rep_button = browser.find_elements_by_css_selector(
                    '.btn-success')
                find_rep_button[0].click()
                sleep(2.5)
                rep_page_anchor_tags = browser.find_elements_by_css_selector(
                    '.rep > a')
                reps = ""
                for anchor_tag in rep_page_anchor_tags:
                    if anchor_tag.text == '':
                        continue
                    print(
                        f"Process {os.getpid()} Representative: {anchor_tag.text}")
                    reps += anchor_tag.text + ", "
                    # Remove when not debugging
                    # break
                zip_code_city_pair.append(reps)
                shared_state_zipcode_data_map[state][index] = zip_code_city_pair
                # Remove when not debugging
                # break
    print("DONE")
    browser.close()


with multiprocessing.Manager() as manager:
    processes = []
    offset = 0
    shared_state_rep_map = manager.dict()
    for cpu in range(NUM_CPUS):
        total_states_limit = (int(TOTAL_STATES/8) + 1) + offset
        print("gather_zip_codes ==> offset, total_states_limit, states:",
              offset, total_states_limit, STATE_NAMES[offset:total_states_limit])
        for state in STATE_NAMES[offset:total_states_limit]:
            shared_state_rep_map[state] = manager.list()
        processes.append(
            multiprocessing.Process(target=gather_zip_codes, args=(
                (offset, total_states_limit, shared_state_rep_map),)))
        offset = total_states_limit

    start_time = time()
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    print("Parallel gather_zip_codes() op time--- %.2f seconds ---" %
          (time() - start_time))

    processes.clear()
    offset = 0
    for cpu in range(NUM_CPUS):
        total_states_limit = (int(TOTAL_STATES/8) + 1) + offset
        print("map_zc_to_rep ==> offset, total_states_limit:",
              offset, total_states_limit)
        processes.append(
            multiprocessing.Process(target=map_zc_to_rep, args=(
                (offset, total_states_limit, shared_state_rep_map),)))
        offset = total_states_limit

    start_time = time()
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    print("Parallel map_zc_to_rep() op time--- %.2f seconds ---" %
          (time() - start_time))

    start_time = time()
    persist_info_to_csv(shared_state_rep_map)
    print("Serial persist_info_to_csv() op time--- %.2f seconds ---" %
          (time() - start_time))
