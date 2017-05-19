<!doctype html>
<html lang="en">
<head>
<title>UART File Manager</title>
<link rel="stylesheet" href="bower_components/bootswatch/paper/bootstrap.min.css" />
<style>
.form {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    }
html,
body {
    height: 100%;
}
</style>
</head>
<body>
<div class="form-group form" >
    <form action="/fm" method="post">
        Serial Port:
        <select class="form-control" name="tty">
          %for item in serial:
            <option value="{{ item }}">{{item}}</option>
          %end
        </select>
        Baud Rate:
        <select class="form-control" name="baud">
           %for item in bauds:
            <option value="{{ item }}">{{item}}</option>
          %end
        </select>
        <input class="form-control" value="Open" type="submit" />
    </form>
</div>
</body>
</html>