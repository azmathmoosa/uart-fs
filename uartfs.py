import os
import serial
from bottle import route, run, template, request, static_file, post
import re
import json
import time
from subprocess import check_output

sTTY = '/dev/ttyUSB0'
sBaud = 57600
ser = None


@post('/fm')
def fm():
    global ser, sTTY, sBaud
    sTTY = request.forms.get('tty')
    sBaud = request.forms.get('baud')
    ser = serial.Serial(sTTY, sBaud, timeout=1)
    return template('fm.tpl',"")

@route('/')
def index():
    ttys = list_ttys()
    bauds = [110, 150, 300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
    if ttys:
        return template('index.tpl', serial=ttys, bauds=bauds)
    else:
        return "Failed"

@route('/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root="views/")

@post('/handler')
def handler():
    postdata = request.body.read().decode()
    postdata = json.loads(postdata)

    if postdata['action'] == 'list':
        res = list(postdata['path'])

    if postdata['action'] == 'getContent':
        res = get_content(postdata['path'])

    if postdata['action'] == 'rename':
        res = rename(postdata['item'],postdata['newItemPath'])

    if postdata['action'] == 'createFolder':
        res = create_folder(postdata['newPath'])

    if postdata['action'] in ['copy', 'move', 'remove']:
        if 'newPath' not in postdata.keys():
            postdata['newPath'] = ""
        if 'singleFilename' in postdata.keys():
            postdata['newPath'] += "/" + postdata['singleFilename']

        res = fm(postdata['action'], postdata['items'], postdata['newPath'])

    if postdata['action'] == "changePermissions":
        res = set_permissions(postdata['items'], postdata['permsCode'], postdata['recursive'])

    result = {"result": res}
    return json.dumps(result)

def greet():
    print("******************** UART FS ***********")
    print("Tool to send and receive files over UART")
    print("Goto localhost:5000")

def list_ttys():
    if not os.path.exists("/dev/serial"):
        return False

    ttys = []
    for dirpath, _, filenames in os.walk("/dev/serial/by-id"):
        for f in filenames:
            s = (os.path.realpath(os.path.abspath(os.path.join(dirpath, f))))
            ttys.append(s)

    return ttys

def filter(x):
    return x[x.find('\n') + 1:x.rfind('\n')]

def command(cmdline):
    ser.write(("    %s \r   "%cmdline).encode())

def send_line(line):
    ser.write(("%s\r"%line).encode())

#API Stuff
def list(path):
    command(" ls --color=never -l %s "%path)
    x = read_result()

    files = x.split('\n')

    jfiles = []
    for file in files:
        try:
            rights, _, __, ___, size, month, day, year, name = file.split()
            type = "dir" if rights.startswith('d') else "file"
            jf = { "name": name,
                   "rights": rights,
                   "size": size,
                   "date": " ".join([day,month,year]),
                   "type": type
                   }
            jfiles.append(jf)
        except Exception as e:
            print(e)

    return jfiles

def get_content(path):
    command(" cat %s  "%path)
    s = filter(read_result())
    return s

def rename(path, newpath):
    command(" mv %s %s  "%(path,newpath))
    s = read_result()
    print(s)
    if len(s) > 0:
        return { "success": "false", "error": s }
    else:
        return { "success": "true", "error" : None }

def create_folder(path):
    command(" mkdir %s  "%path)
    s = read_result()
    if "can't" in s:
        return { "success": "false", "error": s }
    else:
        return { "success": "true", "error" : None }

def fm(action, paths, dest_path):
    if action == "move":
        cmd = "mv"

    if action == "copy":
        cmd = "cp"

    if action == "remove":
        cmd = "rm -r"

    for path in paths:
        command(" %s %s %s "%(cmd, path, dest_path))
        s = read_result()
        if cmd in s:
            return {"success": "false", "error": s}

    return {"success": "true", "error": None}

def set_permissions(paths, code, recursive):
    if recursive == "true":
        rec = "-R"
    else:
        rec = " "

    for path in paths:
        command(" chmod %s %s %s "%(rec, code, path))
        s = read_result()
        if len(s) > 0:
            return {"success": "false", "error": s}

    return {"success": "true", "error": None}


##########33
def cd(args):
    ser.write(("cd %s\r"%args[0]).encode())


# def send_file(args):
#     path = args[0]
#     fname = os.path.basename(path)
#     send_line("cat >%s << 'EOL'"%fname)
#     with open(path) as f:
#         for line in f:
#             send_line(line.rstrip())
#
#         send_line("EOL")
#
#     send_cmd("ls","")
#

def read_result():
    x = ser.read(65535).decode()
    r = x[x.find('\n') + 1:x.rfind('\n')]
    return r.strip()

def print_result():
    p = read_result()
    print(p)


greet()
run(host='0.0.0.0', port=5000)
#
# while True:
#     cmd, *args = input(">").split(" ")
#
#     if cmd in command_engine.keys():
#         command_engine[cmd](args)
#     else:
#         send_cmd(cmd, args)
#
#     print_result()
#

# print(ls())
# cd("~")
# print(ls())
# send_file("/work/15_TempHawk/Repo/temp-hawk/firmware/LinkIt/root/uartfs.py")
