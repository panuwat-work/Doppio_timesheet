import datetime
import json
import requests
from lxml import html

with open('th_holiday.json') as file:
    holiday_data = json.load(file)

with open('credential.json') as file:
    credential_data = json.load(file)

project_id = credential_data["project_id"]

url = 'https://backend.humanos.biz/Admin/EnhanceLeaveListUI.aspx?MenuID=318'
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'connection': 'keep-alive',
    'cookie': f'ASP.NET_SessionId={credential_data["humanos_session_token"]}; DetectLoginHMOS=LoginUI=LoginUI',
    'host': 'backend.humanos.biz',
    'referer': 'https://backend.humanos.biz/Admin/MainUI.aspx?MenuID=100',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
tree = html.fromstring(response.content)
name = tree.xpath("//span[@id = 'ctl00_lblUserFullName']")
if name:
    print("Connected HumanOS as", name[0].text)
else:
    print("Can not connect to HumanOS")

leave_date_data = tree.xpath("//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'lblLeaveRange')]")[:5]
leave_amount_data = tree.xpath("//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'lblAmountDay')]")[:5]
leave_data = tree.xpath("//div[@id='ctl00_body_gridMain']//tbody/tr/td/span[contains(@id, 'RowNo')]/parent::td/following-sibling::td[contains(text(), ' / ')]")[:5]

leave_dict = []
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
        print(f"{date.strftime('%A')}: Holiday")
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
                    print(f"{date.strftime('%A')}: Sick Leave")
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
                    print(f"{date.strftime('%A')}: Sick leave 0.5 day / Work 0.5 day")
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
                    print(f"{date.strftime('%A')}: Annual Leave")
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
                    print(f"{date.strftime('%A')}: Annual Leave 0.5 day / Work 0.5 day")
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
            print(f"{date.strftime('%A')}: Work")
            
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
        print(f"{date.strftime('%A')}: Work")
    response = requests.post(url, headers=headers, json=data)