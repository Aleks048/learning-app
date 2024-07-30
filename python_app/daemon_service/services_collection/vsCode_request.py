import time
import os
import sys

import _utils.logging as log

import file_system.file_system_facade as fsf

import layouts.layouts_facade as lm

import data.temp as dt

import UI.widgets_facade as wf

import outside_calls.outside_calls_facade as oscf

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import settings.facade as sf
import scripts.osascripts as oscr


def processCall(vsCodeFilePath:str, shouldDelete:str):
    log.autolog("Processing vscode request.")

    shouldDelete = shouldDelete == 'delete'

    subsection = fsf.Data.Book.currSection
    imIdx = fsf.Data.Book.entryImOpenInTOC_UI
    relFilepath = ""

    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

    subsectionCodeprojectPath = _upan.Paths.Section.getCodeRootAbs(bookPath, subsection)

    bookCodeFilesRoot = _upan.Paths.Book.Code.getAbs(bookPath)

    if bookCodeFilesRoot in vsCodeFilePath:
         # ask the user if we wnat to proceed.
        if not shouldDelete:
            msg = "Do you want to add marker for book code project \n\n'{0}_{1}'?".format(subsection, imIdx)
        else:
            msg = "Do you want to delete marker for book code project \n\n'{0}_{1}'?".format(subsection, imIdx)
        
        response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

        mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.MathMenuManager)
        mainManager.show()

        if not response:
            return

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

        bookCodeFilesRoot = _upan.Paths.Book.Code.getAbs(bookPath)

        relFilepath = vsCodeFilePath.replace(bookCodeFilesRoot + "/", "")

        log.autolog(f"\
Add marker to VsCode for book project for file '{relFilepath}'\n\
for '{subsection}':'{imIdx}'")

        bookCodeFile:dict = fsf.Data.Sec.bookCodeFile(fsf.Data.Book.currSection)

        if not shouldDelete:
            if bookCodeFile.get(imIdx) == None:
                bookCodeFile[imIdx] = relFilepath
                fsf.Data.Sec.bookCodeFile(fsf.Data.Book.currSection, bookCodeFile)

                return _upan.Names.codeLineMarkerBook(subsection, imIdx)
            else:
                return "CODE_MARKER: marker is already present. Please remove before adding."
        else:
            if bookCodeFile.get(imIdx) == None:
                _u.log.autolog("Deleting the marker for book code project for {subsection}_{imIdx}.\n Marker not present.")
                return "CODE_MARKER: delete marker is not present. "
            else:
                _u.log.autolog("Deleting the marker for book code project for {subsection}_{imIdx}")
                bookCodeFile.pop(imIdx)
                fsf.Data.Sec.bookCodeFile(fsf.Data.Book.currSection, bookCodeFile)

                return _upan.Names.codeLineMarkerBook(subsection, imIdx)

    elif subsectionCodeprojectPath in vsCodeFilePath:
         # ask the user if we wnat to proceed.
        if not shouldDelete:
            msg = "Do you want to add marker for subsection code project \n\n'{0}_{1}'?".format(subsection, imIdx)
        else:
            msg = "Do you want to delete marker for subsection code project \n\n'{0}_{1}'?".format(subsection, imIdx)

        response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

        mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.MathMenuManager)
        mainManager.show()

        if not response:
            return

        relFilepath = vsCodeFilePath.replace(subsectionCodeprojectPath + "/", "")

        log.autolog(f"\
Add marker to VsCode for subsection project for file '{relFilepath}'\n\
for '{subsection}':'{imIdx}'")
        subsectionCodeFile:dict = fsf.Data.Sec.subsectionCodeFile(fsf.Data.Book.currSection)

        if not shouldDelete:
            if subsectionCodeFile.get(imIdx) == None:
                subsectionCodeFile[imIdx] = relFilepath
                fsf.Data.Sec.subsectionCodeFile(fsf.Data.Book.currSection, subsectionCodeFile)

                return _upan.Names.codeLineMarkerSubsection(subsection, imIdx)
            else:
                return "CODE_MARKER: marker is already present. Please remove before adding" 
        else:
            if subsectionCodeFile.get(imIdx) == None:
                _u.log.autolog("Deleting the marker for subsection code project for {subsection}_{imIdx}.\n Marker not present.")
                return "CODE_MARKER: delete marker is not present."
            else:
                _u.log.autolog("Deleting the marker for subsection code roject for {subsection}_{imIdx}")
                subsectionCodeFile.pop(imIdx)
                fsf.Data.Sec.subsectionCodeFile(fsf.Data.Book.currSection, subsectionCodeFile)

                return _upan.Names.codeLineMarkerSubsection(subsection, imIdx)

    return "CODE_MARKER: marker is already present. Please remove before adding" 