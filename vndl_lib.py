from __future__ import print_function
from __future__ import division
from selenium import webdriver
import time
import sys
import os.path
import requests

# Open a new Chrome browser
def init_browser() :
    return webdriver.Chrome()

# Close the browser and end process
def destroy_browser(browser) :
    browser.quit()

# Return a string showing download speed given bps
def progressBar(bps, bar_size, total_downloaded, total_size) :
  bytesPerSec = int(bps)/8
  #print("bps: " + str(bps) + "   Bps: " + str(bytesPerSec))
  speed = "?? B/s"
  if (bytesPerSec < 1000.0):
    speed = str(round(bytesPerSec, 2)) + " B/s"
  elif (bytesPerSec < 100000):
    speed = str(round(bytesPerSec/1000.0, 2)) + " KB/s"
  else:
    speed = str(round(bytesPerSec/1000000.0, 2)) + " MB/s "

  percent_done = total_downloaded/total_size
  num_bars = bar_size*percent_done
  print("[" + "="*int(num_bars) + " "*int(bar_size-num_bars) + "] " + str(round(percent_done*100, 2)) + "%  Speed: " + speed, end="\r")

# Thanks stackoverflow
def sanitizeFilename(filename) :
    keepcharacters = (' ','.','_')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

# Download a file from a uri into directory/filename
def downloadFile(url, directory, filename) :
  with open(directory + '/' + filename, 'wb') as f:
    start = time.clock()
    r = requests.get(url, stream=True)
    total_length = int(r.headers.get('content-length'))
    dl = 0
    if total_length is None: # no content length header
      f.write(r.content)
    else:
      for chunk in r.iter_content(1024*256):
        dl += len(chunk)
        f.write(chunk)
        progressBar(dl/(time.clock()-start), 25, dl, total_length)
  return (time.clock() - start)

# Log into videonote given cornell user (netid), and password
def videonote_login(browser, user, password) :
    # Log into videonote
    browser.get('http://cornell.videonote.com/login')
    browser.find_element_by_css_selector('.btn-info').click() # click "Cornell Web Login"
    browser.implicitly_wait(3)
    browser.find_element_by_id('netid').send_keys(user) # enter username
    browser.find_element_by_id('password').send_keys(password) # enter password
    browser.find_element_by_css_selector('.input-submit').click() # submit login form

    time.sleep(3)

# Download a video embedded in the page
def download_video(browser, directory, filename) :
    browser.set_script_timeout(10)
    time.sleep(3) # wait for page to load
    video = browser.find_element_by_id('videonote-videojs-player_html5_api')
    mp4_url = video.get_attribute('src')
    downloadFile(mp4_url, directory, filename+".mp4");

# Grab a list of videos on the page (MUST BE IN CLASS PAGE)
def get_video_list(browser) :
    videos = []
    for a in browser.find_elements_by_tag_name('a'):
      if (a.get_attribute('ng-click') == "$ctrl.goTo()"):
        videos.append(a)
    return videos

# Download a video from a class (called when in CLASS PAGE)
def download_class_video(browser, video_id, directory) :
    videos = get_video_list(browser)
    to_download = videos[video_id]
    video_name = sanitizeFilename(str(to_download.text))
    if (os.path.isfile(directory + '/' + video_name + ".mp4")):
      print("Skipping: " + video_name + " ... file already exists!")
      return 0
    print("Downloading: " + video_name)
    to_download.click()
    time.sleep(3)
    download_video(browser, directory, video_name)
    return 1

# Download all the videos in a given class
def download_class(browser, directory, class_number) :
    browser.get('http://cornell.videonote.com/channels/' + str(class_number) + '/videos') # test
    time.sleep(3)
    num_videos = len(get_video_list(browser))
    for i in range(1, num_videos) :
        if (download_class_video(browser, num_videos - i, directory) == 1):
            browser.get('http://cornell.videonote.com/channels/' + str(class_number) + '/videos') # test
            time.sleep(3)
