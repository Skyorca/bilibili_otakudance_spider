import pandas
import requests
import global_var
from threading import Thread

class AvatarDownloader:

    def __init__(self):
        self.up = pandas.read_csv("up.csv")
        self.up_name = self.up.loc[:,"up_name"]
        self.up_sex  = self.up.loc[:,"sex"]
        self.up_avatar_url = self.up.loc[:,"avatar"]

    def download_avatar_and_save(self):
        for i in range(len(self.up_name)):
            r = requests.get(url=self.up_avatar_url[i],headers=global_var.headers)
            if self.up_sex[i] == "女":
                with open("./avatars/girls/{}.jpg".format(self.up_name[i]),'wb+') as f:
                    f.write(r.content)
            elif self.up_sex[i] == "男":
                with open("./avatars/boys/{}.jpg".format(self.up_name[i]),'wb+') as f:
                    f.write(r.content)
            else: 
                with open("./avatars/secrets/{}.jpg".format(self.up_name[i]),'wb+') as f:
                    f.write(r.content)

    def start_multithread_download(self):
        task = Thread(target=self.download_avatar_and_save)
        task.start()


downloader = AvatarDownloader()
downloader.start_multithread_download()
        
