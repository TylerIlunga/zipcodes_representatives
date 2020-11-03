import csv
import os
from time import sleep
from os import getcwd
from selenium.webdriver import Chrome
import multiprocessing

NUM_CPUS = multiprocessing.cpu_count()
state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]
total_states = len(state_names)
# TESTING:
# state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut"]
# total_states = len(state_names)
zipcode_url = "https://www.zipcodestogo.com"
rep_url="https://www.house.gov/representatives/find-your-representative"
chrome_driver_path = getcwd() + '/driver/chromedriver'
csv_path = getcwd() + '/data/zipcode_data.csv'

def persist_info_to_csv(shared_state_rep_map):
    with open(csv_path,'w', newline='') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(("Zipcode", "City", "Representative"))
        for state in state_names:
            state_zipcode_data = shared_state_rep_map[state]
            print("(persist_info_to_csv) state:", state, state_zipcode_data)
            if len(state_zipcode_data) == 3:
                print('(persist_info_to_csv) state_zipcode_data:', state_zipcode_data)
                row_tuple = (state_zipcode_data[0], state_zipcode_data[1], state_zipcode_data[2].strip())
                csv_out.writerow(row_tuple)


# Scrape web for all U.S. zipcodes
def gather_zip_codes():
    state_zipcode_data_map = {}
    browser = Chrome(executable_path=chrome_driver_path)
    for state in state_names:
        url = zipcode_url + f"/{state}/"
        state_zipcode_data_map[state] = []
        browser.get(url)
        sleep(2)
        zipcode_anchor_tags = browser.find_elements_by_css_selector('.inner_table > tbody > tr > td > a')
        buffer_pair_data = []
        for anchor_tag in zipcode_anchor_tags:
            print("anchor_tag.text:", anchor_tag.text)
            if anchor_tag.text == "View Map":
                continue
            if len(buffer_pair_data) == 2:
                print("RESET:", buffer_pair_data)
                state_zipcode_data_map[state].append(list(buffer_pair_data))
                buffer_pair_data = []
                # Remove when not debugging
                # break
            buffer_pair_data.append(anchor_tag.text)
        if len(buffer_pair_data) == 2:
             print("SPECIAL CASE RESET:", buffer_pair_data)
             state_zipcode_data_map[state].append(list(buffer_pair_data))
        # Remove when not debugging
        # break
    print("DONE")
    browser.close()
    return state_zipcode_data_map

# Map ZipCode to U.S. Representatives
def map_zc_to_rep(start_end_tuple):
    start = start_end_tuple[0]
    end = start_end_tuple[1]
    shared_state_zipcode_data_map = start_end_tuple[2]
    print("process data separation (start, end):", start, end)
    sns = state_names[start:end]
    browser = Chrome(executable_path=chrome_driver_path)
    for state in sns:
        print(f"Process {os.getpid()} state, shared_state_zipcode_data_map[state]: {state}, {shared_state_zipcode_data_map[state]}")
        if len(state_zipcode_data_map[state]) != 0:
            for zip_code_city_pair in shared_state_zipcode_data_map[state]:
                print(f"Process {os.getpid()} zip_code_city_pair: {zip_code_city_pair}")
                zip_code = zip_code_city_pair[0]
                print(f"Process {os.getpid()} zip_code: {zip_code}")
                browser.get(rep_url)
                sleep(2)
                find_rep_input_field = browser.find_elements_by_css_selector('#Find_Rep_by_Zipcode')
                find_rep_input_field[0].send_keys(zip_code)
                find_rep_button = browser.find_elements_by_css_selector('.btn-success')
                find_rep_button[0].click()
                sleep(2)
                # Rep Page
                rep_page_anchor_tags = browser.find_elements_by_css_selector('.rep > a')
                reps = ""
                for anchor_tag in rep_page_anchor_tags:
                    print(f"Process {os.getpid()} Representative: {anchor_tag.text}")
                    if anchor_tag.text == '':
                        continue
                    reps += anchor_tag.text + ", "
                    # Remove when not debugging
                    # break
                zip_code_city_pair.append(reps)
                shared_state_zipcode_data_map[state] = list(zip_code_city_pair)
                print(f"Process {os.getpid()} shared_state_zipcode_data_map[state]'s new zip_code_city_pair: {shared_state_zipcode_data_map[state]}")
                # Remove when not debugging
                # break
    print("DONE")
    browser.close()

with multiprocessing.Manager() as manager:
    processes = []
    offset = 0
    state_zipcode_data_map = gather_zip_codes()
    shared_state_rep_map = manager.dict()
    for key in state_zipcode_data_map.keys():
        print("key, state_zipcode_data_map[key]:", key, state_zipcode_data_map[key])
        shared_state_rep_map[key] = state_zipcode_data_map[key]

    for cpu in range(NUM_CPUS):
        states_to_process = int(total_states/8) + offset
        print("states_to_process, offset:", states_to_process, offset)
        processes.append(
            multiprocessing.Process(target=map_zc_to_rep, args=((offset, states_to_process, shared_state_rep_map),))
        )
        offset = states_to_process

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    persist_info_to_csv(shared_state_rep_map)
