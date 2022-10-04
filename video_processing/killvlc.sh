# this script is used to close the vlc
# when procesing the video
kill -9 `ps -ax | grep -m1 /Applications/VLC.app/Contents/MacOS/VLC | awk '{print $1}'`