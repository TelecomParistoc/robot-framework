#!/usr/bin/python


from datetime import datetime
import sys
import os


try:
    content = open('/etc/init.d/auto_launch.config', 'r').readlines()
except:
    open('/var/failure_logs', 'a').write(datetime.now().strftime('%H_%M_%d_%m_%Y:')+"\n[-] Error searching for /etc/init.d/auto_launch.config\n")
    exit()

if not os.path.isdir('/var/robots_logs'):
    os.makedirs('/var/robots_logs')

logfile = datetime.now().strftime('/var/robots_logs/robot_%H_%M_%d_%m_%Y.log')
program_to_launch_path = content[0].split('\n')[0]
command_path = content[1].split('\n')[0]
program_path = content[2].split('\n')[0]

print sys.argv
if "start" in sys.argv[1]:
    print("Starting robot main program")
    os.system(program_path+" "+program_to_launch_path+" "+command_path+" > "+logfile)
    print("Robot is alive")
elif "stop" in sys.argv[1]:
    print("Stopping robot main program")
    os.system("killall "+program_path.split('/')[-1])
    print("Robot is dead")
else:
    print("Usage: /etc/init.d/robot_launch_auto {start|stop}")
