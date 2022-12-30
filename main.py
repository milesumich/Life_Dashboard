from Google import Create_Service
import datetime

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

folder_id = '1No9_Q-wSV9q6F3hQLPV1pVIzpTBYZ92q'

yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
yesterday_formatted = yesterday.strftime('%Y-%m-%d')

file_name = f"HealthMetrics-{yesterday_formatted}.csv"

query = f"parents = '{folder_id}' and name = '{file_name}'"
response = service.files().list(q=query).execute()

print(response.get('files')[0])
