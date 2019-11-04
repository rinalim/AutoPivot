#!/usr/bin/python

import sys, os, time

channel = input('Pin number: ')
os.system("sudo sed -i 's/channel = .*/channel = " + channel + "/g' /opt/retropie/configs/all/AutoPivot/AutoPivot.py")

if os.path.isdir('/opt/retropie/configs/all/PauseMode') == True:
    print "PauseMode detected"
    os.system("cat /opt/retropie/configs/all/runcommand-onstart.sh | grep PauseMode >> /opt/retropie/configs/all/AutoPivot/onstart.sh")
    os.system("echo 'sudo killall pngpause' >> /opt/retropie/configs/all/AutoPivot/onend.sh")
    os.system("echo 'sudo killall pngbg' >> /opt/retropie/configs/all/AutoPivot/onend.sh")
    os.system("echo 'sudo killall PauseMode' >> /opt/retropie/configs/all/AutoPivot/onend.sh")
    os.system("sudo cp /opt/retropie/configs/all/PauseMode/pause_stop.png /opt/retropie/configs/all/PauseMode/pause_stop_h.png")
    os.system("sudo cp /opt/retropie/configs/all/PauseMode/pause_resume.png /opt/retropie/configs/all/PauseMode/pause_resume_h.png")
    os.system('sudo convert -rotate "270" /opt/retropie/configs/all/PauseMode/pause_stop.png /opt/retropie/configs/all/PauseMode/pause_stop_v.png')
    os.system('sudo convert -rotate "270" /opt/retropie/configs/all/PauseMode/pause_resume.png /opt/retropie/configs/all/PauseMode/pause_resume_v.png')
