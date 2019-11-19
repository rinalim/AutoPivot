import RPi.GPIO as GPIO
import time, sys, os
from subprocess import *

channel = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ES_CMD = "LANG=ko_KR.UTF-8 emulationstation"
#ES_CMD = "LANG=ko_KR.UTF-8 /home/pi/dev/customES/emulationstation.sh 2"
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

def update_cfg(sysname):
    global POSITION
    conf_file = "/opt/retropie/configs/"+sysname+"/retroarch.cfg"

    os.system("sudo sed -i '/allow_video_rotate/d' " + conf_file)
    os.system("sudo sed -i '/video_rotation/d' " + conf_file)

    if POSITION == 1:
        #print "Vertical mode"
        os.system("sudo sed -i 's/aspect_ratio_index.*/aspect_ratio_index = \"0\"/g' " + conf_file)
        os.system("echo 'allow_video_rotate = \"true\"' >> " + conf_file)
        os.system("echo 'video_rotation = \"1\"' >> " + conf_file)
        if os.path.isdir('/opt/retropie/configs/all/PauseMode') == True:
            os.system("sudo cp /opt/retropie/configs/all/PauseMode/pause_stop_v.png /opt/retropie/configs/all/PauseMode/pause_stop.png")
            os.system("sudo cp /opt/retropie/configs/all/PauseMode/pause_resume_v.png /opt/retropie/configs/all/PauseMode/pause_resume.png")
    elif POSITION == 0:
        #print "Horizontal mode"
        os.system("sudo sed -i 's/aspect_ratio_index.*/aspect_ratio_index = \"22\"/g' " + conf_file)
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
    os.system("echo "+ str(POSITION) + " > /tmp/AutoPivot.log")
    if is_running("bin/retroarch") == True:
        #print 'in game'
        RESTART = False
        pid = run_cmd("ps -ef | grep emulators | grep -v grep | awk '{print $2}'").rstrip()
        command = run_cmd("cat /proc/"+pid+"/cmdline").replace('\0', ' ')
        os.system("sudo cp /dev/shm/runcommand.log /tmp/runcommand-ingame.log")
        os.system("killall retroarch")
        os.system("/opt/retropie/configs/all/AutoPivot/onend.sh")
        if is_running("emulationstation") == True:
            os.system("killall emulationstation")
        time.sleep(1)
        FORCE_KILL = True
        sysname = command.split(" ")[4].split("/")[4]
        update_cfg(sysname)
        conf_file = "/opt/retropie/configs/"+sysname+"/retroarch.cfg"
        conf_flle_tilt = "/opt/retropie/configs/"+sysname+"/retroarch_tilt.cfg"
        os.system("sudo cp " + conf_file + " " + conf_flle_tilt)
        os.system("sudo sed -i 's/savestate_auto_load.*/savestate_auto_load = \"true\"/g' " + conf_flle_tilt)
        command = command.replace(conf_file, conf_flle_tilt)
        os.system("sudo cat /tmp/runcommand-ingame.log > /dev/shm/runcommand.log")
        #print command
        os.system("/opt/retropie/configs/all/AutoPivot/onstart.sh")
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
    os.system("echo "+ str(POSITION) + " > /tmp/AutoPivot.log")
    GPIO.add_event_detect(channel, GPIO.BOTH, callback=alert, bouncetime=100)
    while True:
        #read = GPIO.input(channel)
        #POSITION = read
        if POSITION == 1 and RESTART == True:
            #print "Vertical mode"
            RESTART = False
            update_cfg("fba")
            os.system("clear > /dev/tty1")
            os.system(ES_CMD + " --screenrotate 3 > /dev/null 2>&1")
            #os.system(ES_CMD + " --screenrotate 3 --screensize 1024 1024 --screenoffset 0 100 > /dev/null 2>&1")
        elif POSITION == 0 and RESTART == True:
            #print "Horizontal mode"
            RESTART = False
            update_cfg("fba")
            os.system("clear > /dev/tty1")
            os.system(ES_CMD + " > /dev/null 2>&1")
        else:
            time.sleep(1)
            if is_running("bin/retroarch") == False:
                time.sleep(2)
                if is_running("bin/retroarch") == False and is_running("emulationstation") == False:
                    if FORCE_KILL == True:
                        RESTART = True
                        FORCE_KILL = False
                        os.system("sudo cat /opt/retropie/configs/all/AutoPivot/rasminipi.log > /dev/shm/runcommand.log")
                        continue
                    else:
                        break

if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
