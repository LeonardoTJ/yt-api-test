import py_colors as pc
import pprint
import json
import html
import requests
import datetime
import dateutil.parser

from dateutil import tz
from googleapiclient.discovery import build

class YoutubeStats:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def print_stream_info(self, channel_id):
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=statistics%2Csnippet&id={channel_id}&fields=items(snippet%2Ftitle%2Cstatistics%2FsubscriberCount)&key={self.api_key}"
        json_url = requests.get(url)
        data = json.loads(json_url.text)

        channel_name = data["items"][0]["snippet"]["title"]
        subscribers = data["items"][0]["statistics"]["subscriberCount"]
        print("{boldTag}{blueTag}{name}{endTag}{blueTag} - {subs:,} suscriptores{endTag}".format(boldTag=pc.CBOLD,
                                                                                                blueTag=pc.CBLUE,
                                                                                                name=channel_name,
                                                                                                subs=int(subscribers),
                                                                                                endTag=pc.CEND))

        url = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&eventType=upcoming&maxResults=5&type=video&fields=pageInfo%2Citems(id%2FvideoId%2Csnippet%2Ftitle%2C)&key={self.api_key}"
        json_url = requests.get(url)
        data = json.loads(json_url.text)

        if data["pageInfo"]["totalResults"] == 0:
            print('\t{:10}{}{}{}'.format(pc.CYELLOW, "No hay transmisiones agendadas", pc.CEND))
            return

        streams = {}
        for item in data["items"]:
            id = item["id"]["videoId"]
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={id}&fields=items(liveStreamingDetails%2FscheduledStartTime)&key={self.api_key}"
            json_url = requests.get(url)
            data = json.loads(json_url.text)
            
            dateString = data["items"][0]["liveStreamingDetails"]["scheduledStartTime"]
            scheduledDate = dateutil.parser.parse(dateString).astimezone(tz.tzlocal())
            diff = scheduledDate - scheduledDate.now(tz.tzlocal())
            remainingTime = divmod(diff.total_seconds(), 60)
            remainingHours = divmod(remainingTime[0], 60)

            if remainingHours[0] > 0:
                streams[id] = item["snippet"]
                streams[id]["title"] = html.unescape(streams[id]["title"])
                streams[id]["scheduledDate"] = scheduledDate.strftime("%c")
                streams[id]["remainingTime"] = "en {} horas, {} minutos".format(str(int(remainingHours[0])), str(int(remainingHours[1])))

        i = 0
        for video in streams:
            i += 1
            print("{greenTag}{count:10}. {title} {endTag}[{id:<10}]{greenTag}" \
                  "\n\t\t({date}, {yellowTag}{remaining}{endTag}{greenTag}){endTag}".format(greenTag=pc.CGREEN,
                                                                                                count=i,
                                                                                                title=streams[video]["title"],
                                                                                                date=streams[video]["scheduledDate"],
                                                                                                remaining=streams[video]["remainingTime"],
                                                                                                yellowTag=pc.CYELLOW,
                                                                                                endTag=pc.CEND,
                                                                                                id=video))