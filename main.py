import os
from Google import Create_Service
import datetime
import time
import pandas as pd
from nodejs import node
from twilio.rest import Client
from dotenv import load_dotenv

# accept post requrests on port 8000

load_dotenv()
print(os.getenv('twillio_account_sid'))

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

folder_id = os.getenv('google_drive_folder_id')


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


def start():
    i = 0
    while True:
        update_dashboard()
        time.sleep(86380)
        i += 1
        if (i == 7):
            send_texts_to_all()
            i = 0


def update_dashboard():
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday_formatted = yesterday.strftime('%Y-%m-%d')

    file_name = f"HealthMetrics-{yesterday_formatted}.csv"

    query = f"name = '{file_name}'"
    print(query)
    response = service.files().list(q=query).execute()
    print(response)
    file_id = response.get('files')[0].get('id')

    file_url = f"https://drive.google.com/uc?id={file_id}"

    print(file_url)
    df = pd.read_csv(file_url)

    time_arr = df['Date']
    time_arr = [time.split(' ')[1] for time in time_arr]

    steps_arr = df['Step Count (count) '].dropna()
    cals_arr = df['Active Energy (kcal)'].dropna()
    water_arr = df['Dietary Water (fl_oz_us)'].dropna()

    # calculations for sleep_val
    sleep_asleep_arr = df['Sleep Analysis [Asleep] (hr)'].dropna()
    sleep_in_bed_arr = df['Sleep Analysis [In Bed] (hr)'].dropna()

    sleep_val = (sleep_asleep_arr[0] + sleep_in_bed_arr[0]) / 2
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

    CALORIE_CONST = 500
    STEPS_CONST = 5000

    workout_name_yesterday = yesterday.strftime('%A')
    workout_pct = sum(cals_arr) / CALORIE_CONST
    proper_workout = workout_dict[workout_name_yesterday]
    if (proper_workout == 'Running'):
        step_sum = 0
        for i in range(0, 12):
            step_sum += steps_arr[i]
        workout_pct = step_sum / STEPS_CONST
    if (proper_workout == 'rest'):
        workout_pct = 100
    workout_pct = round(workout_pct, 2)

    # calculations for water_val
    water_val = round(sum(water_arr))

    notion_obj = {
        'Week Day': yesterday.strftime('%A'),
        'Water (fl oz)': water_val,
        'Sleep (Hrs)': 6,
        'Exercise (Pct)': workout_pct,
        'Date': yesterday.isoformat()
    }

    path_arg = "./index.js"

    node.call([path_arg, str(notion_obj)])


start()
