import os
import serial


def greet():
    print("******************** UART FS ***********")
    print("Tool to send and receive files over UART")
    print("Use ls, cd, send_file [path], read_file [path]")

with serial.Serial('/dev/ttyUSB0', 57600, timeout=0.5) as ser:

    def send_line(line):
        ser.write(("%s\r"%line).encode())

    def ls(args):
        ser.write("ls\r".encode())
        x = ser.read(65535).decode()
        print(x)

    def cd(args):
        ser.write(("cd %s\r"%args[0]).encode())


    def send_file(args):
        path = args[0]
        fname = os.path.basename(path)
        send_line("cat >%s << 'EOL'"%fname)
        with open(path) as f:
            for line in f:
                send_line(line.rstrip())

            send_line("EOL")

        send_cmd("ls","")

    def read_file(args):
        try:
            spath = args[0]
            dpath = args[1]
            fname = os.path.basename(dpath)
        except:
            pass

        send_line("cat %s"%spath)
        s = read_result()
        s = s[s.find('\n') + 1:s.rfind('\n')]

        try:
            file = open(dpath, "w")
            file.write(s)
            file.close()
        except Exception as e:
            print(e)


    def send_cmd(cmd, args):
        command = cmd + " " + " ".join(args)
        send_line(command)

    def read_result():
        x = ser.read(65535).decode()
        return x

    def print_result():
        p = read_result()
        print(p)

    command_engine = {
        "exit": exit,
        "send_file": send_file,
        "read_file": read_file
    }

    greet()
    while True:
        cmd, *args = input(">").split(" ")

        if cmd in command_engine.keys():
            command_engine[cmd](args)
        else:
            send_cmd(cmd, args)

        print_result()


    # print(ls())
    # cd("~")
    # print(ls())
    # send_file("/work/15_TempHawk/Repo/temp-hawk/firmware/LinkIt/root/uartfs.py")
