# One click doppio timesheet
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

## Precautions
- Ensure that your leave history within the last 5 entries does not include leaves of 2 days or more, as this will cause the script to malfunction.

## Usage
To use this project, follow these steps:
1. Clone the repository to your local machine.
2. Install the necessary dependencies by running the following command:
    ```
    pip install -r requirements.txt
    ```
3. Configure the project settings by editing the `config.py` file.
4. Run the script using the command:
    ```
    python get_leave_data_from_session_token.py
    ```
