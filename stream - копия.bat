ECHO ============================
ffmpeg -re -rtbufsize 1000M -f dshow -i video="AVerMedia HD Capture C985 Bus 3" -s 1920x1080 -vcodec libx265 -x265-params lossless=1 -bufsize 768k -f mpegts udp://127.0.0.1:2000
"cmd /k" 