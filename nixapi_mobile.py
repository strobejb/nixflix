import requests
from requests_toolbelt.utils import dump
import json
import jsons
from datetime import datetime

NIXPLAY_API = 'mobile-api.nixplay.com'

class NixPlayMobile(object):
  def __init__(self):
    self.authtoken = None
    self.session   = requests.Session()

  def headers(self):
    hdrs = {     
      'Authority': 'mobile-api.nixplay.com',
      'Source': 'mobile',
      'AppName': 'com.creedon.Nixplay',
      'AppVersion': '3.13.4',
      'DeviceModel': 'Android SDK built for x86_64',
      'DevicePlatform': 'android',
      'DevicePlatformVersion': '28',
      'Content-Type': 'application/json',      
      'Accept-Encoding': 'gzip',
      'User-Agent': 'okhttp/3.12.1'
    }     
    if self.authtoken:
      hdrs['Authorization'] = f'Bearer {self.authtoken}'
    return hdrs

  def login(self, user, password):
    self.user = f'{user}@mynixplay.com'
   
    data = {
      'username': user,
      'password': password,
      'deviceId':'46df3cb6cf6bc161',
      'notificationKey': 'eve5oCdE6a0:APA91bExwDEUdnqyJRoJR8cZ33UvRRMgkw0giuHCgr5unBonzIjTpUORN27dSThyljLv_DeMa537R-y_OAdjz9Bic4DT67gb7dS9iqfwALGzc8MePvLEbJdJJTQA3DMNW3IUjqo5Ll3x',
      'platform': 'android',
      'model': 'Android SDK built for x86_64',
      'version': '3.13.4',
      'env':'prod'
    }

    j = self.post_api_v1('auth/signin', data)
    self.authtoken = j['token']    

    # make 2nd API call to get flickr token
    appconf = self.getAppConfig()
    self.flickr_auth = appconf['flickr_api_key']
    return j


  def api(self, request_method, api_version, api_method, params={}, data=None):
    url = f'https://{NIXPLAY_API}/{api_version}/{api_method}'

    defparams = {}
    data = json.dumps(data) if data else None

    r = self.session.request(request_method, url, headers = self.headers(), params={**defparams,**params}, data=data)
    #data = dump.dump_all(r)
    #print(data.decode('utf-8'))
    return r

  def get_api_v1(self, method, params={}):
    r = self.api('GET', 'v1', method, params)
    return json.loads(r.text)

  def get_api_v3(self, method, params={}):
    r = self.api('GET', 'v3', method, params)
    return json.loads(r.text)

  def post_api_v1(self, method, params={}, data={}):
    r = self.api('POST', 'v1', method, params, data)
    #data = dump.dump_all(r)
    #print(data.decode('utf-8'))

    return json.loads(r.text)

  def post_api_v3(self, method, data={}, params={}):
    r = self.api('POST', 'v3', method, params, data)
    return json.loads(r.text)

  def delete_api_v3(self, method, params={}):
    r = self.api('DELETE', 'v3', method, params, data)
    return json.loads(r.text)

  #
  # NixPlay API
  #

  def getOnlineStatus(self):
    return self.get_api_v3('frame/online-status/')

  def getFrames(self):
    return self.get_api_v1('frames')['frames']

  def getFrame(self, name):
    frames = self.getFrames()
    for frame in frames:
      if frame['name'] == name:
        return frame

  # mobile-specific APIs
  def getAppConfig(self):
    r = self.api('POST', 'd/v2', 'app/config/')
    return json.loads(r.text)

  def getFramesStatus(self):
    return self.get_api_v1('frames/status')['frames']

  def getFrameSettings(self, frame_id):
    return self.get_api_v1(f'frames/{frame_id}/settings')    

  #def getFrameSettingsx(self, frame_id):
  #  return self.get_api_v1(f'frame/settings/?frame_pk={frame_id}')    

  def getFrameState(self, frame_internal_id):
    return self.get_api_v1(f'frames/{frame_internal_id}/state')

  def getPlayLists(self):
    return self.get_api_v3('playlists')

  def getPlayList(self, name):
    playlists = self.getPlayLists()

    for p in playlists:
      if p['name'] == name:
        return p

  def getPlayListSlides(self, playlist_id, offset=0, size=50):
    params = {'offset': offset, 'size': size}
    return self.get_api_v1(f'playlists/{playlist_id}', params)

  def getPlayListSocialData(self, playlist_id):
    return self.get_api_v3(f'social-data/playlist/{playlist_id}')    

  def addPlayListPhotos(self, playlist_id, photos):
    return self.post_api_v3(f'playlists/{playlist_id}/items', photos)

  # photo_ids can be a list, or a single item
  def delPlayListPhotos(self, playlist_id, photo_ids):
    #f'playlists/{playlist_id}/
    params = { 'itemIds[]': photo_ids, 'delPhoto': ''}
    return self.delete_api_v1(f'playlists/{playlist_id}/items', params=params)

  def delPlayList(self, playlist_id):
    return self.delete_api_v1(f'playlists/{playlist_id}/items')#?delPhoto=')

  def updatePlaylist(self, frame_id, playlist_id=''):
    # application/x-www-form-urlencoded;
    data = {
      'frame_pk': frame_id,
      'slideshow_list': playlist_id,
      'operation': 'update'
    }
    return self.post_api_v3(f'playlists/{playlist_id}/items')#?delPhoto=')


  def frameControl(self, frame_id, category, command):
    data = {
      "category": category,
      "data": json.dumps(command)   # "{\"button\":\"slideshow\"}"
    }
    return self.post_api_v1(f'frames/{frame_id}/commands', data=data)

  def startPlaylist(self, frame_id, playlist_id):
    return self.frameControl(frame_id, 'carousel', {"source": "gallery", "playlistId": playlist_id})

  def toggleSlideshow(self, frame_id):
    return self.frameControl(frame_id, 'remoteControl', {"button": "slideshow"})

  def screenOn(self, frame_id):
    return self.frameControl(frame_id, 'remoteControl', {"button": "screenOn"})    

  def screenOff(self, frame_id):
    return self.frameControl(frame_id, 'remoteControl', {"button": "screenOff"})        

  def updateActivities(self):
    return self.post_api_v3(f'users/activities', data = {})
 
