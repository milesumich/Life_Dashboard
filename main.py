import os
from Google import Create_Service
import datetime
import pandas as pd
from twilio.rest import Client
from dotenv import load_dotenv
import pygsheets
import time


load_dotenv()


def update_spreadsheet(day_obj):
    sheet_url = 'https://docs.google.com/spreadsheets/d/16WPCMd_JcduYl-to7wWQXsvDKYzS6TTIgrbjyZwwSfs/'
    spreadsheet = pygsheets.authorize('./credentials.json')
    sheet = spreadsheet.open_by_url(sheet_url)
    curr_sheet = sheet[0]
    row = 1
    a1_notation = 'A' + str(row)
    while (curr_sheet.cell(a1_notation).value != ''):
        a1_notation = 'A' + str(row)
        row += 1

    current_letter = 'A'
    row = row - 1
    a1_notation = current_letter + str(row)
    for key in day_obj:
        curr_sheet.cell(a1_notation).set_value(day_obj[key])
        current_letter = chr(ord(current_letter) + 1)
        a1_notation = current_letter + str(row)


def send_text(name, number):
    account_sid = os.getenv('twillio_account_sid')
    auth_token = os.getenv('auth_token')
    client = Client(account_sid, auth_token)

    notion_database_id = os.getenv('db_id')
    notion_url = 'https://www.notion.so/' + notion_database_id

    body_str = 'Hey ' + name + ', its that time of the week again, see how ' + \
        os.getenv('your_name') + \
        ' kept up with his habits this past week:' + notion_url

    client.messages.create(
        messaging_service_sid=os.getenv('messaging_service_sid'),
        body=body_str,
        to=number
    )


# phone_number list and and name_list must be of same length
def send_texts_to_all():
    phone_number_list = os.getenv('phone_list').split(',')
    name_list = os.getenv('name_list').split(',')
    for i in range(0, len(phone_number_list)):
        send_text(name_list[i], phone_number_list[i])


def create_next_page(week_num):
    sheet_url = 'https://docs.google.com/spreadsheets/d/16WPCMd_JcduYl-to7wWQXsvDKYzS6TTIgrbjyZwwSfs/'
    spreadsheet = pygsheets.authorize('./credentials.json')
    sheet = spreadsheet.open_by_url(sheet_url)
    src_worksheet = sheet.worksheet_by_title('Template')
    sheet.add_worksheet("Week " + str(week_num), index=0,
                        src_worksheet=src_worksheet)


def start():
    week_num = 1
    i = 0
    while True:
        if (i == 0):
            create_next_page(week_num)
        update_dashboard()
        i += 1
        if (i == 7):
            i = 0
            send_texts_to_all()
            week_num += 1
        time.sleep(86380)


def update_dashboard():
    client_secret_file = 'credentials.json'
    api_name = 'drive'
    api_version = 'v3'
    scopes = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(client_secret_file, api_name, api_version, scopes)

    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday_formatted = yesterday.strftime('%Y-%m-%d')

    file_name = f"HealthMetrics-{yesterday_formatted}.csv"

    query = f"name = '{file_name}'"
    response = service.files().list(q=query).execute()
    file_id = response.get('files')[0].get('id')

    file_url = f"https://drive.google.com/uc?id={file_id}"

    df = pd.read_csv(file_url)

    row_count = df.shape[0] - 1

    time_arr = df['Date']
    time_arr = [time.split(' ')[1] for time in time_arr]

    steps_arr = df['Step Count (count) '].fillna(0)
    steps_arr = [step.replace(' ', '') for step in steps_arr]
    steps_arr = [step for step in steps_arr if step != '']
    steps_arr = [float(step) for step in steps_arr]

    cals_arr = df['Active Energy (kcal)'].fillna(0)
    water_arr = df['Dietary Water (fl_oz_us)'].fillna(0)

    # calculations for sleep_val
    sleep_asleep_arr = df['Sleep Analysis [Asleep] (hr)'].fillna(0)
    # convert sleep_asleep_arr to an array
    sleep_in_bed_arr = df['Sleep Analysis [In Bed] (hr)'].fillna(0)

    # get sum of values in sleep asleep_arr
    sleep_asleep_sum = 0
    sleep_in_bed_sum = 0
    for i in range(0, row_count):
        sleep_asleep_sum += sleep_asleep_arr[i]
        sleep_in_bed_sum += sleep_in_bed_arr[i]

    sleep_val = (sleep_asleep_sum + sleep_in_bed_sum) / 2
    sleep_val = round(sleep_val, 2)

    # calculations for workout_val
    workout_dict = {
        'Monday': 'Legs',
        'Tuesday': 'Rowing',
        'Wednesday': 'Push',
        'Thursday': 'Running',
        'Friday': 'Pull',
        'Saturday': 'Running',
        'Sunday': 'Rest'
    }

    CALORIE_CONST = 700
    STEPS_CONST = 8000

    workout_name_yesterday = yesterday.strftime('%A')
    workout_pct = sum(cals_arr) / CALORIE_CONST
    proper_workout = workout_dict[workout_name_yesterday]
    if (proper_workout == 'Running'):
        step_sum = 0
        for i in range(0, len(steps_arr)):
            step_sum += steps_arr[i]
        workout_pct = step_sum / STEPS_CONST
    if (proper_workout == 'rest'):
        workout_pct = 100
    workout_pct = round(workout_pct, 2)

    # calculations for water_val
    water_val = round(sum(water_arr))
    day_obj = {
        'Week Day': yesterday.strftime('%A'),
        'Water (fl oz)': water_val,
        'Sleep (Hrs)': sleep_val,
        'Exercise (Pct)': workout_pct,
        'Date': yesterday_formatted
    }
    update_spreadsheet(day_obj)


start()
