import re
from string import ascii_uppercase

###################################################################################################

PLUGIN_TITLE     = "TED talks"
VIDEO_PREFIX     = "/video/TED"

TED_BASE         = "http://www.ted.com"
TED_TALKS_FILTER = "http://www.ted.com/talks/searchRpc?tagid=%d&orderedby=%s"
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

  MediaContainer.art       = R(TED_ART)
  MediaContainer.title1    = PLUGIN_TITLE
  MediaContainer.viewGroup = "InfoList"
  DirectoryItem.thumb      = R(TED_THUMB)

  HTTP.CacheTime = CACHE_1DAY
  HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"

####################################################################################################

def VideoMainMenu():
  dir = MediaContainer(viewGroup="List")

  dir.Append(Function(DirectoryItem(FrontPageList, "Front Page")))
  dir.Append(Function(DirectoryItem(ThemeList, "Themes")))
  dir.Append(Function(DirectoryItem(TagsList, "Tags")))
  dir.Append(Function(DirectoryItem(SpeakersAZ, "Speakers")))

  return dir

####################################################################################################

def SpeakersAZ(sender):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")

  # A to Z
  for char in list(ascii_uppercase):
    dir.Append(Function(DirectoryItem(SpeakersList, title=char), char=char))

  return dir

####################################################################################################

def SpeakersList(sender, char, page=1):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")

  content = HTML.ElementFromURL(TED_SPEAKERS % (page), cacheTime=CACHE_1WEEK)

  letter_list = content.xpath('//h3[text()="' + char + '"]/following-sibling::ul')
  if len(letter_list) == 1:
    for speaker in letter_list[0].xpath('./li/a'):
      speaker_name = speaker.text.split(" ", 1)
      speaker_name.reverse()
      speaker_name = ", ".join(speaker_name)
      speaker_name = speaker_name.strip(", ")
      url = TED_BASE + speaker.get('href')

      dir.Append(Function(DirectoryItem(SpeakerTalks, title=speaker_name, thumb=Function(Photo, url=url)), url=url))

    if len( content.xpath('//a[@class="next"]') ) > 0:
      dir.Extend(SpeakersList(sender, char, page=page+1))

  elif len( content.xpath('//a[@class="next"]') ) > 0:
    dir = SpeakersList(sender, char, page=page+1)

  if len(dir) == 0:
    return MessageContainer("Empty", "There aren't any speakers whose name starts with " + char)

  return dir

####################################################################################################

def SpeakerTalks(sender, url):
  dir = MediaContainer(title2=sender.itemTitle)

  content = HTML.ElementFromURL(url).xpath('//dl[@class="box clearfix"]')
  for talk in content:
    title = talk.xpath('.//h4/a')[0].text
    url = TED_BASE + talk.xpath('.//h4/a')[0].get('href')
    timecode = talk.xpath('.//em')[0].text.split(" Posted: ")[0]
    duration = CalculateDuration(timecode)
    subtitle = talk.xpath('.//em')[0].text.split(" Posted: ")[1]
    thumb = talk.xpath('.//img')[1].get('src')

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=subtitle, duration=duration, thumb=Function(Thumb, url=thumb)), url=url))

  if len(dir) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return dir

####################################################################################################

def FrontPageList(sender):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")

  dir.Append(Function(DirectoryItem(FrontPageSort, "Technology"), id=1))
  dir.Append(Function(DirectoryItem(FrontPageSort, "Entertainment"), id=2))
  dir.Append(Function(DirectoryItem(FrontPageSort, "Design"), id=3))
  dir.Append(Function(DirectoryItem(FrontPageSort, "Business"), id=4))
  dir.Append(Function(DirectoryItem(FrontPageSort, "Science"), id=5))
  dir.Append(Function(DirectoryItem(FrontPageSort, "Global issues"), id=7))
  dir.Append(Function(DirectoryItem(FrontPageSort, "All"), id=0))

  return dir

####################################################################################################

def FrontPageSort(sender, id):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")

  dir.Append(Function(DirectoryItem(GetTalks, "Newest releases"), url=TED_TALKS_FILTER % (id, "NEWEST") ))
  dir.Append(Function(DirectoryItem(GetTalks, "Most languages"), url=TED_TALKS_FILTER % (id, "MOSTTRANSLATED") ))
  dir.Append(Function(DirectoryItem(GetTalks, "Most emailed this week"), url=TED_TALKS_FILTER % (id, "MOSTEMAILED") ))
  dir.Append(Function(DirectoryItem(GetTalks, "Most comments this week"), url=TED_TALKS_FILTER % (id, "MOSTDISCUSSED") ))
  dir.Append(Function(DirectoryItem(GetTalks, "Most favorited of all-time"), url=TED_TALKS_FILTER % (id, "MOSTFAVORITED") ))
  dir.Append(Function(DirectoryItem(GetTalks, "Rated jaw-dropping"), url=TED_TALKS_FILTER % (id, "JAW-DRAPPING") ))
  dir.Append(Function(DirectoryItem(GetTalks, "... persuasive"), url=TED_TALKS_FILTER % (id, "PERSUASIVE") ))
  dir.Append(Function(DirectoryItem(GetTalks, "... courageous"), url=TED_TALKS_FILTER % (id, "COURAGEOUS") ))
  dir.Append(Function(DirectoryItem(GetTalks, "... ingenious"), url=TED_TALKS_FILTER % (id, "INGENIOUS") ))
  dir.Append(Function(DirectoryItem(GetTalks, "... fascinating"), url=TED_TALKS_FILTER % (id, "FASCINATING") ))
  dir.Append(Function(DirectoryItem(GetTalks, "... inspiring"), url=TED_TALKS_FILTER % (id, "INSPIRING") ))
  dir.Append(Function(DirectoryItem(GetTalks, "... beautiful"), url=TED_TALKS_FILTER % (id, "BEAUTIFUL") ))
  dir.Append(Function(DirectoryItem(GetTalks, "... funny"), url=TED_TALKS_FILTER % (id, "FUNNY") ))
  dir.Append(Function(DirectoryItem(GetTalks, "... informative"), url=TED_TALKS_FILTER % (id, "INFORMATIVE") ))

  return dir

####################################################################################################

def ThemeList(sender):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")

  content = HTML.ElementFromURL(TED_THEMES)
  for theme in content.xpath('//div[@id="maincontent"]//a'):
    title = theme.text
    url = TED_BASE + theme.get('href')
    dir.Append(Function(DirectoryItem(Theme, title=title, thumb=Function(Photo, url=url)), url=url))

  return dir

####################################################################################################

def Theme(sender, url):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")
  try:
    rss_url = HTML.ElementFromURL(url).xpath('//link[@rel="alternate"]')[0].get('href')
    content = XML.ElementFromURL(rss_url, errors='ignore')
  except:
    return MessageContainer("Error", "The link for this entry appeaas broken.")

  for item in content.xpath("//item"):
    title = item.xpath('./title')[0].text
    url = item.xpath('./link')[0].text
    summary = String.StripTags( item.xpath('./description')[0].text )
    date = Datetime.ParseDate(item.xpath('./pubDate')[0].text).strftime('%b %Y')
    try:
      thumb = item.xpath('./media:thumbnail', namespaces=MEDIA_NS)[0].get('url')
    except:
      thumb = None

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=summary, thumb=Function(Thumb, url=thumb)), url=url))

  if len(dir) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return dir

####################################################################################################

def TagsList(sender):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")

  content = HTML.ElementFromURL(TED_TAGS)
  for tag in content.xpath('//div[@id="maincontent"]//a'):
    title = tag.text
    id = int( tag.get('href').rsplit('/', 1)[1] )
    url = TED_TALKS_FILTER % (id, "NEWEST")

    dir.Append(Function(DirectoryItem(GetTalks, title=title), url=url))

  return dir

####################################################################################################    

def GetTalks(sender, url):
  dir = MediaContainer(title2=sender.itemTitle)

  talks = JSON.ObjectFromURL(url)['main']
  for talk in talks:
    title = talk['tTitle']
    subtitle = talk['talkpDate'] # Post date
    if talk['altTitle'] != talk['tTitle']:
      summary = String.StripTags( talk['altTitle'] + '\n\n' + talk['blurb'] )
    else:
      summary = String.StripTags( talk['blurb'] )
    timecode = talk['talkDuration']
    duration = CalculateDuration(timecode)
    thumb = str(talk['image']) + "_240x180.jpg"
    url = TED_BASE + talk['talkLink']

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=subtitle, duration=duration, summary=summary, thumb=Function(Thumb, url=thumb)), url=url))
  
  if len(dir) == 0 :
    return MessageContainer("Empty", "This category is empty")
  else:
    return dir

####################################################################################################

def PlayVideo(sender, url):
  video_url = None

  try:
    video_url = HTML.ElementFromURL(url, cacheTime=CACHE_1WEEK).xpath('//dl[@class="downloads"]//dt/a[contains(text(),"Watch")]')[0].get('href')
    video_url = TED_BASE + video_url
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

def YoutubeUrl(video_id, quality='720p'):
  yt_page = HTTP.Request(YT_VIDEO_PAGE % video_id, cacheTime=1).content

  t = re.findall('&t=([^&]+)', yt_page)[0]
  fmt_list = re.findall('&fmt_list=([^&]+)', yt_page)[0]
  fmt_list = String.Unquote(fmt_list, usePlus=False)
  fmts = re.findall('([0-9]+)[^,]*', fmt_list)

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

  url = YT_GET_VIDEO_URL % (video_id, t, fmt)
  return url
