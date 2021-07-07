import requests
import json


url = "https://www.wtfskins.com/api/v1/crashroundhistory/?limit={}&offset=0"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
    'Content-Type': 'text/html',
    }



def getRecentCrashes(amountOfRecentCrashPoints):
    page = requests.get(url.format(amountOfRecentCrashPoints),headers=headers)
    pageJson = json.loads(page.content)

    recentCrashPoints = []
    for x in pageJson['response']['data']:
        recentCrashPoints.append(x['crash_point'])
    
    return recentCrashPoints


def main():
    print(getRecentCrashes(4))

if __name__ =="__main__":
    main()
    