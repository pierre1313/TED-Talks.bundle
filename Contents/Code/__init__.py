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
  ObjectContainer.view_group = "InfoList"
  DirectoryObject.thumb      = R(TED_THUMB)

  HTTP.CacheTime = CACHE_1DAY
  HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"

####################################################################################################

def VideoMainMenu():
  oc = ObjectContainer(view_group="List")

  oc.add(DirectoryObject(key=Callback(FrontPageList, name="Front Page"), title="Front Page"))
  oc.add(DirectoryObject(key=Callback(ThemeList, name="Themes"), title="Themes"))
  oc.add(DirectoryObject(key=Callback(TagsList, name="Tags"), title="Tags"))
  oc.add(DirectoryObject(key=Callback(SpeakersAZ, name="Speakers"), title="Speakers"))

  return oc

####################################################################################################

def SpeakersAZ(name):
  oc = ObjectContainer(title2=name, view_group="List")

  # A to Z
  for char in list(ascii_uppercase):
    oc.add(DirectoryObject(key=Callback(SpeakersList, char=char), title=char))

  return oc

####################################################################################################

def SpeakersList(char, page=1):
  oc = ObjectContainer(title2=char, view_group="List")

  i = page
  content = HTML.ElementFromURL(TED_SPEAKERS % (i), cacheTime=CACHE_1WEEK)
  
  while len(content.xpath('//a[@class="next"]')) > 0:
    content = HTML.ElementFromURL(TED_SPEAKERS % (i), cacheTime=CACHE_1WEEK)
    letter_list = content.xpath('//h3[text()="' + char + '"]/following-sibling::ul')
    i = i+1
    if len(letter_list) == 1:
      for speaker in letter_list[0].xpath('./li/a'):
        speaker_name = speaker.text.split(" ", 1)
        speaker_name.reverse()
        speaker_name = ", ".join(speaker_name)
        speaker_name = speaker_name.strip(", ")
        url = TED_BASE + speaker.get('href')

        oc.add(DirectoryObject(key=Callback(SpeakerTalks, name=speaker_name, url=url), title=speaker_name, thumb=Callback(Photo, url=url)))

    #if len( content.xpath('//a[@class="next"]') ) > 0:
      #oc.add(DirectoryObject(key=Callback(SpeakersList, char=char, page=page+1), title="Next page"))
    # oc.extend(SpeakersList(char=char, page=page+1))

  #elif len( content.xpath('//a[@class="next"]') ) > 0:
  #  oc = SpeakersList(char, page=page+1)
  #  pass

  if len(oc) == 0:
    return MessageContainer("Empty", "There aren't any speakers whose name starts with " + char)

  return oc

####################################################################################################

def SpeakerTalks(name, url):
  oc = ObjectContainer(title2=name)

  content = HTML.ElementFromURL(url).xpath('//dl[@class="box clearfix"]')
  for talk in content:
    title = talk.xpath('.//h4/a')[0].text
    url = TED_BASE + talk.xpath('.//h4/a')[0].get('href')
    timecode = talk.xpath('.//em')[0].text.split(" Posted: ")[0]
    duration = CalculateDuration(timecode)
    date = Datetime.ParseDate(talk.xpath('.//em')[0].text.split(" Posted: ")[1]).date()
    thumb = talk.xpath('.//img')[1].get('src')
    oc.add(VideoClipObject(url=url, title=title, originally_available_at=date, duration=duration, thumb=Function(Thumb, url=thumb)))

  if len(oc) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return oc

####################################################################################################

def FrontPageList(name):
  oc = ObjectContainer(title2=name, view_group="List")

  oc.add(DirectoryObject(key=Callback(FrontPageSort, name="Technology", id=20), title="Technology"))
  oc.add(DirectoryObject(key=Callback(FrontPageSort, name="Entertainment", id=25), title="Entertainment"))
  oc.add(DirectoryObject(key=Callback(FrontPageSort, name="Design", id=26), title="Design"))
  oc.add(DirectoryObject(key=Callback(FrontPageSort, name="Business", id=21), title="Business"))
  oc.add(DirectoryObject(key=Callback(FrontPageSort, name="Science", id=24), title="Science"))
  oc.add(DirectoryObject(key=Callback(FrontPageSort, name="Global issues", id=28), title="Global issues"))
  oc.add(DirectoryObject(key=Callback(FrontPageSort, name="All", id=None), title="All"))

  return oc

####################################################################################################

def FrontPageSort(name, id):
  oc = ObjectContainer(title2=name, view_group="List")
  if id == None:
    id_s = ''
  else:
    id_s = str(id)
    
  oc.add(DirectoryObject(key=Callback(GetTalks, name="Newest releases", url=TED_TALKS_FILTER % (id_s, "NEWEST")), title="Newest releases"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="Most languages", url=TED_TALKS_FILTER % (id_s, "MOSTTRANSLATED")), title="Most languages"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="Most emailed this week", url=TED_TALKS_FILTER % (id_s, "MOSTEMAILED")), title="Most emailed this week"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="Most comments this week", url=TED_TALKS_FILTER % (id_s, "MOSTDISCUSSED")), title="Most comments this week"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="Rated jaw-dropping", url=TED_TALKS_FILTER % (id_s, "JAW-DRAPPING")), title="Rated jaw-dropping"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="... persuasive", url=TED_TALKS_FILTER % (id_s, "PERSUASIVE")), title="... persuasive"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="... courageous", url=TED_TALKS_FILTER % (id_s, "COURAGEOUS")), title="... courageous"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="... ingenious", url=TED_TALKS_FILTER % (id_s, "INGENIOUS")), title="... ingenious"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="... fascinating", url=TED_TALKS_FILTER % (id_s, "FASCINATING")), title="... fascinating"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="... inspiring", url=TED_TALKS_FILTER % (id_s, "INSPIRING")), title="... inspiring"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="... beautiful", url=TED_TALKS_FILTER % (id, "BEAUTIFUL")), title="... beautiful"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="... funny", url=TED_TALKS_FILTER % (id_s, "FUNNY")), title="... funny"))
  oc.add(DirectoryObject(key=Callback(GetTalks, name="... informative", url=TED_TALKS_FILTER % (id_s, "INFORMATIVE")), title="... informative"))

  return oc

####################################################################################################

def ThemeList(name):
  oc = ObjectContainer(title2=name, view_group="List")

  content = HTML.ElementFromURL(TED_THEMES)
  for theme in content.xpath('//div[@id="maincontent"]//a'):
    try:
      title = theme.text
      url = TED_BASE + theme.get('href')
      oc.add(DirectoryObject(key=Callback(Theme, name=title, url=url), title=title, thumb=Callback(Photo, url=url)))
    except:
      pass
    
  return oc

####################################################################################################

def Theme(name, url):
  oc = ObjectContainer(title2=name, view_group="List")
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
    oc.add(VideoClipObject(url=url, title=title, originally_available_at=date, summary=summary, thumb=Callback(Thumb, url=thumb)))

  if len(oc) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return oc

####################################################################################################

def TagsList(name):
  oc = ObjectContainer(title2=name, view_group="List")

  content = HTML.ElementFromURL(TED_TAGS)
  for tag in content.xpath('//div[@id="maincontent"]//a'):
    title = tag.text
    url = TED_BASE + tag.get('href')
    oc.add(DirectoryObject(key=Callback(Tag, name=title, url=url), title=title))

  return oc

####################################################################################################

def Tag(name, url):
  oc = ObjectContainer(title2=name, view_group="List", http_cookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))
  current_page = HTML.ElementFromURL(url)
  try:
    prevpage = current_page.xpath("//div[@class='pagination clearfix']")[0]
    try: 
      oc.add(DirectoryObject(key=Callback(Tag, name=name, url=TED_BASE + prevpage.xpath(".//a[@class='previous']")[0].get('href')), title="Previous Page"))
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
      oc.add(VideoClipObject(url=url, title=title, originally_available_at=date, summary=summary, thumb=Callback(Thumb, url=thumb)))
      nextpage = current_page.xpath("//div[@class='pagination clearfix']")[0]
      try: 
	oc.add(DirectoryObject(key=Callback(Tag, name=name, url=TED_BASE + prevpage.xpath(".//a[@class='next']")[0].get('href')), title="Next Page"))
      except:
	pass
  except:
    pass    
  if len(oc) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return oc

####################################################################################################    

def GetTalks(name, url):
  oc = ObjectContainer(title2=name, http_cookies=HTTP.GetCookiesForURL('http://www.youtube.com/'))

  talks = JSON.ObjectFromURL(url)['main']
  for talk in talks:
    title = talks[str(talk)]['tTitle']
    date = Datetime.ParseDate(talks[str(talk)]['talkpDate']).date() # Post date
    if talks[str(talk)]['altTitle'] != talks[str(talk)]['tTitle']:
      summary = String.StripTags( talks[str(talk)]['altTitle'] + '\n\n' + talks[str(talk)]['blurb'] )
    else:
      summary = String.StripTags( talks[str(talk)]['blurb'] )
    timecode = talks[str(talk)]['talkDuration']
    duration = CalculateDuration(timecode)
    thumb = str(talks[str(talk)]['image']) + "_240x180.jpg"
    url = TED_BASE + talks[str(talk)]['talkLink']

    oc.add(VideoClipObject(url=url, title=title, originally_available_at=date, duration=duration, summary=summary, thumb=Callback(Thumb, url=thumb)))
  
  if len(oc) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return oc

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


