import pathlib
import os
import _utils._utils_main as _u
import settings.facade as sf

import outside_calls.outside_calls_facade as ocf

def readFromDict(word):
    word = word.lower()

    parentPath = pathlib.Path(__file__).parent.resolve()
    jsonDict:dict = \
        _u.JSON.readFile(os.path.join(parentPath, "data/dictionary_alpha_arrays.json"))[ord(word[0]) - 97]
    return jsonDict.get(word)

def writeToDict(key, newValue):
    key = key.lower()

    parentPath = pathlib.Path(__file__).parent.resolve()
    jsonDict:dict = \
        _u.JSON.readFile(os.path.join(parentPath, "data/dictionary_alpha_arrays.json"))
    letterDict = jsonDict[ord(key[0]) - 97]
    letterDict[key] = newValue

    _u.JSON.writeFile(os.path.join(parentPath, "data/dictionary_alpha_arrays.json"), jsonDict)

    currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
    msg = f"After updating word dict for key {key}."
    ocf.Wr.TrackerAppCalls.stampChanges(currBookpath, msg)

def deleteFromDict(key):
    key = key.lower()

    parentPath = pathlib.Path(__file__).parent.resolve()
    jsonDict:dict = \
        _u.JSON.readFile(os.path.join(parentPath, "data/dictionary_alpha_arrays.json"))
    letterDict = jsonDict[ord(key[0]) - 97]
    letterDict.pop(key)

    _u.JSON.writeFile(os.path.join(parentPath, "data/dictionary_alpha_arrays.json"), jsonDict)

    currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
    msg = f"After deleting key '{key}' from word dict."
    ocf.Wr.TrackerAppCalls.stampChanges(currBookpath, msg)