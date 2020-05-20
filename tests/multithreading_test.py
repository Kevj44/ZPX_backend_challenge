import requests, threading, random, uuid, time, json

BASE_API_URL = 'http://localhost:5000/ZPXsteamdata/api/v1.0/reports/'
TIMESPANS = ['daily', 'weekly', 'yearly']

def send_report_request():
    for count in range(10):
        if random.randrange(1,8) == 1:
            start = time.time()
            response = requests.get(url = BASE_API_URL + 'votes')
            end = time.time()
            json_response = response.json()
            with open('./multithreading_test_results/' + str(uuid.uuid4()) + '_votes_result.txt', 'a') as f:
                f.write('timing: ' + str(end-start) + '\n\n')
                f.write(json.dumps(json_response, sort_keys = True, indent = 4, separators = (',', ': ')))
        else:
            start_year = random.randrange(2016, 2020)
            end_year = start_year + 1
            start_month = random.randrange(1, 13)
            end_month = random.randrange(1, 13)
            start_day = random.randrange(1, 29)
            end_day = random.randrange(1, 29)
            start_date = str(start_year) + '-' + str(start_month).zfill(2) + '-' + str(start_day).zfill(2)
            end_date = str(end_year) + '-' + str(end_month).zfill(2) + '-' + str(end_day).zfill(2)
            timespan = random.choice(TIMESPANS)
            PARAMS = {'start_date': start_date, 'end_date': end_date, 'timespan': timespan}
            start = time.time()
            response = requests.get(url = BASE_API_URL + 'trends', params = PARAMS)
            end = time.time()
            json_response = response.json()
            with open('./multithreading_test_results/' + str(uuid.uuid4()) + '_trends_result.txt', 'a') as f:
                f.write('start_date: ' + start_date + '\n')
                f.write('end_date: ' + end_date + '\n')
                f.write('timespan: ' + timespan + '\n')
                f.write('timing: ' + str(end-start) + '\n\n')
                f.write(json.dumps(json_response, sort_keys = True, indent = 4, separators = (',', ': ')))

try:
   threading.Thread(target=send_report_request).start()
   threading.Thread(target=send_report_request).start()
   threading.Thread(target=send_report_request).start()
   threading.Thread(target=send_report_request).start()
except:
   print('Message: unable to start thread')
