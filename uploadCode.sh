printf "\n\ncopying keys!!\n\n"
ssh-copy-id pi@10.8.30.11 
ssh pi@10.8.30.11 'sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot'
scp handleCamera.py pi@10.8.30.11:/home/pi/handleCamera.py
scp vision2022.py pi@10.8.30.11:/home/pi/vision2022.py
