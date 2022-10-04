file="/Users/ashum048/books/_utils/ImNum_ImName.txt"
while read first_line && read second_line
do
    echo "$first_line" "$second_line"
    defaults write com.apple.screencapture name $first_line"_"$second_line
    defaults write com.apple.screencapture "include-date" 0
    killall SystemUIServer
done < "$file"
screencapture -ip
# osascript -e 'tell application "System Events" to keystroke "4" using {command down, shift down}'