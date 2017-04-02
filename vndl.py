# VNDL - Videonote Downloader by Nick Sarkis
#
# Instructions:
#   - Enter your netid and password when requested
#   - You will be logged in and brought to the videonote class page,
#     find the class you want to download, and give the id in the url
#     when asked to "Enter class number:"
#   - Select the destination to download the videos
#   - Wait until all videos are downloaded!


from Tkinter import Tk
from tkFileDialog import askdirectory
import vndl_lib as vndl
import getpass

browser = vndl.init_browser()
user = raw_input("Cornell netid: ")
password = getpass.getpass("Password: ")
vndl.videonote_login(browser, user, password)
class_num = int(raw_input("Enter class number: "))
Tk().withdraw()
path = askdirectory()
print("Downloading videos to: " + path)
vndl.download_class(browser, path, class_num)
destory_browser(browser)
