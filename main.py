import csv
from time import sleep
from os import getcwd
from selenium.webdriver import Chrome

state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]
zipcode_url = "https://www.zipcodestogo.com"
rep_url="https://www.house.gov/representatives/find-your-representative"
chrome_driver_path = getcwd() + '/driver/chromedriver'
csv_path = getcwd() + '/data/zipcode_data.csv'

browser = Chrome(executable_path=chrome_driver_path)
state_zipcode_data_map = {}


def persist_info_to_csv():
    with open(csv_path,'w', newline='') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(("Zipcode", "City", "Representative"))
        for state in state_names:
            for state_zipcode_data in state_zipcode_data_map[state]:
                row_tuple = (state_zipcode_data[0], state_zipcode_data[1], state_zipcode_data[2].strip())
                csv_out.writerow(row_tuple)


# Scrape web for all U.S. zipcodes
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
    print("state_zipcode_data_map[state]:", state_zipcode_data_map[state])
    if len(state_zipcode_data_map[state]) != 0:
        for zip_code_city_pair in state_zipcode_data_map[state]:
            print("zip_code_city_pair:", zip_code_city_pair)
            zip_code = zip_code_city_pair[0]
            print("zip_code:", zip_code)
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
                print("Representative:", anchor_tag.text)
                if anchor_tag.text == '':
                    continue
                reps += anchor_tag.text + ", "
                # Remove when not debugging
                # break
            zip_code_city_pair.append(reps)
            print("zip_code_city_pair:", zip_code_city_pair)
            # Remove when not debugging
            # break

print("DONE")

browser.close()

persist_info_to_csv()
