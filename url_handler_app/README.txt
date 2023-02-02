***
URL schema
***
KIK:/"bookName"."topSection"."subsection"."page"


***
REGISTER THE APP
***
NOTE:
need to run the app to register it
NOTE:
to register the "KIK" url handler for the app we need to add :"
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>Cliff's handler</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>KIK</string>
        </array>
    </dict>
</array>
"
to the Info.phlist file