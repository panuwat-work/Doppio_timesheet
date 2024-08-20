# Doppio_timesheet
## Goal of this project
- Eliminate the need for manual timesheet entry on a daily basis.

## Features
- Automatically retrieve leave days from humanOS.
- Automatically input holidays, leave, and work day into the timesheet for the entire week.
- Ability to input half-day leave into the timesheet.

## Supported leave types
- Vacation leave
- Sick leave
- Holidays

## Untested Functions
- Leave full day on vacation leave.
- Leave half day on vacation leave.
- Verify value of variable `__VIEWSTATE` and `__EVENTVALIDATION` are used in another HumanOS account for login using a session token.

## Holiday API
TH holiday data is retrieved from [calendarific.com](https://calendarific.com).

## Installation Requirements
To install the necessary dependencies, use the following command:
```
pip install -r requirements.txt
```
