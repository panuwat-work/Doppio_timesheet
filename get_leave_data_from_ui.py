import datetime
import json
import requests
from lxml import html
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

PATH = (r"chromedriver")
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=PATH, options=options)

with open('projectId.json') as file:
    data = json.load(file)

with open('th_holiday.json') as file:
    holiday_data = json.load(file)

with open('my_credential.json') as file:
    credential_data = json.load(file)

project_id = credential_data["project_id"]

for obj in data['data']:
    if obj['id'] == project_id:
        project_name = obj['name']
        break
    elif str(obj['id']) == project_id:
        project_name = obj['name']
        break        

print("Connecting to HumanOS...")
driver.get('https://backend.humanos.biz/LoginUI.aspx')
driver.maximize_window()

input_username = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@id = 'ctl00_body_txtUserName']")))
input_username.send_keys(credential_data["doppio_email"])

input_password = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@id = 'ctl00_body_txtPasswordMask']")))
input_password.click()

actions = ActionChains(driver)

password = credential_data["humanos_password"]

for char in password:
    actions.send_keys(char)
actions.perform()

submit = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//a[@id = 'ctl00_body_btnSubmit']")))
submit.click()

name = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//span[@id = 'ctl00_lblUserFullName']"))).text

if name:
    print("Connected HumanOS as", name)
    driver.get('https://backend.humanos.biz/Admin/EnhanceLeaveListUI.aspx?MenuID=318')

    get_leave_date = driver.find_elements(By.XPATH, "//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'lblLeaveRange')]")
    get_leave_amount = driver.find_elements(By.XPATH, "//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'lblAmountDay')]")
    get_leave_reason = driver.find_elements(By.XPATH, "//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'RowNo')]/parent::td/following-sibling::td[contains(text(), ' / ')]")

    leave_date = [element.text for element in get_leave_date[:5]]
    leave_amount = [element.text for element in get_leave_amount[:5]]
    leave_reason = [element.text for element in get_leave_reason[:5]]

    leave_dict = {}
    for i in range(len(leave_date)):
        date = leave_date[i].split(' ')[0]
        date = date.replace("67", "2024")
        date = datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%d-%m-%Y')
        reason = leave_reason[i]
        amount = leave_amount[i].split(' วัน')
        leave_dict[date] = {
            'leave_type': reason,
            'leave_amount': amount[0]
        }

    driver.quit()

    url = 'https://timesheet.doppio-tech.com/api/save_timesheet'
    
    encoded_string = credential_data['doppio_email'] 
    encoded_string = base64.b64encode(encoded_string.encode("utf-8"))
    encode_token = encoded_string.decode("utf-8")

    headers = {
        'token': encode_token,
    }

    current_date = datetime.date.today()

    start_date = current_date - datetime.timedelta(days=current_date.weekday())
    end_date = start_date + datetime.timedelta(days=6)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    for i in range(5):
        date = start_date + datetime.timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        if any(holiday['date']['iso'] == date_str for holiday in holiday_data['response']['holidays']):
            date_str = date.strftime('%d-%m-%Y')
            data = {
                'date': date_str,
                'data': [
                    {
                        'hours': '8',
                        'project_id': '22',
                        'remark': ''
                    }
                ]
            }
            print(f"{date.strftime('%A %d-%m-%Y')} : Holiday")
        elif i < len(leave_dict):
            date_str = date.strftime('%d-%m-%Y')
            if any(leave == date_str for leave in leave_dict):
                if leave_dict[date_str]['leave_type'] == 'ลาป่วย / Sick Leave':
                    if leave_dict[date_str]['leave_amount'] == '1':
                        data = {
                            'date': date_str,
                            'data': [
                                {
                                    'hours': '8',
                                    'project_id': '19',
                                    'remark': ''
                                }
                            ]
                        }
                        print(f"{date.strftime('%A %d-%m-%Y')} : Sick Leave")
                    elif leave_dict[date_str]['leave_amount'] == '0.5':
                        data = {
                            "date": date_str,
                            "data": [
                                {
                                "hours": "4",
                                "project_id": "19",
                                "remark": ""
                                },
                                {
                                "hours": "4",
                                "project_id": project_id,
                                "remark": ""
                                }
                            ]
                        }
                        print(f"{date.strftime('%A %d-%m-%Y')} : Sick leave 0.5 day / {project_name} 0.5 day")
                elif leave_dict[date_str]['leave_type'] == 'ลาพักร้อน / Annual Leave':
                    if leave_dict[date_str]['leave_amount'] == '1':
                        data = {
                            'date': date_str,
                            'data': [
                                {
                                    'hours': '8',
                                    'project_id': '20',
                                    'remark': ''
                                }
                            ]
                        }
                        print(f"{date.strftime('%A %d-%m-%Y')} : Annual Leave")
                    elif leave_dict[date_str]['leave_amount'] == '0.5':
                        data = {
                            "date": date_str,
                            "data": [
                                {
                                "hours": "4",
                                "project_id": "20",
                                "remark": ""
                                },
                                {
                                "hours": "4",
                                "project_id": project_id,
                                "remark": ""
                                }
                            ]
                        }
                        print(f"{date.strftime('%A %d-%m-%Y')} : Annual Leave 0.5 day / {project_name} 0.5 day")
            else:
                data = {
                    'date': date_str,
                    'data': [
                        {
                            'hours': '8',
                            'project_id': project_id,
                            'remark': ''
                        }
                    ]
                }
                print(f"{date.strftime('%A %d-%m-%Y')} : {project_name}")
                
        else:
            date_str = date.strftime('%d-%m-%Y')
            data = {
                'date': date_str,
                'data': [
                    {
                        'hours': '8',
                        'project_id': project_id,
                        'remark': ''
                    }
                ]
            }
            print(f"{date.strftime('%A %d-%m-%Y')} : {project_name}")
        response = requests.post(url, headers=headers, json=data)
else:
    print("Can not connect to HumanOS")