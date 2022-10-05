from asyncore import read
from cProfile import label
from concurrent.futures import thread
from email.errors import MultipartInvariantViolationDefect
import imp
from msilib.schema import Font
from time import timezone
from tkinter.tix import IMAGE
from tkinter import Button, Label, messagebox
from tkinter.ttk import Combobox, Progressbar
from xmlrpc.server import resolve_dotted_attribute
import threading
from PIL import Image, ImageTk
from tkinter import filedialog
import pytube as pyyt
from pytube.cli import on_progress
import tkinter as gui
import urllib.request
import io

COLOR = "#FFFFFF"
GREY = "#495057"
DARK = "#212529"
HIGHLIGHT = "#ff0054"
FONT = "Montserrat"
# import yt_api



class Ui:
    def __init__(self) :

        # youtube request
        self.yt_result = None

        # Gui window
        self.tk = gui.Tk()

        # backgroud image (our backgroud is not a color but a image)  
        self.img = gui.PhotoImage(file ="My_youtube/background.png")
        # window size
        self.tk.geometry("800x320")

        # disable resizing
        self.tk.resizable(False, False)

        # gui title
        self.tk.title("YouTube Downloader")

        #file_dictor..
        self.filename = None

        # video Resolution
        self.res = ["720p",  "360p"]

        # video tag
        self.v_tag = None

        # background
        self.bg_img = gui.Label(image=self.img,)
        self.bg_img.place(x=0,y=0)

        # Canvas for the thumbnail
        self.canvas = gui.Canvas( width=400,height=200 )
        self.canvas.place(x= 30, y=80)

        # choose res
        self.stream = None

        # link
        self.link_btn = gui.Label(text="Youtube Link", font=(FONT), background=DARK, fg=COLOR)
        self.link_btn.place(x=30, y= 30)
        self.link_input = gui.Entry(width=40, background= DARK, font=(FONT,10), fg= COLOR)
        self.link_input.place(x=180, y= 35)


        # name
        self.video_name = gui.Label(text="Title:", font=(FONT), fg=COLOR, bg=DARK)
        self.video_name.place(x=450 , y= 80)
        self.got_title = gui.Label(text="No Video", font=(FONT, 10), fg=COLOR, bg=DARK, wraplength= 300)
        self.got_title.place(x=500, y= 85)

        # Size
        self.size_text = gui.Label(text="Size:", font=(FONT), fg=COLOR, bg=DARK)
        self.size_text.place(x = 450, y= 150)
        self.got_size = gui.Label(text="No Video", font=(FONT, 10), fg=COLOR, bg=DARK)
        self.got_size.place(x = 500, y= 155)


        #Download btn using Thread
        self.D_btn = gui.Button(text="Download", background=HIGHLIGHT,state="disabled", fg=COLOR , padx=20, pady=10, command=self.download_video)
        self.D_btn.place(x = 635, y = 27)

        # search button using Thread
        self.search_btn = gui.Button(text="Search", command=self.search_link , background=HIGHLIGHT, fg=COLOR , padx=20, pady=10)
        self.search_btn.place(x=550, y=27)
        

        # https://www.youtube.com/watch?v=DBIUeqkbCgI&list=PL_C6OPPIQyFgqmQYEyhvS1i_wNBlYZdgW&index=12

        # combo
        self.select_box = Combobox(values = self.res, state="disabled")
        self.select_box.set("Video Quality")
        self.select_box.place(x= 450, y= 200)
        self.select_box.bind("<<ComboboxSelected>>",  self.change_size)


        # Video_Path
        # self.path_Lbl = Label(text="Save in")
        # self.path_Lbl.place(x= 550, y= 220)
        # self.path_btn = Button(text= "browser", command=self.path, background=HIGHLIGHT)
        # self.path_btn.place(x= 450, y=220)

        # Download Progress
        self.Dp = Label(background=DARK)
        self.Dp.place(x= 450 , y= 260)


        # loop to keep the Gui running 
        self.tk.mainloop()


###############################################################################

    #functions
    # search function
    def search_link(self):

        def search_thread():
            # gets the link
            text = self.link_input.get()

            # searching
            self.search_btn.config(text="Searching...", padx=20, pady=10)

            # size
            self.got_size.config(text="Getting.....")

            # change the link to Youtube object            
            self.yt_result = pyyt.YouTube(text, on_progress_callback = self.progress_func)
            
            # change old data with new
            self.got_title.config(text = self.yt_result.title)

            # get the jpg from Url which is jpg so we use a function to break the code.
            thumb_n = self.yt_result.thumbnail_url
            self.resize_thumbnail(thumb_n)
            # print(self.yt_result.streams.filter( file_extension="mp4", mime_type = "video/mp4"))

            # we got the link
            self.search_btn.config(text="Search")
            self.select_box.config(state="readonly")
            self.D_btn.config(state="active")
            self.got_size.config(text="Select")
        
        search = threading.Thread(target=search_thread).start()



    # download file Path
    def path(self):
        self.filename = filedialog.askdirectory()
        self.path_Lbl.config(text = self.filename)
        # print(self.filename)

    
    # changes video size        
    def change_size(self,event):
        choice = self.select_box.get()
        if self.yt_result:
            resolution = self.yt_result.streams.filter(res = choice, progressive= True)[0].filesize  
            # print(resolution)
            # round the filesize and multiple by 10^6 
            self.got_size.config(text=f"{round(resolution * 10**-6, 2)}.mb")
            # print(choice)
            self.stream = self.yt_result.streams.filter(res=choice, file_extension="mp4" , progressive= True )[0]
        else:
            print("No link")
    


    def progress_func(self,stream= None, chunk= None, bytes_remaining=None, file_handle=None ):
        size = stream.filesize 
        downloaded = size - bytes_remaining
        percent = downloaded/size
        # print(percent)
        # print(downloaded)
        # print(f'Downloaded: {percent:.0%}', end='\r')
        self.Dp.config(text= f'Downloaded: {percent:.0%}' )



    # download the 
    def download_video(self):
        # thread can run only once so when ever we called download_video function 
        # we create a new instance for thread
        def thread_():
            self.filename = filedialog.askdirectory()
            try:
                self.stream.download( output_path=self.filename)
            except AttributeError:
                messagebox.showerror("Download Error", "Quality Missing")
        # thread instance 
        download = threading.Thread(target=thread_).start()

    # Function that resize the thumbnail using pillow
    def resize_thumbnail(self, image):

        # url library to read our url image
        with urllib.request.urlopen(image) as u:
            raw_data = u.read()

        self.th_img = Image.open(io.BytesIO(raw_data))
        self.resize_img = self.th_img.resize((400,200))
        self.th_img1 = ImageTk.PhotoImage(self.resize_img)
        self.canvas.create_image(200,100, image = self.th_img1 )


        
        