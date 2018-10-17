import os
import zipfile
from shutil import copyfile

zip_file = zipfile.ZipFile('Submission.zip', mode='w')
zip_file.write("MyBot.py")

for dirpath,dirs,files in os.walk("hlt"):
  for f in files:
    fn = os.path.join(dirpath, f)
    zip_file.write(fn)
zip_file.close()

copyfile("MyBot.py","oldBots/MyBot"+str(len(os.listdir("oldBots"))-1)+".py")
