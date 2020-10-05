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

def demo(args):

  np = NixPlay()
  np.login(args.username, args.password)

  # Frames
  frames = np.getFrames()
  #print(json.dumps(frames, indent=2))  
  for f in frames:
    print(f['id'], f['name'])

  # Playlists
  playlists = np.getPlayLists()
  #print(json.dumps(playlists, indent=2))

  for p in playlists:
    print(p['id'], p['name'], f"({p['picture_count']})", p['last_updated_date'])#datetime.fromtimestamp(p['lastUpdate']/1000))  

    if p['name'] == 'My Playlist':
      #print(Color.Red+p[''])
      playlist_id = p['id']

  # Online status
  status = np.getOnlineStatus()
  print(json.dumps(status, indent=2))
  for f in status['frames']:
    ls = datetime.fromtimestamp(int(f['lastConnected'])/100)
    print(f'lastSeen: {ls}')

  # Slides
  slides = np.getPlayListSlides(playlist_id)
  print(json.dumps(slides, indent=2))
  for slide in slides['slides']:
    ts = datetime.fromtimestamp(slide['timestamp']/1000)
    print(slide['playlistItemId'], ts)
    pass

  # user profile
  print('')
  profile = np.flickr_urls_getUserProfile()
  print(json.dumps(profile, indent=2))

  # Flickr albums
  photolist = np.flickr_photosets_getList()
  #print(json.dumps(photolist, indent=2))

  for photoset in photolist['photosets']['photoset']:
    print(photoset['id'], photoset['title']['_content'])
    if photoset['title']['_content'] == 'Favs':
      photoset_id = photoset['id']   
      
  # Album info
  info = np.flickr_photosets_getInfo(photoset_id)
  print(json.dumps(info, indent=2))

  # Album photos
  photos = np.flickr_photosets_getPhotos(photoset_id)
  print(json.dumps(photos, indent=2))

  for photo in photos['photoset']['photo']:
    lu = datetime.fromtimestamp(int(photo["lastupdate"]))
    du = datetime.fromtimestamp(int(photo["dateupload"]))
    print(f'{photo["id"]} \"{photo["title"]}\" - {lu} - {du} ')#{photo["url_o"]}')


  items = {
    "items": [
      { 'orientation': 1 },
      { 'photoUrl': 'https://live.staticflickr.com/.....' },
      { 'thumbnailUrl': 'https://live.staticflickr.com/.....' }
    ]
  }

  #{"items":[
  #{"photoUrl":"https://live.staticflickr.com/65535/50382815533_de06b99634_k.jpg","thumbnailUrl":"https://live.staticflickr.com/65535/50382815533_0fcd8ceb05.jpg","orientation":1},
  #{"photoUrl":"https://live.staticflickr.com/65535/50398382646_e5fa29725f_k.jpg","thumbnailUrl":"https://live.staticflickr.com/65535/50398382646_621fa40f1d.jpg","orientation":1},
  #{"photoUrl":"https://live.staticflickr.com/65535/50405265737_d48fad2c00_k.jpg","thumbnailUrl":"https://live.staticflickr.com/65535/50405265737_12844d3e9c.jpg","orientation":1}
  #]}

  #np.addPlayListPhotos(playlist_id, items)

  #POST api.nixplay.com/v3/playlists/3201700/items
  #{items:[
  #orientation: 1
  #photoUrl: "https://live.staticflickr.com/31337/49849262952_82684bd73e_o.jpg"
  #thumbnailUrl: "https://live.staticflickr.com/31337/49849262952_49382bb194.jpg"
  #]}
  #
  #
  ##

  # flickr:
  #method=flickr.photosets.getList&page=1&per_page=30&primary_photo_extras=url_m,url_o
  #method=flickr.urls.getUserProfile
  #method=flickr.photosets.getInfo&nojsoncallback=1&photoset_id=72157713990481416
  #method=flickr.photosets.getPhotos&nojsoncallback=1&page=1&per_page=30&photoset_id=72157713990481416



  favs = np.flickr_favorites_getList(photoset_id)
  print(json.dumps(favs, indent=2))

def update_nixplay_playlist(np, np_playlist_name, flickr_album_name):
 
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
  flickr_last_updated = datetime.fromtimestamp(int(photoset['date_update']), pytz.timezone("UTC"))
  #flickr_last_updated = utc.localize(flickr_last_updated)
  print(f'Flickr album updated: {flickr_last_updated}')

  if np_last_updated < flickr_last_updated: 

    print('Updating!')

    # get list of flickr photots in album
    photos = np.flickr_photosets_getPhotos(photoset['id'])
    #print(json.dumps(photos, indent=2))

    items = { "items": [] }
    for photo in photos['photoset']['photo']:
      updated = datetime.fromtimestamp(int(photo["lastupdate"]))
      
      item = { 
        "photoUrl":     photo["url_o"], 
        "thumbnailUrl": photo["url_m"],
        "orientation":  1
      }
        
      items['items'].append(item)
      
    r = np.addPlayListPhotos(playlist['id'], items)
    print(f'Posted: {r.status_code}')

def main(args):
  np = NixPlay()
  np.login(args.username, args.password)

  while True:
    update_nixplay_playlist(np, args.playlist, args.album)

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


