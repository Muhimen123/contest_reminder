import os
import sys
from datetime import datetime, timedelta

import requests

username = os.environ["CLIST_USER"]
api_key = os.environ["CLIST_API_KEY"]
filter_list = ["atcoder.jp", "codeforces.com", "codechef.com", "vjudge.net"]
format_string = "%I:%M %p %d-%b"

def filter_contest(all_contests):
    contests = list()
    for contest in all_contests:
        host = contest["host"]
        if host in filter_list:
            contests.append(contest)

    return contests


def pretty_print(all_contests):

    ssc = solo_speed_contest()
    if not isinstance(ssc, int):
        all_contests.append(ssc)

    for contest in all_contests:
        print("---")
        print(f"Site: {contest['host']}")
        print(f"Contest Name: {contest['event']}")
        print(f"Start time: {contest['start']}")
        print(f"Duration: {contest['duration']}")
        print(f"Contest code: {contest['id']}")


def convert_timestring(time_string):
    format = "%Y-%m-%dT%H:%M:%S"
    dt_obj = datetime.strptime(time_string, format)
    dt_obj += timedelta(hours=6)

    output = dt_obj.strftime(format_string)
    return output


def solo_speed_contest():
    url = "https://vjudge.net/contest/data?draw=1&start=0&length=20&sortDir=desc&sortCol=0&category=all&running=0&title=&owner=ICPC_Bot"
    res = requests.get(url)
    data = res.json()
    data = data["data"][0]

    contest_id = data[0]
    contest_name = data[1]
    contest_start_time = data[3]
    contest_end_time = data[4]
    contest_duration = (contest_end_time - contest_start_time) // (1000 * 3600)

    contest_start_time_unix = datetime.fromtimestamp(contest_start_time / 1000)
    contest_start_time_formatted = contest_start_time_unix.strftime("%d.%m %a %H:%M")

    contest = dict()
    
    contest["id"] = contest_id
    contest["host"] = "vjudge.net"
    contest["event"] = contest_name
    contest["start"] = contest_start_time_formatted
    contest["duration"] = f"{contest_duration} hours" 
    contest["href"] = f"https://vjudge.net/contest/{contest_id}"

    current_time = datetime.now()
    unix_time = int(current_time.timestamp())
    unix_time *= 1000
    contest["unix_time"] = unix_time
    if unix_time < contest_start_time:
        return contest
    else:
        return -1


def template_print_ssc(contest):
    contest_name = contest["event"]
    contest_link = contest["href"]
    hours = 1
    minutes = 0
    start_time = datetime.fromtimestamp(contest["unix_time"] / 1000)
    start_time = start_time.strftime(format_string)

    announcement = f"""Assalamu alaikum everyone.

Contest reminder for {contest_name}
Starts at: {start_time}
Duration: {hours} hours {minutes} minutes
Link: {contest_link}"""

    print(announcement)


def template_print(contest):
    if not (contest["host"] == "vjudge.net"):
        start_time = convert_timestring(contest["start"])
    else:
        start_time = contest["start"]
    
    seconds = contest["duration"]
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    contest_name = contest["event"]
    contest_link = contest["href"]

    announcement = f"""Assalamu alaikum everyone. 

Contest reminder for {contest_name}
Starts at: {start_time}
Duration: {hours} hours {minutes} minutes
Link: {contest_link}"""
    print(announcement)


def main():
    if len(sys.argv) == 1:
        option = "help"
    else:
        option = sys.argv[1]


    if option == "view":
        base_url = "https://clist.by:443/api/v4/contest/"
        params = {
            "username": username,
            "api_key": api_key,
            "upcoming": True,
            "format_time": True,
            "limit": 1000,
            "order_by": "-start",
        }

        res = requests.get(base_url, params=params)

        if res.status_code == 200:
            data = res.json()
            contests = filter_contest(data["objects"])
            pretty_print(contests)
        else:
            print("Request Failed!")

    elif option == "details":
        try:
            contest_id = sys.argv[2]
            base_url = f"https://clist.by:443/api/v4/contest/{contest_id}"
            params = {"username": username, "api_key": api_key}
            res = requests.get(base_url, params=params)

            if res.status_code == 200:
                data = res.json()
                template_print(data)
            else:
                contest = solo_speed_contest()
                if not isinstance(contest, int):
                    template_print_ssc(contest)

        except os.error as e:
            print("Please provide contest id")

    elif option == "upcoming":

        starting_time = datetime.now()
        ending_time = starting_time + timedelta(hours=48)
        formatted_string = ending_time.strftime("%Y-%m-%dT%H:%M:%S")

        base_url = "https://clist.by:443/api/v4/contest/"
        params = {
            "username": username,
            "api_key": api_key,
            "upcoming": True,
            "format_time": True,
            "end__lte": formatted_string,
        }

        res = requests.get(base_url, params=params)

        if res.status_code == 200:
            data = res.json()
            contests = filter_contest(data["objects"])
            pretty_print(contests)
        else:
            print("Request Failed!")


    else:
        print("Available flags: view, details, upcoming")

if __name__ == "__main__":
    main()
