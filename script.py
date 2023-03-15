from os import listdir, popen, system
import sys
import time

def getAvailableCommands():
    cmds = listdir('/bin/')
    cmds += listdir('/sbin/')
    with open('commands.txt') as my_file:
        additionalCommands = my_file.read().splitlines()
    cmds += additionalCommands
    cmds.remove('pfctl')
    cmds.remove('alias')
    return cmds

def getUsers():
    return popen('cut -d: -f1 /etc/passwd').read().split('\n')

def createUser(user, password):
    system("pw useradd -n " + user + " -m -s /usr/local/bin/bash -d /usr/home/" + user) 
    system("echo " + password + " | pw usermod " + user + " -h 0")
    system("echo '" + user + " ALL = (root) NOPASSWD: /usr/sbin/tcpdump' >> /usr/local/etc/sudoers")
    system("echo '" + user + " ALL = (root) NOPASSWD: /sbin/pfctl' >> /usr/local/etc/sudoers")
    system("echo '' >> /usr/local/etc/sudoers")

def blacklistCommands(blacklist, homeDir):
    f = open(homeDir + ".bash_profile", "w+")
    for b in blacklist:
        f.write("alias " + b + "=\"printf 'Command not permitted.\\n'\"\n")
    f.write("alias alias=\"printf '\\n'\"")

def disableBashAutocompletion(homeDir):
    f = open(homeDir + ".inputrc", "w+")
    f.write("set disable-completion on")

def main():
    print("Checking if 'bash' package is installed...")
    time.sleep(1)
    r = popen("pkg info | grep bash").read()
    if not r:
        sys.exit("[Error] 'bash' should be installed (Install with 'pkg install bash'). ")
    else:
        print("Ok.")

    print("Checking if 'sudo' package is installed...")
    time.sleep(1)
    r = popen("pkg info | grep sudo").read()
    if not r:
        sys.exit("[Error] 'sudo' should be installed (Install with 'pkg install sudo'). ")
    else:
        print("Ok.")

    users = getUsers()

    ### uncomment to print all registered users
        # for u in users:
    #     sys.stdout.write(u + " ")
    # print()
    
    username = raw_input("Type a name for the new user: ")
    
    if username not in users:
        password = raw_input("Type a password: ")
        createUser(username, password)
    else:
        sys.exit("Username already exists!")

    homeDir = "/usr/home/" + username + "/"
    
    availableCommands = getAvailableCommands()

    w = raw_input("Permitted commands (seperated with a space): ")
    whitelist = w.split(" ")
    blacklist = [x for x in availableCommands if x not in whitelist]

    blacklistCommands(blacklist, homeDir)

    system("chmod -R 755 " + homeDir)

    disableBashAutocompletion(homeDir)
    
if __name__ == '__main__':
    main()
