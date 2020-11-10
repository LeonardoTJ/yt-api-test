import py_colors as pc
#import pprint
import json
import html
import requests
import datetime
import dateutil.parser
from dateutil import tz

from googleapiclient.discovery import build
from tqdm import tqdm

class YoutubeStats:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def print_stream_info(self, channel_id):
        url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=upcoming&key={self.api_key}'
        json_url = requests.get(url)
        data = json.loads(json_url.text)

        if(len(data["items"]) == 0):
            print(pc.CRED + pc.CBOLD + "Sin resultados" + pc.CEND)
            return

        channel_name = data["items"][0]["snippet"]["channelTitle"]
        
        streams = {}
        for item in data["items"]:
            id = item["id"]["videoId"]
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={id}&key={self.api_key}"
            json_url = requests.get(url)
            
            data = json.loads(json_url.text)["items"][0]["liveStreamingDetails"]["scheduledStartTime"]
            scheduledDate = dateutil.parser.parse(data).astimezone(tz.tzlocal())
            diff = scheduledDate - scheduledDate.now(tz.tzlocal())
            remainingTime = divmod(diff.total_seconds(), 60)
            remainingHours = divmod(remainingTime[0], 60)

            if remainingHours[0] > 0:
                streams[id] = item["snippet"]
                streams[id]["title"] = html.unescape(streams[id]["title"])
                streams[id]["scheduledDate"] = scheduledDate.strftime("%c")
                streams[id]["remainingTime"] = "en {} horas, {} minutos".format(str(remainingHours[0]), str(int(remainingHours[1])))
        
        print(pc.CBOLD + pc.CBLUE + channel_name + pc.CEND)
        if not bool(streams):
            print('\t{:10}{}{}{}'.format(pc.CRED, pc.CBOLD, "No hay transmisiones agendadas", pc.CEND))
            return
        
        # pp = pprint.PrettyPrinter()
        # pp.pprint(streams)
        # return

        i = 0
        for video in streams:
            i += 1
            print("{greenTag}{count:10}. {title:50} {endTag}[{id:<10}]{greenTag}" \
                  "\n\t\t({date}, {yellowTag}{remaining}{endTag}{greenTag}){endTag}".format(greenTag=pc.CGREEN,
                                                                                                count=i,
                                                                                                title=streams[video]["title"],
                                                                                                date=streams[video]["scheduledDate"],
                                                                                                remaining=streams[video]["remainingTime"],
                                                                                                yellowTag=pc.CYELLOW,
                                                                                                endTag=pc.CEND,
                                                                                                id=video))