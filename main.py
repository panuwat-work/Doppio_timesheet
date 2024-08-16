import datetime
import json
import requests
from lxml import html

with open('projectId.json') as file:
    data = json.load(file)

with open('th_holiday.json') as file:
    holiday_data = json.load(file)

with open('credential.json') as file:
    credential_data = json.load(file)

project_id = credential_data["project_id"]

for obj in data['data']:
    if obj['id'] == 59:
        project_name = obj['name']
        break

url = 'https://backend.humanos.biz/Admin/EnhanceLeaveListUI.aspx?MenuID=318'
headers = {
    'cookie': f'ASP.NET_SessionId={credential_data["humanos_session_token"]}; DetectLoginHMOS=LoginUI=LoginUI',
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
    headers = {
        'token': credential_data['doppio_session_token'],
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