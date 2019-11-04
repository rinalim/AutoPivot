import RPi.GPIO as GPIO
import time, sys, os, keyboard
from subprocess import *

channel = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ES_CMD = "LANG=ko_KR.UTF-8 /home/pi/dev/customES/emulationstation.sh 2"
RESTART = True
POSITION = -1
FORCE_KILL = False

def run_cmd(cmd):
# runs whatever in the cmd variable
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output

def is_running(pname):
    ps_grep = run_cmd("ps -ef | grep " + pname + " | grep -v grep")
    if len(ps_grep) > 1:
        return True
    else:
        return False

def update_cfg():
    global POSITION

    os.system("sudo sed -i '/allow_video_rotate/d' /opt/retropie/configs/fba/retroarch.cfg")
    os.system("sudo sed -i '/video_rotation/d' /opt/retropie/configs/fba/retroarch.cfg")

    if POSITION == 1:
        #print "Vertical mode"
        os.system("sudo sed -i 's/aspect_ratio_index.*/aspect_ratio_index = \"0\"/g' /opt/retropie/configs/fba/retroarch.cfg")
        os.system("echo 'allow_video_rotate = \"true\"' >> /opt/retropie/configs/fba/retroarch.cfg")
        os.system("echo 'video_rotation = \"1\"' >> /opt/retropie/configs/fba/retroarch.cfg")
        if os.path.isdir('/opt/retropie/configs/all/PauseMode') == True:
            os.system("sudo cp /opt/retropie/configs/all/PauseMode/pause_stop_v.png /opt/retropie/configs/all/PauseMode/pause_stop.png")
            os.system("sudo cp /opt/retropie/configs/all/PauseMode/pause_resume_v.png /opt/retropie/configs/all/PauseMode/pause_resume.png")
    elif POSITION == 0:
        #print "Horizontal mode"
        os.system("sudo sed -i 's/aspect_ratio_index.*/aspect_ratio_index = \"22\"/g' /opt/retropie/configs/fba/retroarch.cfg")
        if os.path.isdir('/opt/retropie/configs/all/PauseMode') == True:
            os.system("sudo cp /opt/retropie/configs/all/PauseMode/pause_stop_h.png /opt/retropie/configs/all/PauseMode/pause_stop.png")
            os.system("sudo cp /opt/retropie/configs/all/PauseMode/pause_resume_h.png /opt/retropie/configs/all/PauseMode/pause_resume.png")


def alert(ev=None):
    #print("event detected")
    global RESTART
    global POSITION
    global FORCE_KILL

    time.sleep(0.1)
    read = GPIO.input(channel)
    if read == POSITION:
        return
    POSITION = read
    if is_running("bin/retroarch") == True:
        #print 'in game'
        RESTART = False
        pid = run_cmd("ps -ef | grep emulators | grep -v grep | awk '{print $2}'").rstrip()
        command = run_cmd("cat /proc/"+pid+"/cmdline").replace('\0', ' ')
        os.system("sudo cp /dev/shm/runcommand.log /tmp/runcommand-ingame.log")
        os.system("killall retroarch")
        if is_running("emulationstation") == True:
            os.system("killall emulationstation")
        time.sleep(1)
        update_cfg()
        FORCE_KILL = True
        os.system("sudo cp /opt/retropie/configs/fba/retroarch.cfg /opt/retropie/configs/fba/retroarch_tilt.cfg")
        os.system("sudo sed -i 's/savestate_auto_load.*/savestate_auto_load = \"true\"/g' /opt/retropie/configs/fba/retroarch_tilt.cfg")
        command = command.replace("fba/retroarch.cfg", "fba/retroarch_tilt.cfg")
        os.system("sudo cat /tmp/runcommand-ingame.log > /dev/shm/runcommand.log")
        #print command
        os.system(command+" &")
    else:
        RESTART = True
        FORCE_KILL = False
        run_cmd("killall emulationstation")

def loop():
    global RESTART
    global POSITION
    global FORCE_KILL
    POSITION = GPIO.input(channel)
    GPIO.add_event_detect(channel, GPIO.BOTH, callback=alert, bouncetime=100)
    while True:
        #read = GPIO.input(channel)
        #POSITION = read
        if POSITION == 1 and RESTART == True:
            #print "Vertical mode"
            RESTART = False
            update_cfg()
            os.system("clear > /dev/tty1")
            #run_cmd(ES_CMD + " --screenrotate 3 > /dev/null 2>&1")
            os.system(ES_CMD + " --screenrotate 3 --screensize 1024 1024 --screenoffset 0 100 > /dev/null 2>&1")
        elif POSITION == 0 and RESTART == True:
            #print "Horizontal mode"
            RESTART = False
            update_cfg()
            os.system("clear > /dev/tty1")
            os.system(ES_CMD + " > /dev/null 2>&1")
        else:
            time.sleep(1)
            if is_running("bin/retroarch") == False:
                time.sleep(2)
                ps_grep = run_cmd("ps -ef | grep  grep -v grep")
                ps_grep_es = run_cmd("ps -ef | grep | grep -v grep")
                if is_running("bin/retroarch") == False and is_running("emulationstation") == False:
                    if FORCE_KILL == True:
                        RESTART = True
                        FORCE_KILL = False
                        os.system("sudo cat /home/pi/tilt/rasminipi.log > /dev/shm/runcommand.log")
                        continue
                    else:
                        break

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
