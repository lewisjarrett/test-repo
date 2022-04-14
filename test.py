import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import pandas as pd

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get(
    'https://www.o2.co.uk/shop/tariff/apple/iphone-13?productId=fefe3c9c-46fd-403c-a788-d7f58c1c4ff5&contractType=paymonthly')
# driver.fullscreen_window()

def get_info():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'capacity')))
    data_temp = driver.find_elements_by_class_name('capacity')
    datas = [data.text for data in data_temp]

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'section-summary-content')))
    name = driver.find_element_by_class_name('section-summary-content').text
    names = [name] * len(datas)

    int_costs = driver.find_elements_by_class_name('total-cost-price-int')
    dec_costs = driver.find_elements_by_class_name('total-cost-price-decimal')

    final_costs = []

    for num, dec in zip(int_costs, dec_costs):
        p = f'{num.text}{dec.text[:2]}'
        price = float(p.strip('£'))
        final_costs.append(price)

    up_costs = final_costs[::2]
    month_costs = final_costs[1::2]

    contract_lens = []

    lengths_temp = driver.find_elements_by_class_name('data-limit')
    for length in lengths_temp:
        contract_lens.append(length.text[:2])

    all_info = list(zip(names, datas, up_costs, month_costs, contract_lens))
    return all_info


def get_info_custom(phone_name, current_capacity, contract_length):
    month = driver.find_element_by_class_name('monthlyContainer').text
    month = float(month.strip('\n').replace('£', '').replace('MONTHLY', '').replace('*', ''))

    up_front = driver.find_element_by_class_name('upFrontContainer').text
    up_front = float(up_front.replace('£', '').replace('UPFRONT', ''))

    new_info = [phone_name, current_capacity, up_front, month, contract_length]

    return new_info


def custom_page():
    ALL_CUSTOM_INFO = []
    requested_month = ['24']
    contract_len = []
    name = driver.find_element_by_class_name('section-summary-content').text
    # DECREASING MONTHS BUTTON
    while requested_month:
        try:
            driver.find_element_by_xpath('//*[@id="ni_imp_prim_accept"]').click()
            driver.find_element_by_class_name('tooltip-wrapper leftAlignTooltip').click()

        except selenium.common.exceptions.NoSuchElementException:
            pass
        except selenium.common.exceptions.ElementNotInteractableException:
            pass

        finally:
            current_month = driver.find_element_by_xpath(
                '/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div[2]/div/div['
                '2]/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div['
                '1]/div/div/div/div[1]/div/div[3]/div[2]/p[1]').text
            if current_month in requested_month:
                requested_month.remove(current_month)
                contract_len.append(int(current_month))
                # print('month found - adding info')
                break

            else:
                try:
                    button = driver.find_element_by_xpath(
                        '/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div['
                        '2]/div/div[2]/div/div/div[4]/div/div/div[1]/div/div/div/div[1]/div/div[3]/div['
                        '1]/div/button')
                    button.click()
                except selenium.common.exceptions.ElementClickInterceptedException:
                    time.sleep(3.5)
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.ESCAPE).perform()
                    button = driver.find_element_by_xpath(
                        '/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div['
                        '2]/div/div[2]/div/div/div[4]/div/div/div[1]/div/div/div/div[1]/div/div[3]/div['
                        '1]/div/button')
                    button.click()

    ALL_CAPACITIES = []

    # INCREASING CAPACITY BUTTON
    cap_max = driver.find_element_by_xpath('/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div[2]/div/div['
                                           '2]/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div[1]/div/div/div/div['
                                           '1]/div/div[4]/div[3]/div/p').text

    test = []
    while not test:
        current_cap = driver.find_element_by_xpath('/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div[2]/div/div['
                                                   '2]/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div['
                                                   '1]/div/div/div/div[1]/div/div[4]/div[2]/p[1]').text
        if current_cap in ALL_CAPACITIES:
            # print(f'**INFORMATION FOR {current_cap} HAS ALREADY BEEN PROCESSED')
            pass
        else:
            custom_info = get_info_custom(name, current_cap, contract_len[0])
            ALL_CUSTOM_INFO.append(custom_info)
            # print(f'processing information for {current_cap}')
            ALL_CAPACITIES.append(current_cap)

        if current_cap in cap_max:
            # print('reached limit - must go back now')
            test.append(current_cap)

        else:
            increase_button = driver.find_element_by_xpath(
                '/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div[2]/div/div['
                '2]/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div['
                '1]/div/div/div/div[1]/div/div[4]/div[3]/div/button')
            increase_button.click()

    # DECREASING CAPACITY BUTTON
    cap_min = driver.find_element_by_xpath(
        '/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div/div['
        '4]/div/div/div[1]/div/div/div/div[1]/div/div[4]/div[1]/div/p').text
    test_2 = []

    while not test_2:
        current_cap = driver.find_element_by_xpath('/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div[2]/div/div['
                                                   '2]/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div['
                                                   '1]/div/div/div/div[1]/div/div[4]/div[2]/p[1]').text
        if current_cap in ALL_CAPACITIES:
            # print(f'**INFORMATION FOR {current_cap} HAS ALREADY BEEN PROCESSED')
            pass
        else:
            custom_info = get_info_custom(name, current_cap, contract_len[0])
            ALL_CUSTOM_INFO.append(custom_info)
            # print(f'processing information for {current_cap}')
            ALL_CAPACITIES.append(current_cap)
        if current_cap in cap_min:
            # print('lower cap reached')
            test_2.append(current_cap)

        else:
            decrease_button = driver.find_element_by_xpath('/html/body/div[4]/div[3]/div[1]/div/div[2]/div/div['
                                                           '2]/div/div[2]/div/div/div[2]/div/div[2]/div/div/div['
                                                           '4]/div/div/div[1]/div/div/div/div[1]/div/div[4]/div['
                                                           '1]/div/button')
            decrease_button.click()

    return ALL_CUSTOM_INFO


def process_2():
    time.sleep(1)
    driver.find_element_by_class_name('edit-text').click()
    time.sleep(2)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'second-offer-dd')))
    driver.find_element_by_class_name('second-offer-dd').click()
    capacity_elements = driver.find_elements_by_class_name('dp-list-color')

    FINAL_CAPACITY = []
    for x in capacity_elements:
        if x.text:
            FINAL_CAPACITY.append(x.text)

    actions = ActionChains(driver)
    for i in range(len(FINAL_CAPACITY)):  # SEND RIGHT TO THE TOP OF DROPDOWN
        actions.send_keys(Keys.ARROW_UP).perform()
        time.sleep(0.5)
    time.sleep(1)
    actions.send_keys(Keys.ENTER).perform()

    final_information = []
    current_check = []
    for i in range(len(FINAL_CAPACITY)):
        if i == 0:
            driver.find_element_by_class_name('tne-primary').click()
            time.sleep(1)
            # CHECK CURRENT CAPACITY OF PHONE
            cap_check = driver.find_element_by_class_name('section-summary-content').text[-5:].replace(' ', '').replace(
                '|', '')
            if not bool(cap_check in current_check):
                current_check.append(cap_check)
                info_list = get_info()
                final_information.append(info_list)
                print(f'processing {cap_check} iPhone information')
                time.sleep(1)
                driver.find_element_by_class_name('edit-plan').click()
                time.sleep(1)
                custom_info = custom_page()
                final_information.append(custom_info)
                time.sleep(1)
                driver.find_element_by_class_name('edit-text').click()
                time.sleep(2)
                driver.find_element_by_class_name('second-offer-dd').click()
            else:
                # IF DATA HAS ALREADY BEEN ADDED TO FILE
                print('data already added')
                time.sleep(2)
                driver.find_element_by_class_name('edit-text').click()

        # START SCROLLING DOWN DROP DOWN MENU
        else:
            actions = ActionChains(driver)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(1)
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(1.5)
            driver.find_element_by_class_name('tne-primary').click()
            time.sleep(1)
            cap_check = driver.find_element_by_class_name('section-summary-content').text[-5:].replace(' ', '').replace(
                '|', '')
            if not bool(cap_check in current_check):
                current_check.append(cap_check)
                info_list = get_info()
                final_information.append(info_list)
                print(f'processing {cap_check} iPhone information')
                time.sleep(1)
                driver.find_element_by_class_name('edit-plan').click()
                time.sleep(1)
                custom_info = custom_page()
                final_information.append(custom_info)
                time.sleep(1)
                driver.find_element_by_class_name('edit-text').click()
                time.sleep(2)
                driver.find_element_by_class_name('second-offer-dd').click()

            else:
                print('data already added')
                time.sleep(2)
                driver.find_element_by_class_name('edit-text').click()

    return final_information


def create_csv(information):
    headers = ['Phone Name', 'Data', 'RRP', 'MRC', 'No. of Months']
    flat_list = [item for sublist in information for item in sublist]

    with open('phone_data.csv', 'a') as phone_data:
        wr = csv.writer(phone_data)
        wr.writerows(flat_list)

    df = pd.read_csv("phone_data.csv", header=None, names=headers, index_col=None)
    new = df['No. of Months'] * df['MRC'] + df['RRP']
    df['Total Cost'] = new
    df.to_csv("phone_data.csv")


time.sleep(2)
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'close-icon')))
driver.find_element_by_class_name('close-icon').click()
time.sleep(1)
phone_info = process_2()
create_csv(phone_info)
