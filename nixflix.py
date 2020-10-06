import argparse
import json
import jsons
from datetime import datetime
import dateutil.parser
import pytz
import os
import sys

from nixapi import NixPlay
from colorama import Fore, Back, Style, init
try:
    init()
except:
    print('No colour support')

def update_nixplay_playlist(np, np_playlist_name, flickr_album_name, force):
 
  # Nixplay playlist
  playlist = np.getPlayList(args.playlist)  
  if not playlist:
    print(f'Playlist not found: {args.playlist}')
    return 1
  #print(json.dumps(playlist, indent=2))
  #utcfromtimestamp
  np_last_updated = dateutil.parser.isoparse(playlist['last_updated_date'])
  
  #np_last_updated = datetime.utcfromtimestamp(np_last_updated)#int(playlist['last_updated_date']))
  #np_last_updated = utc.localize(np_last_updated)
  print(f'Nixplay last updated: {np_last_updated}')


  # Flickr album
  photoset = np.flickr_photosets_getWithName(args.album)
  #print(json.dumps(photoset, indent=2))

  # Album info
  #info = np.flickr_photosets_getInfo(photoset['id'])
  #print(json.dumps(info, indent=2))

  flickr_last_updated = datetime.fromtimestamp(int(photoset['date_update']), pytz.timezone("UTC"))
  #flickr_last_updated = utc.localize(flickr_last_updated)
  print(f'Flickr album updated: {flickr_last_updated}')

  if np_last_updated < flickr_last_updated or force: 

    print('Updating!')

    items = { "items": [] }
    page = 1
    while True:
      # get list of flickr photots in album
      photos = np.flickr_photosets_getPhotos(photoset['id'], page)
      #print(json.dumps(photos, indent=2))

      for photo in photos['photoset']['photo']:
        updated = datetime.fromtimestamp(int(photo["lastupdate"]))
        orientation = 1 if photo["width_o"] < photo["height_o"] else 0
      
        item = { 
          "photoUrl":     photo["url_k"] if "url_k" in photo else photo["url_o"], 
          "thumbnailUrl": photo["url_m"],
          "orientation":  orientation
        }
        
        items['items'].append(item)

      page = page + 1
      if page > photos['photoset']['pages']:
        break
      
    #print(items)
    r = np.delPlayList(playlist['id'])
    r = np.addPlayListPhotos(playlist['id'], items)
    print(f'Posted {len(items["items"])} photos: {r.status_code}')

    np.updateActivities()

def status(np):
  frames = np.getFrames()
  print(json.dumps(frames, indent=2))
  print('-'*80)

  for frame in frames:
    config = np.getFrameSettings(frame['id'])
    print(json.dumps(config, indent=2))
  
  print('-'*80)
  
  status = np.getOnlineStatus()
  print(json.dumps(status, indent=2))
  
  for frame in status['frames']:
    ls = datetime.fromtimestamp(int(frame['lastConnected'])/100)
    print(f'lastSeen: {ls}')

def main(args):
  np = NixPlay()
  np.login(args.username, args.password)

  if args.status:
    status(np)
    return 0

  while True:
    update_nixplay_playlist(np, args.playlist, args.album, args.force)

    if not args.poll:
      break

    sleep(60)

if __name__ == "__main__":
  parser = argparse.ArgumentParser('Nixplay / Flickr album sync')
  parser.add_argument('--username', help='Nixplay username')
  parser.add_argument('--password', help='Nixplay password')
  parser.add_argument('--nixplay-list', dest = 'playlist', default='My Playlist')
  parser.add_argument('--flickr-album', dest = 'album',    default='Favs')
  parser.add_argument('--poll', default = 0)
  parser.add_argument('--force', default=True)
  parser.add_argument('--status', action='store_true', default=False)

  args = parser.parse_args()
  if not args.username and 'NIXPLAY_USERNAME' in os.environ:
    args.username = os.environ['NIXPLAY_USERNAME']
  else:
    print('Missing username')
    sys.exit(-1)

  if not args.password and 'NIXPLAY_PASSWORD' in os.environ:
    args.password = os.environ['NIXPLAY_PASSWORD']
  else:
    print('Missing password')
    sys.exit(-1)    

  main(args)


