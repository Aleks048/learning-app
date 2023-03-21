import data.temp as dt
import _utils.logging as log
import _utils._utils_main as _u
import settings.facade as sf

def get_NameOfFrontSkimDoc_CMD():
	cmd = "osascript -e '\
tell application \"{0}\" to return name of front document\
'".format( sf.Wr.Data.TokenIDs.AppIds.skim_ID)
	return cmd

def get_PageOfSkimDoc_CMD(filename):
	cmd = "osascript -e '\
tell application \"{0}\"\n\
	repeat with d in documents\n\
		set n to name of d\n\
		if n contains \"{1}\" then\n\
			tell d\n\
				return current page\n\
			end tell\n\
		end if\n\
	end repeat\n\
end tell'".format( sf.Wr.Data.TokenIDs.AppIds.skim_ID, filename)
	return cmd

def get_NameOfFrontPreviewDoc_CMD():
    cmd = "osascript -e '\
        tell application \"Preview\" to save the front document\n\
        tell application \"System Events\" to tell process \"Preview\"\n\
            tell front window \n\
                click button 1\n\
            end tell\n\
        end tell\
        '"
    return cmd



def closeSkimDocument(skimPID, docNameId):
    skimCloseWindowCmd = "osascript -e '\
tell application \"System Events\"\n\
	set processList to every process whose unix id is {0}\n\
	repeat with proc in processList\n\
		set idx to 1\n\
		set listSize to count of windows of proc\n\
		repeat\n\
			if idx > listSize then\n\
				exit repeat\n\
			end if\n\
			set procN to name of proc\n\
			if procN is equal to \"{1}\" then\n\
				set procN to \"{1}\"\n\
			end if\n\
			if name of document idx of application \"{1}\" contains \"{2}\" then\n\
				tell document idx of application \"{1}\" to close\n\
				exit repeat\n\
			end if\n\
			set idx to idx + 1\n\
		end repeat\n\
	end repeat\n\
end tell'".format(skimPID, sf.Wr.Data.TokenIDs.AppIds.skim_ID, docNameId)
    return skimCloseWindowCmd

def closeVscodeWindow(vscodePID, winNameID):
    cmd = "\
                        click button 1 of theWindow\n"
    outCmd = getCmdToRunOnVscodeWindow(vscodePID, winNameID, cmd)
    return outCmd

def closeFinderWindow(vscodePID, winNameID):
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

def getMoveWindowCMD(appPID, bounds, windowIdentifier):
    bounds = [str(i) for i in bounds]
   
    cmd = "osascript -e '\
tell application \"System Events\"\n\
	set processList to every process whose unix id is " + appPID + "\n\
	repeat with proc in processList\n\
		tell proc\n\
			repeat with theWindow in windows\n\
				set n to name of theWindow\n\
				if n contains \"" + windowIdentifier + "\" then\n\
					tell theWindow\n\
                        perform action \"AXRaise\"\n\
                        set position to {" + bounds[2] + ", " + bounds[3] + "}\n\
                        delay 0.1\n\
                        set size to {" + bounds[0] + ", " + bounds[1] + "}\n\
                        delay 0.1\n\
					end tell\n\
				end if\n\
			end repeat\n\
		end tell\n\
	end repeat\n\
end tell'"

    return cmd

def get_SetSecVSCode_CMD():
    cmd = "osascript -e '\n\
		activate " + sf.Wr.Data.TokenIDs.AppIds.vsCode_ID + "\n\
        tell application \"System Events\"\n\
            keystroke \"kw\" using {command down}\n\
            keystroke \"b\" using {command down, option down}\n\
        end tell\n\
	'"
    return cmd

