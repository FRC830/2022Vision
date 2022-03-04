printf "\n\ncopying keys!!\n\n"
#login to the pi
ssh pi@10.8.30.11 'sudo mount -o remount,rw / ; sudo mount -o remount,rw /boot'
#Set PI to read write
ssh-copy-id pi@10.8.30.11 
#Upload the files to PI
scp handleCamera.py pi@10.8.30.11:/home/pi/handleCamera.py
scp vision2022.py pi@10.8.30.11:/home/pi/vision2022.py
#reboot the PI uncomment when needed
ssh pi@10.8.30.11 'sudo reboot'
