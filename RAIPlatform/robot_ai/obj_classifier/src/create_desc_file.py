import os

def create_descriptor():
    for dirs in ['../negative_data']:
      for img in os.listdir(dirs):
        current_image_path = str(dirs)+'/'+str(img)+'\n'
        with open('bg.txt','a') as f:
            f.write(current_image_path)

create_descriptor()