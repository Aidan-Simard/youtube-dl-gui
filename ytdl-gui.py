import threading
import tkinter as tk
import youtube_dl
from tkinter.scrolledtext import ScrolledText
import os
import queue

class App(tk.Frame):
    def __init__(self, master=None):
        '''
        (App, tk)->None
        Initializes the gui
        '''

        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.pathDir = os.path.dirname(os.path.realpath(__file__))
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': '{}....\\bin'.format(self.pathDir)
        }

    def create_widgets(self):
        '''
        (App)->None
        Creates the widgets for the GUI
        '''

        # create label for video input
        self.title = tk.Label(self, justify=tk.CENTER, text="Input youtube link on each line", font=("", 15))
        self.title.pack(pady=(5, 0))

        # create multiline text box
        self.input = ScrolledText(self, height=10, width=100)
        self.input.pack(side="top", pady=(5, 5), padx=10)

        # create label for directory input
        self.dirLabel = tk.Label(self, justify=tk.CENTER, text="Input full path below", font=("", 15))
        self.dirLabel.pack(pady=(0, 5))

        # create the directory text box
        self.directory = tk.Text(self, height=1, width=50)
        self.directory.pack(padx=10)

        # create the button
        self.b = tk.Button(self, text="Download MP3", command=lambda: self.get_input(self.input, self.directory))
        self.b.pack(pady=20, padx=5)

        # create an output box
        self.output = tk.Text(self, height=10, width=100)
        self.output.pack(padx=10)

    def get_input(self, text, directory):
        '''
        (App, string, string)->None
        Gets the input from the text fields and calls the parse_links method
        '''

        # get all text fields
        t = text.get("1.0", "end-1c")
        d = directory.get("1.0", "end-1c")
        
        # run AudioDownloader
        self.queue = queue.Queue()
        AudioDownloader(self.queue, t, d).start()

    def addToOutput(self, text):
        '''(App, string)->None
        Adds the given text to the output text field in the GUI'''
        self.output.configure(state="normal")
        self.output.insert(tk.END, text+"\n")
        self.output.configure(state="disable")

class AudioDownloader(threading.Thread):
    def __init__(self, queue, text, directory):
        threading.Thread.__init__(self)
        self.queue = queue
        self.text = text
        self.directory = directory
        self.pathDir = os.path.dirname(os.path.realpath(__file__))
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': '{}\\bin'.format(self.pathDir)
        }

    def run(self):
        '''
        (AudioDownloader)->None
        Run the youtube-dl downloader
        '''
        # update the download directory
        if self.directory != "" or self.d != None:
            self.ydl_opts["outtmpl"] = '{}\\%(title)s.%(ext)s'.format(self.directory)

        else:
            self.ydl_opts["outtmpl"] = '{}\\%(title)s.%(ext)s'.format(self.pathDir)

        self.parse_links(self.text)

    def parse_links(self, text):
        '''
        (AudioDownloader, string)->string
        Will loop through all links and download all valid links to the provided directory
        '''
        text = text.split('\n')

        for link in text:
            if self.isValidLink(link):
                urlId = self.getLinkId(link)

                if urlId == None:
                    app.addToOutput("A youtube video ID for {} could not be found.".format(link))

                else:
                    self.download_video(urlId)

            else:
                app.addToOutput("The link {} is not valid.".format(link))

    def getLinkId(self, link):
        '''
        (AudioDownloader, string)->string
        Gets the id at the end of the youtube link
        '''
        for c in range(len(link)-1, 0, -1):
            if link[c] == '=':
                return link[c+1:]

        return None

    def isValidLink(self, link):
        '''
        (AudioDownloader, string)->boolean
        Determines if the given link is of the form of a youtube link.
        Will also determine if the link corresponds to a youtube video.
        '''
        link = link.split('.')

        # a couple of checks to see if the link is real by checking url components
        if link[1] != "youtube":
            return False

        elif link[2][:12] != "com/watch?v=":
            return False

        else:
            return True

    def download_video(self, urlid):
        '''
        (AudioDownloader, string)->None
        Downloads the youtube video given by the video url ID
        '''
        try:
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                tmp = ydl.extract_info("https://www.youtube.com/watch?v="+urlid, download=True).get("title", None)
                app.output.after(1500, app.addToOutput(tmp+" has been downloaded successfully."))

        except:
            app.addToOutput("Youtube-dl could not download your video")

root = tk.Tk()
root.geometry("800x500")
root.title("Youtube to MP3 GUI")
app = App(master=root)
app.mainloop()
