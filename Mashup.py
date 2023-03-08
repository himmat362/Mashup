from flask import Flask,request,redirect,render_template
import zipfile
import smtplib
import numpy as np
#import sys
#import re
from pytube import YouTube
from pydub import AudioSegment
from pydub.utils import make_chunks
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders
from zipfile import ZipFile
from youtube_search import YoutubeSearch
import pandas as pd
app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def index():
    if(request.method=='POST'):
        singer=request.form['singer']
        Number_vid=int(request.form['Number_vid'])
        duration=int(request.form['duration'])
        email=request.form['email']
        results1 = YoutubeSearch(singer, max_results=Number_vid).to_dict()
        data=pd.DataFrame(results1)
        for i in range(1,(data['url_suffix'].count())):
            data['url_suffix'][i]="https://www.youtube.com"+data['url_suffix'][i]
        links=data['url_suffix']
        for i in links:
            yt = YouTube(str(i))
            #print(yt.title)
            #if(yt.length<100):
            # extract only audio
            video = yt.streams.filter(only_audio=True).first()
        # download the file
            out_file = video.download()
        # save the file
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp4'
            os.rename(out_file, new_file)
        audio_files = []
        for file in os.listdir():
                if file.endswith(".mp4"):
                    audio = AudioSegment.from_file(file, "mp4")
                    audio_file = file.replace(".mp4", ".wav")
                    audio.export(audio_file, format="wav")
                    audio_files.append(audio_file)
        chunks = []
        #print(audio_files)
        for audio_file in audio_files:
                chunk = make_chunks(AudioSegment.from_file(audio_file,format="wav"), chunk_length=duration * 1000)
                id=np.random.randint(0,len(chunk))
                chunk=chunk[id]
                #print(chunk)
                chunks.append(chunk)
        merged=AudioSegment.empty()
        for chunk in  chunks:
            merged+=chunk
        merged.export('output.mp3', format="mp3")
        dir=os.getcwd()
        test = os.listdir(dir)
        for item in test:
            if item.endswith(".mp4"):
                os.remove(os.path.join(dir, item))
            if item.endswith(".wav"):
                os.remove(os.path.join(dir, item))
        with zipfile.ZipFile('output.zip', 'w') as zipf:
            zipf.write('output.mp3')
        msg = MIMEMultipart()
        msg['From'] = "noobbobby241@gmail.com"
        msg['To'] = COMMASPACE.join([email])
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "Downloaded and Converted Audio"

        with open("output.zip", "rb") as f:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename="output.zip")
            msg.attach(part)
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login("noobbobby241@gmail.com", "cliwqftyqujpisht")
        smtp.sendmail("noobbobby241@gmail.com", [email], msg.as_string())
        print("Email Sent")
        return redirect("/success")
    return render_template('index.html')
@app.route('/success')
def success():
    return render_template("success.html")
if __name__=='__main__':
    app.run()