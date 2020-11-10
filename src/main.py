import keys
import channels
from ytstats import YoutubeStats

yt = YoutubeStats(keys.API_KEY)

for channel in channels.ids.values():
    yt.print_stream_info(channel)
