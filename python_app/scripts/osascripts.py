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
end tell'".format(sf.Wr.Data.TokenIDs.AppIds.skim_ID, filename)
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
				tell document idx of application \"{1}\"\n\
    				save\n\
    				close\n\
                end tell\n\
				exit repeat\n\
			end if\n\
			set idx to idx + 1\n\
		end repeat\n\
	end repeat\n\
end tell'".format(skimPID, sf.Wr.Data.TokenIDs.AppIds.skim_ID, docNameId)
    return skimCloseWindowCmd


def closeVscodeWindow(vscodePID, winNameID):
    cmd = "click button 1 of theWindow\n"
    outCmd = getCmdToRunOnProcessWindow(vscodePID, winNameID, cmd)
    return outCmd


def closeFinderWindow(finderPID, winNameID):
    cmd = "click button 1 of theWindow\n"
    outCmd = getCmdToRunOnProcessWindow(finderPID, winNameID, cmd)
    return outCmd

def closeNoteAppWindow(noteAppPID, winNameID):
    cmd = "click button 1 of theWindow\n"
    outCmd = getCmdToRunOnProcessWindow(noteAppPID, winNameID, cmd)
    return outCmd


def getCmdToRunOnProcessWindow(vscodePID, winNameID, cmd):
    outCmd = "osascript -e '\
tell application \"System Events\"\n\
	set processList to every process whose unix id is {0}\n\
	repeat with proc in processList\n\
		tell proc\n\
			repeat with theWindow in windows\n\
				set n to name of theWindow\n\
				if n contains \"{1}\" then\n\
					tell theWindow\n\
						{2}\
					end tell\n\
				end if\n\
			end repeat\n\
		end tell\n\
	end repeat\n\
end tell'".format(vscodePID, winNameID, cmd)
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


def openNotesAppNotebook(link):
	cmd = "\
osascript -e '\n\
    tell application \"System Events\" to tell process \"GoodNotes\"\n\
	click menu item \"New\" of menu 1 of menu bar item \"File\" of menu bar 1\n\
end tell\n\
do shell script \"open -a GoodNotes {0}\"\n\
'".format(link)
	return cmd

def addNoteTheToThePage(docToken, page, noteText, bounds):
	cmd = "\
osascript -e '\n\
	tell application \"{0}\"\n\
		repeat with d in documents\n\
			set n to name of d\n\
			if n contains \"{1}\" then\n\
				tell d\n\
					tell page {2}\n\
                        repeat with nt in notes\n\
							set nttext to text of nt\n\
                            if nttext contains \"{3}\"\n\
								return\n\
							end if\n\
                        end repeat\n\
						set nt to (make new note with properties {{type:text note}})\n\
						set text of nt to \"{3}\"\n\
						set bounds of nt to {{{4}, {5}, {6}, {7}}}\n\
					end tell\n\
                end tell\n\
			end if\n\
            save\n\
		end repeat\n\
	end tell\
'".format(sf.Wr.Data.TokenIDs.AppIds.skim_ID, docToken, page, noteText, *bounds)
     
	return cmd

def deleteAllNotesFromThePage(docToken, page):
	cmd = "\
osascript -e '\n\
	tell application \"{0}\"\n\
		repeat with d in documents\n\
			set n to name of d\n\
			if n contains \"{1}\" then\n\
				tell d\n\
					tell page {2}\n\
                        set nList to notes\n\
						repeat with i from 1 to count nList\n\
							set nt to item i of nList\n\
							set nttext to text of nt\n\
							if nttext contains \"KIK\" then\n\
								delete item i of nList\n\
							end if\n\
						end repeat\n\
					end tell\n\
					save\n\
                end tell\n\
			end if\n\
		end repeat\n\
	end tell\
'".format(sf.Wr.Data.TokenIDs.AppIds.skim_ID, docToken, page)
     
	return cmd

def get_BoundsOfThePage(docToken, page = 1):
	cmd = "\
osascript -e '\n\
	tell application \"{0}\"\n\
		repeat with d in documents\n\
			set n to name of d\n\
			if n contains \"{1}\" then\n\
                tell d\n\
                    tell page {2}\n\
                        return bounds\n\
                    end tell\n\
                end tell\n\
            end if\n\
            save\n\
		end repeat\n\
	end tell\
'".format(sf.Wr.Data.TokenIDs.AppIds.skim_ID, docToken, page)
    
	return cmd

def get_NumberOfNotes(docToken, page = 1):
	cmd = "\
osascript -e '\n\
	tell application \"{0}\"\n\
		repeat with d in documents\n\
			set n to name of d\n\
			if n contains \"{1}\" then\n\
                tell d\n\
                    tell page {2}\n\
                        return count of notes\n\
                    end tell\n\
                end tell\n\
            end if\n\
            save\n\
		end repeat\n\
	end tell\
'".format(sf.Wr.Data.TokenIDs.AppIds.skim_ID, docToken, page)
    
	return cmd


