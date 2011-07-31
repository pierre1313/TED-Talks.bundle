import re
from string import ascii_uppercase

###################################################################################################

PLUGIN_TITLE     = "TED talks"
VIDEO_PREFIX     = "/video/TED"

TED_BASE         = "http://www.ted.com"
TED_TALKS_FILTER = "http://www.ted.com/talks/browse.json?tagid=%s&orderedby=%s"
TED_THEMES       = "http://www.ted.com/themes/atoz"
TED_TAGS         = "http://www.ted.com/talks/tags"
TED_SPEAKERS     = "http://www.ted.com/speakers/atoz/page/%d"

MEDIA_NS         = {'media':'http://search.yahoo.com/mrss/'}

YT_VIDEO_PAGE    = "http://www.youtube.com/watch?v=%s"
YT_GET_VIDEO_URL = "http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=%d&asv=3"
YT_VIDEO_FORMATS = ['Standard', 'Medium', 'High', '720p', '1080p']
YT_FMT           = [34, 18, 35, 22, 37]

# Default artwork and icon(s)
TED_ART          = "art-default.jpg"
TED_THUMB        = "icon-default.jpg"

###################################################################################################

def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, PLUGIN_TITLE, TED_THUMB, TED_ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

  ObjectContainer.art       = R(TED_ART)
  ObjectContainer.title1    = PLUGIN_TITLE
  objectContainer.view_group = "InfoList"
  DirectoryObject.thumb      = R(TED_THUMB)

  HTTP.CacheTime = CACHE_1DAY
  HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"

####################################################################################################

def VideoMainMenu():
  oc = ObjectContainer(view_group="List")

  oc.add(Function(DirectoryObject(FrontPageList, "Front Page")))
  oc.add(Function(DirectoryObject(ThemeList, "Themes")))
  oc.add(Function(DirectoryObject(TagsList, "Tags")))
  oc.add(Function(DirectoryObject(SpeakersAZ, "Speakers")))

  return oc

####################################################################################################

def SpeakersAZ(sender):
  oc = ObjectContainer(title2=sender.itemTitle, view_group="List")

  # A to Z
  for char in list(ascii_uppercase):
    oc.add(Function(DirectoryObject(SpeakersList, title=char), char=char))

  return oc

####################################################################################################

def SpeakersList(sender, char, page=1):
  oc = ObjectContainer(title2=sender.itemTitle, view_group="List")

  content = HTML.ElementFromURL(TED_SPEAKERS % (page), cacheTime=CACHE_1WEEK)

  letter_list = content.xpath('//h3[text()="' + char + '"]/following-sibling::ul')
  if len(letter_list) == 1:
    for speaker in letter_list[0].xpath('./li/a'):
      speaker_name = speaker.text.split(" ", 1)
      speaker_name.reverse()
      speaker_name = ", ".join(speaker_name)
      speaker_name = speaker_name.strip(", ")
      url = TED_BASE + speaker.get('href')

      oc.add(Function(DirectoryObject(SpeakerTalks, title=speaker_name, thumb=Function(Photo, url=url)), url=url))

    if len( content.xpath('//a[@class="next"]') ) > 0:
      oc.Extend(SpeakersList(sender, char, page=page+1))

  elif len( content.xpath('//a[@class="next"]') ) > 0:
    oc = SpeakersList(sender, char, page=page+1)

  if len(oc) == 0:
    return MessageContainer("Empty", "There aren't any speakers whose name starts with " + char)

  return oc

####################################################################################################

def SpeakerTalks(sender, url):
  oc = ObjectContainer(title2=sender.itemTitle,httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))

  content = HTML.ElementFromURL(url).xpath('//dl[@class="box clearfix"]')
  for talk in content:
    title = talk.xpath('.//h4/a')[0].text
    url = TED_BASE + talk.xpath('.//h4/a')[0].get('href')
    timecode = talk.xpath('.//em')[0].text.split(" Posted: ")[0]
    duration = CalculateDuration(timecode)
    date = Datetime.ParseDate(talk.xpath('.//em')[0].text.split(" Posted: ")[1]).date()
    thumb = talk.xpath('.//img')[1].get('src')
  ########### Confrim proper way to add VideoObjects ########
    oc.add(Function(VideoItem(PlayVideo, title=title, originally_available_at=date, duration=duration, thumb=Function(Thumb, url=thumb)), url=url))

  if len(dir) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return oc

####################################################################################################

def FrontPageList(sender):
  oc = ObjectContainer(title2=sender.itemTitle, view_group="List")

  oc.add(Function(DirectoryObject(FrontPageSort, "Technology"), id=20))
  oc.add(Function(DirectoryObject(FrontPageSort, "Entertainment"), id=25))
  oc.add(Function(DirectoryObject(FrontPageSort, "Design"), id=26))
  oc.add(Function(DirectoryObject(FrontPageSort, "Business"), id=21))
  oc.add(Function(DirectoryObject(FrontPageSort, "Science"), id=24))
  oc.add(Function(DirectoryObject(FrontPageSort, "Global issues"), id=28))
  oc.add(Function(DirectoryObject(FrontPageSort, "All"), id=None))

  return oc

####################################################################################################

def FrontPageSort(sender, id):
  oc = MediaContainer(title2=sender.itemTitle, view_group="List")
  if id == None:
    id_s = ''
  else:
    id_s = str(id)
    
  oc.add(Function(DirectoryObject(GetTalks, "Newest releases"), url=TED_TALKS_FILTER % (id_s, "NEWEST") ))
  oc.add(Function(DirectoryObject(GetTalks, "Most languages"), url=TED_TALKS_FILTER % (id_s, "MOSTTRANSLATED") ))
  oc.add(Function(DirectoryObject(GetTalks, "Most emailed this week"), url=TED_TALKS_FILTER % (id_s, "MOSTEMAILED") ))
  oc.add(Function(DirectoryObject(GetTalks, "Most comments this week"), url=TED_TALKS_FILTER % (id_s, "MOSTDISCUSSED") ))
  oc.add(Function(DirectoryObject(GetTalks, "Rated jaw-dropping"), url=TED_TALKS_FILTER % (id_s, "JAW-DRAPPING") ))
  oc.add(Function(DirectoryObject(GetTalks, "... persuasive"), url=TED_TALKS_FILTER % (id_s, "PERSUASIVE") ))
  oc.add(Function(DirectoryObject(GetTalks, "... courageous"), url=TED_TALKS_FILTER % (id_s, "COURAGEOUS") ))
  oc.add(Function(DirectoryObject(GetTalks, "... ingenious"), url=TED_TALKS_FILTER % (id_s, "INGENIOUS") ))
  oc.add(Function(DirectoryObject(GetTalks, "... fascinating"), url=TED_TALKS_FILTER % (id_s, "FASCINATING") ))
  oc.add(Function(DirectoryObject(GetTalks, "... inspiring"), url=TED_TALKS_FILTER % (id_s, "INSPIRING") ))
  oc.add(Function(DirectoryObject(GetTalks, "... beautiful"), url=TED_TALKS_FILTER % (id, "BEAUTIFUL") ))
  oc.add(Function(DirectoryObject(GetTalks, "... funny"), url=TED_TALKS_FILTER % (id_s, "FUNNY") ))
  oc.add(Function(DirectoryObject(GetTalks, "... informative"), url=TED_TALKS_FILTER % (id_s, "INFORMATIVE") ))

  return oc

####################################################################################################

def ThemeList(sender):
  oc = ObjectContainer(title2=sender.itemTitle, view_group="List")

  content = HTML.ElementFromURL(TED_THEMES)
  for theme in content.xpath('//div[@id="maincontent"]//a'):
    try:
      title = theme.text
      url = TED_BASE + theme.get('href')
      oc.add(Function(DirectoryObject(Theme, title=title, thumb=Function(Photo, url=url)), url=url))
    except:
      pass
    
  return oc

####################################################################################################

def Theme(sender, url):
  oc = ObjectContainer(title2=sender.itemTitle, view_group="List",httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))
  try:
    rss_url = HTML.ElementFromURL(url).xpath('//link[@rel="alternate"]')[0].get('href')
    content = XML.ElementFromURL(rss_url, errors='ignore')
  except:
    return MessageContainer("Error", "The link for this entry appears to be broken")

  for item in content.xpath("//item"):
    title = item.xpath('./title')[0].text
    url = item.xpath('./link')[0].text
    summary = String.StripTags( item.xpath('./description')[0].text )
    date = Datetime.ParseDate(item.xpath('./pubDate')[0].text).date()
    try:
      thumb = item.xpath('./media:thumbnail', namespaces=MEDIA_NS)[0].get('url')
    except:
      thumb = None
  ########### Confrim proper way to add VideoObjects ########
    oc.add(Function(VideoItem(PlayVideo, title=title, originally_available_at=date, summary=summary, thumb=Function(Thumb, url=thumb)), url=url))

  if len(dir) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return oc

####################################################################################################

def TagsList(sender):
  oc = ObjectContainer(title2=sender.itemTitle, view_group="List")

  content = HTML.ElementFromURL(TED_TAGS)
  for tag in content.xpath('//div[@id="maincontent"]//a'):
    title = tag.text
    url = TED_BASE + tag.get('href')
    oc.add(Function(DirectoryObject(Tag, title=title), url=url))

  return oc

####################################################################################################

def Tag(sender, url):
  oc = ObjectContainer(title2=sender.itemTitle, view_group="List",httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))
  current_page = HTML.ElementFromURL(url)
  try:
    prevpage = current_page.xpath("//div[@class='pagination clearfix']")[0]
    try: 
      oc.add(Function(DirectoryObject(Tag, title="Previous Page"), url=TED_BASE + prevpage.xpath(".//a[@class='previous']")[0].get('href')))
    except:
      pass
    for item in HTML.ElementFromURL(url).xpath("//dl[@class='clearfix']"):
      title = item.xpath('./dd//a')[0].text
      url = TED_BASE + item.xpath('./dd//a')[0].get('href')
      summary= None
      date = None
      try:
	thumb = item.xpath('./dt//img[@alt="Talk image"]')[0].get('src')
      except:
	thumb = None
      ########### Confrim proper way to add VideoObjects ########
      oc.add(Function(VideoItem(PlayVideo, title=title, originally_available_at=date, summary=summary, thumb=Function(Thumb, url=thumb)), url=url))
      nextpage = current_page.xpath("//div[@class='pagination clearfix']")[0]
      try: 
	oc.add(Function(DirectoryObject(Tag, title="Next Page"), url=TED_BASE + prevpage.xpath(".//a[@class='next']")[0].get('href')))
      except:
	pass
  except:
    pass    
  if len(oc) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return oc

####################################################################################################    

def GetTalks(sender, url):
  oc = ObjectContainer(title2=sender.itemTitle,httpCookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))

  talks = JSON.ObjectFromURL(url)['main']
  for talk in talks:
    title = talks[str(talk)]['tTitle']
    date = Datetime.ParseDate(talks[str(talk)]['talkpDate']).daet() # Post date
    if talks[str(talk)]['altTitle'] != talks[str(talk)]['tTitle']:
      summary = String.StripTags( talks[str(talk)]['altTitle'] + '\n\n' + talks[str(talk)]['blurb'] )
    else:
      summary = String.StripTags( talks[str(talk)]['blurb'] )
    timecode = talks[str(talk)]['talkDuration']
    duration = CalculateDuration(timecode)
    thumb = str(talks[str(talk)]['image']) + "_240x180.jpg"
    url = TED_BASE + talks[str(talk)]['talkLink']

    dir.Append(Function(VideoItem(PlayVideo, title=title, originally_available_at=date, duration=duration, summary=summary, thumb=Function(Thumb, url=thumb)), url=url))
  
  if len(oc) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return oc

####################################################################################################


######## Implement URL Service Call(s) ########
def PlayVideo(sender, url):
  video_url = None

  videoList = HTML.ElementFromURL(url, cacheTime=7200, errors='ignore')
  
  try:
    video_url = videoList.xpath('.//dl[@class="downloads"]/dt/a')[2].get('href')
  except:
    try:
      yt_url = HTML.ElementFromURL(url, cacheTime=CACHE_1WEEK).xpath('//embed[contains(@src, "youtube.com")]')[0].get('src')
      video_id = re.search('v/(.{11})', yt_url).group(1)
      video_url = YoutubeUrl(video_id)
    except:
      try:
        yt_url = HTML.ElementFromURL(url, cacheTime=CACHE_1WEEK).xpath('//a[contains(@href, "youtube.com")]')[0].get('href')
        video_id = re.search('v=(.{11})', yt_url).group(1)
        video_url = YoutubeUrl(video_id)
      except:
        try:
          ted_streaming_el = HTML.ElementFromURL(url, cacheTime=CACHE_1WEEK).xpath("//div[@class='save clearfix']")[0]
          video_url = re.search('vu=(http://video.ted.com.*?flv)', HTML.StringFromElement(ted_streaming_el)).group(1)
        except:
	  try:
	    yt_url = HTML.ElementFromURL(url, cacheTime=CACHE_1WEEK).xpath('//param[contains(@value, "youtube.com")]')[0].get('value')
	    video_id = re.search('v/(.{11})', yt_url).group(1)
	    video_url = YoutubeUrl(video_id)
	  except:
	    Log(HTTP.Request(url).content)
	    pass

  return Redirect(video_url)

####################################################################################################

def Photo(url):
  try:
    photo_url = HTML.ElementFromURL(url).xpath('//link[@rel="image_src"]')[0].get('href')
    data = HTTP.Request(photo_url, cacheTime=CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(TED_THUMB))

####################################################################################################

def Thumb(url):
  if url:
    try:
      data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
      return DataObject(data, 'image/jpeg')
    except:
      pass
  return Redirect(R(TED_THUMB))

####################################################################################################

def CalculateDuration(timecode):
  milliseconds = 0
  d = re.search('([0-9]{1,2}):([0-9]{2})', timecode)
  milliseconds += int( d.group(1) ) * 60 * 1000
  milliseconds += int( d.group(2) ) * 1000
  return milliseconds

####################################################################################################

def YoutubeUrl(video_id, quality='1080p'):
  yt_page = HTTP.Request(YT_VIDEO_PAGE % video_id, cacheTime=1).content
  
  fmt_url_map = re.findall('"fmt_url_map".+?"([^"]+)', yt_page)[0]
  fmt_url_map = fmt_url_map.replace('\/', '/').split(',')

  fmts = []
  fmts_info = {}

  for f in fmt_url_map:
    (fmt, url) = f.split('|')
    fmts.append(fmt)
    fmts_info[str(fmt)] = url

  index = YT_VIDEO_FORMATS.index(quality)

  if YT_FMT[index] in fmts:
    fmt = YT_FMT[index]
  else:
    for i in reversed( range(0, index+1) ):
      if str(YT_FMT[i]) in fmts:
        fmt = YT_FMT[i]
        break
      else:
        fmt = 5

  url = (fmts_info[str(fmt)]).decode('unicode_escape')
  Log("  VIDEO URL --> " + url)
  return url

####################################################################################################

