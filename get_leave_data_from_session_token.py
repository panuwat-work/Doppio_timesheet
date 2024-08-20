import datetime
import json
import requests
from lxml import html
import base64

with open('projectId.json') as file:
    data = json.load(file)

with open('th_holiday.json') as file:
    holiday_data = json.load(file)

with open('credential.json') as file:
    credential_data = json.load(file)

project_id = credential_data["project_id"]

for obj in data['data']:
    if obj['id'] == project_id:
        project_name = obj['name']
        break
    elif str(obj['id']) == project_id:
        project_name = obj['name']
        break  

url = 'https://backend.humanos.biz/LoginUI.aspx'
headers = {
    'accept': '*/*',
    'accept-language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh;q=0.5',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://backend.humanos.biz',
    'priority': 'u=1, i',
    'referer': 'https://backend.humanos.biz/LoginUI.aspx',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-microsoftajax': 'Delta=true',
    'x-requested-with': 'XMLHttpRequest'
}

data = {
    '__EVENTTARGET': 'ctl00$body$btnSubmit',
    '__VIEWSTATE': 'Qy2uW17VyGDu/8CYIjArIhvjoCplkUgWsDh28hWiTD0su+soKf1B5XlohbNhMlVX65hjeNTk4B9jnZZCtTXIvxLaahG311nzA11IN8igTMtWACKZLae+bnas2OoR7MykS69trBnBLanJTUJOnIBOjLjGjfCmdbZxKEWw2qNgtTbAtL8ke5d//XgHF9J03Vg0',
    '__EVENTVALIDATION': 'lb/GqK6HroX/DPF7r5iiSjIGW8fCOecupqXJtiTD3Xg3TEh974GWhROs7AnztrVqOs2y8NGfFRjbzdTVt3XlNV79TD9OhZ574LoaY7ga3P7dAgyGjorcEIPh8NjGmrNiVx5iCuyShSY7ewrf9HRjuzAZQfiTMzCa2r93FTgl2cvJOdchnPBmo7a2QhWYe9HEmFo84lVVu8Bj+ndN+q5UOv+GuOmruGiTzjwEDuxdJg/cf4tsCtoBiKWVNpwFK9SVmXl9AX4STZQrlynpW6AMlFqbWJzS+9K40YBBYUOcbag=',
    'ctl00$body$txtUserName': credential_data['doppio_email'],
    'ctl00_body_txtUserName_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"' + credential_data['doppio_email'] + '","valueAsString":"' + credential_data['doppio_email'] + '","lastSetTextBoxValue":"' + credential_data['doppio_email'] + '"}',
    'ctl00$body$txtPassword': credential_data['humanos_password'],
    'ctl00_body_txtPassword_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"' + credential_data['humanos_password'] + '","valueAsString":"' + credential_data['humanos_password'] + '","lastSetTextBoxValue":"' + credential_data['humanos_password'] + '"}',
}

response = requests.post(url, headers=headers, data=data)
set_cookie_header = response.headers.get('Set-Cookie')
if set_cookie_header:
    asp_net_session_id = set_cookie_header.split(';')[0].split('=')[1]
else:
    print("No Set-Cookie header found")

url = 'https://backend.humanos.biz/Admin/EnhanceLeaveListUI.aspx?MenuID=318'
headers = {
    'cookie': f'ASP.NET_SessionId={asp_net_session_id}; DetectLoginHMOS=LoginUI=LoginUI',
}

response = requests.get(url, headers=headers)

tree = html.fromstring(response.content)
name = tree.xpath("//span[@id = 'ctl00_lblUserFullName']")
if name:
    print("Connected HumanOS as", name[0].text)
    leave_date_data = tree.xpath("//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'lblLeaveRange')]")[:5]
    leave_amount_data = tree.xpath("//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'lblAmountDay')]")[:5]
    leave_data = tree.xpath("//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'RowNo')]/parent::td/following-sibling::td[contains(text(), ' / ')]")[:5]

    leave_dict = {}
    for i in range(len(leave_date_data)):
        leave_date = leave_date_data[i].text.split(' ')[0]
        leave_date = leave_date.replace("67", "2024")
        leave_date = datetime.datetime.strptime(leave_date, '%d/%m/%Y').strftime('%d-%m-%Y')
        leave_type = leave_data[i].text
        leave_amount = leave_amount_data[i].text.split(' วัน')[0]
        leave_dict[leave_date] = {
            'leave_type': leave_type,
            'leave_amount': leave_amount
        }

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
            print(f"{date.strftime('%A %d-%m-%Y')} : Public holiday")
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