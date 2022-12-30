from Google import Create_Service
import datetime
import pandas as pd
from nodejs import node

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

folder_id = '1No9_Q-wSV9q6F3hQLPV1pVIzpTBYZ92q'

# remember days should be = 1 but I am just doing it now for proper sleep thing
yesterday = datetime.datetime.today() - datetime.timedelta(days=2)
yesterday_formatted = yesterday.strftime('%Y-%m-%d')

file_name = f"HealthMetrics-{yesterday_formatted}.csv"

query = f"parents = '{folder_id}' and name = '{file_name}'"
response = service.files().list(q=query).execute()
file_id = response.get('files')[0].get('id')

file_url = f"https://drive.google.com/uc?id={file_id}"

print(file_url)
df = pd.read_csv(file_url)

time_arr = df['Date']
time_arr = [time.split(' ')[1] for time in time_arr]


steps_arr = df['Step Count (count) '].dropna()
cals_arr = df['Active Energy (kcal)'].dropna()
water_arr = df['Dietary Water (fl_oz_us)'].dropna()

# # calculations for sleep_val
# sleep_asleep_arr = df['Sleep Analysis [Asleep] (hr)'].dropna()
# sleep_in_bed_arr = df['Sleep Analysis [In Bed] (hr)'].dropna()

# sleep_val = (sleep_asleep_arr[0] + sleep_in_bed_arr[0]) / 2
# sleep_val = round(sleep_val, 2)

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
    'Date': yesterday.strftime('%m-%d-%Y'),
    'Water (fl oz)': water_val,
    'Sleep (Hrs)': 6,
    'Exercise (Pct)': workout_pct
}


# print(notion_obj)
path_arg = "./node/index.js"


# file thing is better
node.call([path_arg, str(notion_obj)])
