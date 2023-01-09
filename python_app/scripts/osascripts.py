import data.temp as dt
import _utils.logging as log
import _utils._utils_main as _u

def closeSkimDocument(skimPID, docNameId):
    skimCloseWindowCmd = "osascript -e '\
tell application \"System Events\"\n\
	set processList to every process whose unix id is " + skimPID + "\n\
	repeat with proc in processList\n\
		set idx to 1\n\
		set listSize to count of windows of proc\n\
		repeat\n\
			if idx >= listSize then\n\
				exit repeat\n\
			end if\n\
			set procN to name of proc\n\
			if procN is equal to \"Skim\" then\n\
				set procN to \"Skim\"\n\
			end if\n\
			if name of document idx of application \"Skim\" contains \"" + docNameId + "\" then\n\
				tell document idx of application \"Skim\" to close\n\
				exit repeat\n\
			end if\n\
			set idx to idx + 1\n\
		end repeat\n\
	end repeat\n\
end tell'"
    return skimCloseWindowCmd

def closeVscodeWindow(vscodePID, winNameID):
    cmd = "\
                        click button 1 of theWindow\n"
    outCmd = getCmdToRunOnVscodeWindow(vscodePID, winNameID, cmd)
    return outCmd

def closeWindow(vscodePID, winNameID):
    cmd = "\
                        click button 1 of theWindow\n"
    outCmd = getCmdToRunOnVscodeWindow(vscodePID, winNameID, cmd)
    return outCmd

def getCmdToRunOnVscodeWindow(vscodePID, winNameID, cmd):
    outCmd = "osascript -e '\
tell application \"System Events\"\n\
	set processList to every process whose unix id is " + vscodePID + "\n\
	repeat with proc in processList\n\
		tell proc\n\
			repeat with theWindow in windows\n\
				set n to name of theWindow\n\
				if n contains \"" + winNameID + "\" then\n\
					tell theWindow\n"
    outCmd += cmd
    outCmd += "\
					end tell\n\
				end if\n\
			end repeat\n\
		end tell\n\
	end repeat\n\
end tell'"
    return outCmd

def getMoveWindowCMD(appPID, bounds, windowIdentifier = ""):
    bounds = [str(i) for i in bounds]
    if windowIdentifier == "":
        cmd = "osascript -e '\
        tell application \"System Events\"\n\
            set processList to every process whose unix id is " + appPID + "\n\
            repeat with proc in processList\n\
                tell proc\n\
                    tell window " + "1" + "\n\
                        set size to {" + bounds[0] + ", " + bounds[1] + "}\n\
                        delay 0.1\n\
                        set position to {" + bounds[2] + ", " + bounds[3] + "}\n\
                        delay 0.1\n\
                        perform action \"AXRaise\"\n\
                    end tell\n\
                end tell\n\
            end repeat\n\
        end tell'"
    else:
        cmd = "osascript -e '\
tell application \"System Events\"\n\
	set processList to every process whose unix id is " + appPID + "\n\
	repeat with proc in processList\n\
		tell proc\n\
			repeat with theWindow in windows\n\
				set n to name of theWindow\n\
				if n contains \"" + windowIdentifier + "\" then\n\
					tell theWindow\n\
                        set size to {" + bounds[0] + ", " + bounds[1] + "}\n\
                        delay 0.1\n\
                        set position to {" + bounds[2] + ", " + bounds[3] + "}\n\
                        delay 0.1\n\
                        perform action \"AXRaise\"\n\
					end tell\n\
				end if\n\
			end repeat\n\
		end tell\n\
	end repeat\n\
end tell'"

    # attempt to do this with xdotools
    # cmd = "xdotool search --name windowmove " + windowID + " " + bounds[2] + " " + bounds[3]
    # os.system(cmd)
    # cmd = "xdotool windowsize " + windowID + " " + bounds[0] + " " + bounds[1]
    return cmd

def get_SetSecVSCode_CMD():
    cmd = "osascript -e '\n\
        tell application \"System Events\"\n\
            keystroke \"kw\" using {command down}\n\
            keystroke \"b\" using {command down, option down}\n\
        end tell\n\
        '"
    return cmd

