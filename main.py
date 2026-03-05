import cv2
import os
import PIL
from PIL import ImageTk
import PIL.Image
import speech_recognition as sr
from tkinter import *
import tkinter as tk
import numpy as np

image_x, image_y = 64, 64

def check_sim(i, file_map):
    for item in file_map:
        for word in file_map[item]:
            if i == word:
                return 1, item
    return -1, ""

op_dest = "filtered_data-20241031T113525Z-001/"
alpha_dest = "alphabet-20241031T113511Z-001/alphabet/"
dirListing = os.listdir(op_dest)
editFiles = [item for item in dirListing if ".webp" in item]

file_map = {i: i.replace(".webp", "").split() for i in editFiles}

def func(a):
    all_frames = []
    words = a.split()
    for i in words:
        flag, sim = check_sim(i, file_map)
        if flag == -1:
            for j in i:
                im = PIL.Image.open(alpha_dest + str(j).lower() + "_small.gif")
                frameCnt = im.n_frames
                for frame_cnt in range(frameCnt):
                    im.seek(frame_cnt)
                    im.save("tmp.png")
                    img = cv2.imread("tmp.png")
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (380, 260))
                    im_arr = PIL.Image.fromarray(img)
                    all_frames.extend([im_arr] * 15)
        else:
            im = PIL.Image.open(op_dest + sim)
            im.info.pop('background', None)
            im.save('tmp.gif', 'gif', save_all=True)
            im = PIL.Image.open("tmp.gif")
            frameCnt = im.n_frames
            for frame_cnt in range(frameCnt):
                im.seek(frame_cnt)
                im.save("tmp.png")
                img = cv2.imread("tmp.png")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (380, 260))
                im_arr = PIL.Image.fromarray(img)
                all_frames.append(im_arr)
    final = PIL.Image.new('RGB', (380, 260))
    final.save("out.gif", save_all=True, append_images=all_frames, duration=100, loop=0)
    return all_frames

class Tk_Manage(tk.Tk):
    def __init__(self, *args, **kwargs):     
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Audio to Sign Conversion")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        
        for F in (LoginPage, StartPage, VtoS):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(LoginPage)  # Show LoginPage first

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        # Load and set the background image
        self.bg_image = ImageTk.PhotoImage(PIL.Image.open("loginpage.jpg"))  # Path to background image
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        label = tk.Label(self, text="Login", font=("Verdana", 20), bg="#ffffff")
        label.pack(pady=10, padx=10)
        
        tk.Label(self, text="Username", bg="#ffffff").pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)
        
        tk.Label(self, text="Password", bg="#ffffff").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        
        login_button = tk.Button(self, text="Login", command=lambda: controller.show_frame(StartPage))
        login_button.pack(pady=10)

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Audio to Sign Language Translation for Deaf People", font=("Verdana", 20))
        label.pack(pady=10, padx=20)
        
        button = tk.Button(self, text="Audio to Sign", command=lambda: controller.show_frame(VtoS))
        button.pack()
        
        load = PIL.Image.open("logo.jpg")
        load = load.resize((640, 450))
        render = ImageTk.PhotoImage(load)
        img = Label(self, image=render)
        img.image = render
        img.place(x=100, y=150)

class VtoS(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.cnt = 0
        self.gif_frames = []
        self.inputtxt = tk.Text(self, height=10, width=25)
        label = tk.Label(self, text="Audio to Sign", font=("Verdana", 30))
        label.pack(pady=10, padx=10)
        
        gif_box = tk.Label(self)
        button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        
        def gif_stream():
            if self.cnt == len(self.gif_frames):
                return
            img = self.gif_frames[self.cnt]
            self.cnt += 1
            imgtk = ImageTk.PhotoImage(image=img)
            gif_box.imgtk = imgtk
            gif_box.configure(image=imgtk)
            gif_box.after(50, gif_stream)
        
        def hear_voice():
            store = sr.Recognizer()
            self.inputtxt.delete("1.0", tk.END)  # Clear the text area at the beginning

            with sr.Microphone() as s:
                try:
                    audio_input = store.record(s, duration=10)
                    text_output = store.recognize_google(audio_input)
                    self.inputtxt.insert(tk.END, text_output)  # Insert the new text

                except sr.UnknownValueError:
                    self.inputtxt.insert(tk.END, "Could not understand the audio.")  # Handle no-recognition error
                except sr.RequestError:
                    self.inputtxt.insert(tk.END, "Could not request results from Google Speech Recognition service.")
        
        def take_input():
            INPUT = self.inputtxt.get("1.0", tk.END+"-1c")
            self.gif_frames = func(INPUT)
            self.cnt = 0
            gif_stream()
            gif_box.place(x=400, y=160)
        
        l = tk.Label(self, text="Enter Text or Voice:")
        l1 = tk.Label(self, text="OR")
        voice_button = tk.Button(self, height=2, width=25, text="Record Voice", command=hear_voice)
        voice_button.place(x=50, y=180)
        display_button = tk.Button(self, height=2, width=20, text="Convert", command=take_input)
        
        l.place(x=50, y=160)
        l1.place(x=115, y=230)
        self.inputtxt.place(x=50, y=250)
        display_button.pack()

app = Tk_Manage()
app.geometry("800x700")
app.mainloop()
