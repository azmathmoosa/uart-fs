import datetime
import json
import os
import tempfile
import threading
import time

import serial
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket

from bottle import route, get, run, template, request, static_file, post

sTTY = '/dev/ttyUSB0'
sBaud = 57600
ser = None

serial_out = []

console = None
flag_eof = True
flag_getfile = False

EOF_STRING = "#&^eof^&#"


@post('/fm')
def fm():
    global ser, sTTY, sBaud
    sTTY = request.forms.get('tty')
    sBaud = request.forms.get('baud')
    uName = request.forms.get('username')
    uPass = request.forms.get('password')

    if ser is not None:
        ser.close()

    ser = serial.Serial(sTTY, sBaud, timeout=1)
    readThread = threading.Thread(target=listen_serial, args=(ser,))
    readThread.start()
    return template('fm.tpl',sTTY=sTTY,sBaud=sBaud)


@route('/')
def index():
    ttys = list_ttys()
    bauds = [110, 150, 300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
    if ttys:
        return template('index.tpl', serial=ttys, bauds=bauds)
    else:
        return "Failed"


@get('/console_websocket', apply=[websocket])
def console_websocket(ws):
    global console
    console = ws
    while True:
        msg = ws.receive()
        if msg is not None:
            if msg != "init websocket":
                ser_write(msg+"\r")
            else:
                ws.send("WebSocket Initialized")
        else:
            break


@route('/download')
def download():
    global flag_getfile, flag_eof
    filepath = request.query['path']
    with tempfile.TemporaryDirectory() as td:
        fp = tempfile.NamedTemporaryFile(delete=False,dir=td)

        def writeFile(line):
            if not EOF_STRING in line:
                fp.write(line.encode())

        flag_getfile = writeFile
        flag_eof = False
        raw_command(' cat \'%s\' && echo "%s"  ' % (filepath, EOF_STRING), 0)
        while flag_eof == False:
            time.sleep(1)

        fp.seek(0)
        flag_getfile = False
        fp.close()

        newname = fp.name

        oldname = os.path.join(os.path.dirname(fp.name), os.path.basename(filepath))

        os.rename(newname, oldname)

        return static_file(oldname,root="/",download=True)


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
        res = get_content(postdata['item'])

    if postdata['action'] == 'edit':
        res = edit_content(postdata['item'], postdata['content'])

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


def command(cmdline, wait=1):
    # clear read buffer
    serial_out.clear()
    ser.write(("  cmd=$( %s 2>&1)\r   "%cmdline).encode())
    time.sleep(wait)


def raw_command(cmdline, wait=1):
    serial_out.clear()
    ser.write(("   %s   \r   " % cmdline).encode())
    if wait > 0:
        time.sleep(wait)


def ser_write(cmdline):
    ser.write(("%s" % cmdline).encode())


def send_line(line):
    ser.write(("%s\r"%line).encode())


#API Stuff
def list(path):
    raw_command(" ls --color=never -l %s "%path)
    x = read_result()

    files = x.split('\n')

    jfiles = []

    for file in files:
        try:
            rights, _, __, ___, size, month, day, t, name = file.split()
            if ':' not in t:
                y = t
                t = "0:0"
            else:
                y = datetime.datetime.now().year

            mon = datetime.datetime.strptime(month,"%b")
            mon = mon.strftime("%m")
            dt = "%s-%s-%s %s:%s"%(y, mon, day, t,"0")

            #d = "%s%s%s%s"%(day,month,y,t)
            #dt = time.mktime(datetime.datetime.strptime(d, "%d%b%Y%H:%M").timetuple())

            type = "dir" if rights.startswith('d') else "file"
            jf = { "name": name,
                   "rights": rights,
                   "size": size,
                   "date": dt,
                   "type": type
                   }
            jfiles.append(jf)
        except Exception as e:
            print(e)

    return jfiles


def get_content(path):
    global flag_eof
    flag_eof = False
    raw_command(' cat \'%s\' && echo "%s"  '%(path, EOF_STRING),0)
    while flag_eof == False:
        time.sleep(1)

    s = read_result()
    s = s[s.find('\n') + 1:s.rfind('\n')]
    print(s)

    return s


def edit_content(path, contents):
    raw_command(" cat << 'EOF' > %s \r%s\r "%(path,contents))
    ser_write("\rEOF\r")
    s = read_result()
    st, msg = validate_cmd()
    if st:
        return {"success":"true", "error":None}
    else:
        return {"success":"false", "error": msg}


def rename(path, newpath):
    command(" mv %s %s  "%(path,newpath))
    s = read_result()
    st, msg = validate_cmd()
    if not st:
        return { "success": "false", "error": msg }
    else:
        return { "success": "true", "error" : None }


def create_folder(path):
    command(" mkdir %s  "%path)
    s = read_result()
    st,msg = validate_cmd()
    if not st:
        return { "success": "false", "error": msg }
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
        if action=="remove":
            compiledcmd = " %s '%s' " % (cmd, path)
        else:
            compiledcmd = " %s '%s' '%s' "%(cmd, path, dest_path)

        command(compiledcmd)
        st, msg = validate_cmd()
        if not st:
            return {"success": "false", "error": msg}

    return {"success": "true", "error": None}


def set_permissions(paths, code, recursive):
    if recursive == "true":
        rec = "-R"
    else:
        rec = " "

    for path in paths:
        command(" chmod %s %s %s "%(rec, code, path))
        s = read_result()
        st, msg = validate_cmd()
        if st:
            return {"success": "false", "error": msg}

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
#             send_line(line.rstrip())
#
#         send_line("EOL")
#
#     send_cmd("ls","")
#

def read_result():
    global serial_out
    for i, _ in enumerate(serial_out):
        serial_out[i] = serial_out[i].strip()

    t = "\n".join(serial_out)
    serial_out.clear()
    return t
    #x = ser.read(65535).decode()
    #r = x[x.find('\n') + 1:x.rfind('\n')]
    #return r.strip()


def validate_cmd():
    s = read_result()
    raw_command(" echo $? ")
    status = read_result()
    if status.strip().endswith("1"):
        raw_command(" echo $cmd ")
        s = read_result()
        return False, s
    else:
        return True, ""


def print_result():
    p = read_result()
    print(p)


def listen_serial(port):
    global serial_out, flag_eof
    while True:
        if ser.inWaiting() > 0:
            readval = port.readline().decode()
            serial_out.append(readval)
            if readval.strip() == EOF_STRING:
                flag_eof = True

            if console != None:
                console.send(readval.strip())

            if flag_getfile != False:
                flag_getfile(readval)

greet()

host = "0.0.0.0"
port = 5000
run(host='0.0.0.0', port=5000, server=GeventWebSocketServer)
#server = WSGIServer((host,port), Bottle(), handler_class=WebSocketHandler)

#server.serve_forever()

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
