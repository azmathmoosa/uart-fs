<!doctype html>
<html lang="en" data-ng-app="FileManagerApp">
<head>
  <!--
    * UART File Manager based on Angular FileManager v1.5.1 (https://github.com/joni2back/angular-filemanager)
    * Azmath Moosa -- based on works of Jonas Sciangula Street <joni2back@gmail.com>
    * Licensed under MIT (https://github.com/joni2back/angular-filemanager/blob/master/LICENSE)
  -->
  <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
  <meta charset="utf-8">
  <title>UART File Manager</title>

  <!-- third party -->
    <script src="bower_components/angular/angular.min.js"></script>
    <script src="bower_components/angular-translate/angular-translate.min.js"></script>
    <script src="bower_components/ng-file-upload/ng-file-upload.min.js"></script>
    <script src="bower_components/jquery/dist/jquery.min.js"></script>
    <script src="bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="bower_components/bootswatch/paper/bootstrap.min.css" />
  <!-- /third party -->


    <script src="src/js/app.js"></script>
    <script src="src/js/directives/directives.js"></script>
    <script src="src/js/filters/filters.js"></script>
    <script src="src/js/providers/config.js"></script>
    <script src="src/js/entities/chmod.js"></script>
    <script src="src/js/entities/item.js"></script>
    <script src="src/js/services/apihandler.js"></script>
    <script src="src/js/services/apimiddleware.js"></script>
    <script src="src/js/services/filenavigator.js"></script>
    <script src="src/js/providers/translations.js"></script>
    <script src="src/js/controllers/main.js"></script>
    <script src="src/js/controllers/selector-controller.js"></script>
    <link href="src/css/animations.css" rel="stylesheet">
    <link href="src/css/dialogs.css" rel="stylesheet">
    <link href="src/css/main.css" rel="stylesheet">


  <!-- Comment if you need to use raw source code
    <link href="dist/angular-filemanager.min.css" rel="stylesheet">
    <script src="dist/angular-filemanager.min.js"></script>
   -->

  <script type="text/javascript">
    //example to override angular-filemanager default config
    angular.module('FileManagerApp').config(['fileManagerConfigProvider', function (config) {
      var defaults = config.$get();
      config.set({
        appName: 'angular-filemanager',
        pickCallback: function(item) {
          var msg = 'Picked %s "%s" for external use'
            .replace('%s', item.type)
            .replace('%s', item.fullPath());
          window.alert(msg);
        },
        allowedActions: angular.extend(defaults.allowedActions, {
          pickFiles: false,
          pickFolders: false,
        }),
      });
    }]);
  </script>
  <style>
    .fm {
        height: 60%;
    }
  </style>

        <script type="text/javascript">
         function WebSocketInit()
         {
            if ("WebSocket" in window)
            {
               console.log("WebSocket is supported by your Browser!");
               var consoleWrapper = document.getElementById('console');
               var consoleNode = document.getElementById('terminal');

               // Let us open a web socket
               var ws = new WebSocket("ws://localhost:5000/console_websocket");

               ws.onopen = function()
               {
                  // Web Socket is connected, send data using send()
                  ws.send("init websocket");

               };

               ws.onmessage = function (evt)
               {
                  var received_msg = evt.data;
                  console.log(received_msg);
                  var lineNode = document.createElement("P");
                  var lineText = document.createTextNode(received_msg);
                  lineNode.appendChild(lineText);
                  lineNode.classList.add('terminal--output');
                  consoleNode.appendChild(lineNode);
                  consoleWrapper.scrollTop = consoleWrapper.scrollHeight;

                  //consoleNode.appendChild(


               };

               ws.onclose = function()
               {
                  // websocket is closed.
                  console.log("Connection is closed...");
               };

               document.getElementById("consoleBox")
                .addEventListener("keyup", function(event) {
                event.preventDefault();
                if (event.keyCode == 13) {
                    var cmd = document.getElementById("consoleBox").value;
                    ws.send(cmd);
                    console.log(cmd);
                    document.getElementById("consoleBox").value = "";
                }
                });
            }

            else
            {
               // The browser doesn't support WebSocket
               console.log("WebSocket NOT supported by your Browser!");
            }
         }
      </script>
</head>

<body class="ng-cloak">
 <div class="fm">
  <angular-filemanager></angular-filemanager>
 </div>

 <div id="console" class="console">
    %include('console.tpl');
 </div>
</body>
</html>