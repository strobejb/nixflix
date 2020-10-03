import requests
from requests_toolbelt.utils import dump
import json
import jsons
from datetime import datetime

class NixPlay(object):
  def __init__(self):
    self.crsftok = None
    self.cookies = None
    self.session = requests.Session()

  def headers(self):
    return { 
      'X-CSRF-Token': self.crsftok,
      'X-Nixplay-Username': self.user, 
      'X-Requested-With': 'XMLHttpRequest',
      'Referer': 'https://app.nixplay.com/',
      'Origin': 'https://app.nixplay.com',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-site',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
      'Accept':  'application/json, text/plain, */*',
      'Accept-Encoding': 'gzip, deflate, br',
      'Content-Type' : 'application/json'
    }       

  def login(self, user, password):
    self.user = f'{user}@mynixplay.com'

    data = {
      'email': user,
      'password': password,
      'signup_pair': 'no_pair',
      'login_remember': 'false'
    }
    hdr = {
      'Referer': 'https://app.nixplay.com/login',
      'Origin': 'https://app.nixplay.com',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-site'
    }
    r = self.session.post('https://api.nixplay.com/www-login/', headers=hdr,data=data)
    #data = dump.dump_all(r)
    #print(data.decode('utf-8'))

    j = json.loads(r.text)
    token = j['token']
    
    data = {
      'token': token,
      'startPairing': 'false',
      'redirectPath': ''
    }
    hdr = {
      'Referer': 'https://app.nixplay.com/login',
      'Origin': 'https://app.nixplay.com',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'same-site',
      'Sec-Fetch-User': '?1',
      'Upgrade-Insecure-Requests': '1'
    }
    r = self.session.post('https://api.nixplay.com/v2/www-login-redirect/', headers=hdr,data=data, allow_redirects=False)    
    #data = dump.dump_all(r)
    #print(data.decode('utf-8'))

    self.cookies = r.cookies
    #j - json.loads(r.text)

    # save the CSRF token
    self.csrftok  = r.cookies.get('prod.csrftoken')
    self.flickr_auth = r.cookies.get('prod.flickr.access_token')
    
    return j


  def flickr_api(self, method, params={}):
    u = f'https://api.nixplay.com/v2/social_api/flickr/services/rest'
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
    #print(r.request.url)
    #print(r.request.headers)
    #print(r.text)
    #print(r.request.url)
    #data = dump.dump_all(r)
    #print(data.decode('utf-8'))
    #?api_key={self.apikey}&auth_token={self.auth_token}&format=json&method={method}&nojsoncallback=1'
    return json.loads(r.text)

  def get_api_v3(self, method, params={}):
    u = f'https://api.nixplay.com/v3/{method}'
    defparams={}
    #print(Fore.GREEN+Style.BRIGHT+'\n' + u + Style.RESET_ALL)
    r = self.session.get(u, headers = self.headers(), params={**defparams,**params})
    return json.loads(r.text)

  def post_api_v3(self, method, data={}, params={}):
    u = f'https://api.nixplay.com/v3/{method}'
    defparams={}
    
    hdrs = self.headers()#{'Content-Type' : 'application/json' }
    #**self.headers(), 

    # preflight??? 
    r = self.session.options(u, headers=hdrs)
    print(r.status_code)
    #r = self.session.options(u, headers = hdrs)
    #print(r.status_code)
    #https://api.nixplay.com/v3/playlists/3201700/items
    r = self.session.post(u, headers = hdrs, data=json.dumps(data))  #params={**defparams,**params}, 
    print(r.request.url)
    print(r.request.headers)
    print(r.request.body)
    #print(r.status_code)
    return r

  #
  # NixPlay API
  #

  def getOnlineStatus(self):
    return self.get_api_v3('frame/online-status/')

  def getFrames(self):
    return self.get_api_v3('frames')

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

  #
  # Social / Flickr API
  #

  def flickr_people_getPhotos(self, page=1):
    return self.flickr_api('flickr.people.getPhotos', {'photoset_id': photoset_id, 'page': page, 'per_page':1, 'user_id':'me', 'extras':'url_m,url_o'})
   
  def flickr_photosets_getPhotos(self, photoset_id,page=1):
    return self.flickr_api('flickr.photosets.getPhotos', {'photoset_id': photoset_id, 'page': page, 'per_page':100, 'extras':'url_m,url_k,url_o,date_upload,last_update'})

  def flickr_photosets_getList(self, page=1):
    #primary_photo_extras=url_m,url_o
    return self.flickr_api('flickr.photosets.getList', {'page': page, 'per_page': 100})

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

  def flickr_favorites_getList(self, page=1):
    #primary_photo_extras=url_m,url_o
    return self.flickr_api('flickr.favorites.getList', {'page': page, 'per_page': 100})
