from __future__ import print_function    # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys
import app_config

client_credentials_manager = SpotifyClientCredentials(client_id=app_config.SPOTIPY_CLIENT_ID,
                                                      client_secret=app_config.SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

if len(sys.argv) > 1:
    tid = sys.argv[1]
else:
    tid = 'spotify:track:4TTV7EcfroSLWzXRY6gLv6'

start = time.time()
analysis = sp.audio_analysis(tid)
delta = time.time() - start
# print(json.dumps(analysis, indent=4))
with open('analysis.json', 'w') as outfile:
    json.dump(analysis, outfile)

print("analysis retrieved in %.2f seconds" % (delta,))
