import _utils.logging as log

import file_system.file_system_facade as fsf

import data.temp as dt

import _utils.pathsAndNames as _upan

import settings.facade as sf
import generalManger.generalManger as gm


def processCall(vsCodeFilePath:str, shouldDelete:str):
    log.autolog("Processing vscode request.")

    shouldDelete = shouldDelete == 'delete'

    subsection = fsf.Data.Book.currSection
    imIdx = dt.CodeTemp.currCodeFullLink

    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

    subsectionCodeprojectPath = _upan.Paths.Section.getCodeRootAbs(bookPath, subsection)

    bookCodeFilesRoot = _upan.Paths.Book.Code.getAbs(bookPath)


    if bookCodeFilesRoot in vsCodeFilePath:
        gm.GeneralManger.AddAddMarkerToCode(subsection=subsection, imIdx = imIdx,
                                            vsCodeFilePath = vsCodeFilePath,
                                            subsectionCodeprojectPath = subsectionCodeprojectPath,
                                            shouldDelete = shouldDelete,
                                            bookcCodeMarker = True)
    elif subsectionCodeprojectPath in vsCodeFilePath:
        gm.GeneralManger.AddAddMarkerToCode(subsection=subsection, imIdx = imIdx,
                                            vsCodeFilePath = vsCodeFilePath,
                                            subsectionCodeprojectPath = subsectionCodeprojectPath,
                                            shouldDelete = shouldDelete,
                                            bookcCodeMarker = False)

    return "CODE_MARKER: marker is already present. Please remove before adding" 