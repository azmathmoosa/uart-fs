<!doctype html>
<html lang="en">
<head>
</head>
<body>
    <form action="/fm" method="post">
        Serial Port:
        <select name="tty">
          %for item in serial:
            <option value="{{ item }}">{{item}}</option>
          %end
        </select>
        Baud Rate:
        <select name="baud">
           %for item in bauds:
            <option value="{{ item }}">{{item}}</option>
          %end
        </select>
        <input value="Open" type="submit" />
    </form>
</body>
</html>