import requests
from requests_toolbelt.utils import dump
import json
import jsons
from datetime import datetime

#NIXPLAY_API = 'api.nixplay.com'
NIXPLAY_API = 'mobile-api.nixplay.com'

class NixPlay(object):
  def __init__(self):
    self.crsftok   = None
    self.cookies   = None
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


  def flickr_api(self, method, params={}):
    u = f'https://{NIXPLAY_API}/v1/social_api/flickr/services/rest'
    defparams = {
      'api_key':'3a95aeba90bc3698ba73fb076f7ed370',
      'auth_token':self.flickr_auth,
      'format': 'json',
      'method':method,
      'nojsoncallback':1,
      #'page':1,
      'per_page':100,
      #'primary_photo_extras':''
      #'url_m,url_o
    }
    #print(Fore.GREEN+Style.BRIGHT+f'\n{u} <{method}> {json.dumps(params)}'+Style.RESET_ALL)
    #print(self.headers())

    r = self.session.get(u, headers = self.headers(), params={**defparams,**params})#,cookies=self.cookies)
    data = dump.dump_all(r)
    print(data.decode('utf-8'))

    #print(r.request.url)
    #print(r.request.headers)
    #print(r.text)
    #print(r.request.url)
    #data = dump.dump_all(r)
    #print(data.decode('utf-8'))
    #?api_key={self.apikey}&auth_token={self.auth_token}&format=json&method={method}&nojsoncallback=1'
    return json.loads(r.text)

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



  # mobile-specific APIs
  def getAppConfig(self):
    r = self.api('POST', 'd/v2', 'app/config/')
    return json.loads(r.text)

  def getFramesStatus(self, frame_id):
    return self.get_api_v1('frames/status')['frames']

  def getFrameSettings(self, frame_id):
    return self.get_api_v1(f'frames/{frame_id}/settings')    

  def getFrameSettingsx(self, frame_id):
    return self.get_api_v1(f'frame/settings/?frame_pk={frame_id}')    

  def getPlayLists(self):
    return self.get_api_v3('playlists')

  def getPlayList(self, name):
    playlists = self.getPlayLists()

    for p in playlists:
      if p['name'] == name:
        return p

  def getPlayListSlides(self, playlist_id, offset=0, size=100):
    return self.get_api_v3(f'playlists/{playlist_id}/slides', {'size': size, 'offset': offset})

  def addPlayListPhotos(self, playlist_id, photos):
    return self.post_api_v3(f'playlists/{playlist_id}/items', photos)

  def delPlayListPhoto(self, playlist_id, id):
    #f'playlists/{playlist_id}/
    params = { 'id': id, 'delPhoto': ''}
    return self.delete_api_v3(f'playlists/{playlist_id}/items', params=params)

  def delPlayList(self, playlist_id):
    return self.delete_api_v3(f'playlists/{playlist_id}/items')#?delPhoto=')

  def updatePlaylist(self, frame_id, playlist_id=''):
    # application/x-www-form-urlencoded;
    data = {
      'frame_pk': frame_id,
      'slideshow_list': playlist_id,
      'operation': 'update'
    }
    return self.post_api_v3(f'playlists/{playlist_id}/items')#?delPhoto=')


  def frameControl(self, frame_id, command):
    data = {
      "category": "remoteControl",
      "data": json.dumps(command)   # "{\"button\":\"slideshow\"}"
    }
    return self.post_api_v1(f'frames/{frame_id}/commands', data=data)

  def startSlideshow(self, frame_id):
    return self.frameControl(frame_id, {"button": "slideshow"})

  def screenOn(self, frame_id):
    return self.frameControl(frame_id, {"button": "screenOn"})    

  def screenOff(self, frame_id):
    return self.frameControl(frame_id, {"button": "screenOff"})        

  def updateActivities(self):
    return self.post_api_v3(f'users/activities', data = {})
 

  #
  # Social / Flickr API
  #

  def flickr_people_getPhotos(self, page=1):
    return self.flickr_api('flickr.people.getPhotos', {'photoset_id': photoset_id, 'page': page, 'per_page':1, 'user_id':'me', 'extras':'url_m,url_o'})
   
  def flickr_photosets_getPhotos(self, photoset_id, page=1, per_page=30):
    return self.flickr_api('flickr.photosets.getPhotos', {'photoset_id': photoset_id, 'page': page, 'per_page':per_page, 'extras':'url_m,url_k,url_o,date_upload,last_update'})

  def flickr_photosets_getList(self, page=1, per_page=30):
    #primary_photo_extras=url_m,url_o
    return self.flickr_api('flickr.photosets.getList', {'page': page, 'per_page': per_page})

  def flickr_photosets_getWithName(self, name):
    photosets = self.flickr_photosets_getList()
    
    for photoset in photosets['photosets']['photoset']:
      #print(photoset['id'], photoset['title']['_content'])
      if photoset['title']['_content'] == name:
        return photoset
        #photoset_id = photoset['id']   

  def flickr_photosets_getInfo(self, photoset_id):
    return self.flickr_api('flickr.photosets.getInfo', {'photoset_id': photoset_id})

  def flickr_urls_getUserProfile(self):
    return self.flickr_api('flickr.urls.getUserProfile')

  def flickr_favorites_getList(self, page=1, per_page=30):
    #primary_photo_extras=url_m,url_o
    return self.flickr_api('flickr.favorites.getList', {'page': page, 'per_page': per_page})

