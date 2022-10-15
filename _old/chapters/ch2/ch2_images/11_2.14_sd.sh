#!/bin/bash
conIDX=`grep -n "% THIS IS CONTENT id: 11" "/Users/ashum048/books//b_analysis_test/ch2//subchapters//ch_2.14/2.14_con.tex" | cut -d: -f1`
tocIDX=`grep -n "% THIS IS CONTENT id: 11" "/Users/ashum048/books//b_analysis_test/ch2//subchapters//ch_2.14/2.14_toc.tex" | cut -d: -f1`
if [ "$conIDX" != "" ]
then
osascript -  $conIDX <<EOF
    on run argv
        tell application "code"
            activate
            tell application "System Events"
                keystroke "1" using {command down}
                delay 0.1
                keystroke "g" using {control down}
                keystroke item 1 of argv + 20
                keystroke return
            end tell
        end tell
    end run
EOF
fi
if [ "$tocIDX" != "" ]
then
osascript - $tocIDX <<EOF
    on run argv
        tell application "code"
            activate
            tell application "System Events"
                keystroke "2" using {command down}
                delay 0.1
                keystroke "g" using {control down}
                keystroke item 1 of argv
                keystroke return
            end tell
        end tell
    end run
EOF
fi
osascript -e 'tell application "skim"
    tell document "2.14_main.pdf"
        delay 0.1
        go to page 11
        end tell
end tell'