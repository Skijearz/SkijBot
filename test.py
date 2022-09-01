import os
import requests
import re

html = requests.get("https://www.youtube.com/channel/UCgvFyzcNPRFl6GJAd-ueRTQ"+"/videos",headers={'accept-language' :'en-US,en;q=0.9','Cache-Control': 'no-cache'},cookies={'CONSENT': 'YES+42'}).text
channelName = re.search('(?<="name": ").*?(?=")',html).group()
newestUrl = "https://www.youtube.com/watch?v=" + re.search('(?<="videoId":").*?(?=")',html).group()
print(html + html + " test for pr")
