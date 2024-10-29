import _utils.logging as log
import file_system.file_system_facade as fsf
import _utils.pathsAndNames as _upan
import file_system.file_system_facade as fsf

def processCall(call:str):
    log.autolog("Processing browser request: '{0}'.".format(call))

    request = call.split("/_/")

    currSection = fsf.Data.Book.currSection
    currEntry = fsf.Data.Book.entryImOpenInTOC_UI

    if "getCurrent" == request[1]:
        wikiPagesForEntries:dict = fsf.Data.Sec.wikiPages(currSection)

        if wikiPagesForEntries.get(currEntry) != None:

            return fsf.Data.Sec.wikiPages(currSection)[currEntry]
        else:
            return {}
    elif "addSearchPage" == request[1]:
        '''
        'KIK:/_/addSearchPage/_/" + wurl
                            + "/_/" + name + "/_/" + text + "'";
        '''
        page = request[2]
        name = request[3]
        searchText = request[4]

        #currEntry = fsf.Data.Book.entr
        wikiPagesForEntries:dict = fsf.Data.Sec.wikiPages(currSection)

        if wikiPagesForEntries.get(currEntry) != None:
            wikiPages = wikiPagesForEntries[currEntry]
            if type(wikiPages) != dict:
                wikiPages = {}

            if wikiPages.get(page) == None:
                wikiPages[page] = {name: searchText}
            else:
                wikiPage:dict = wikiPages[page]

                if wikiPage.get(None) == None:
                    wikiPage[name] = searchText
                    wikiPages[page] = wikiPage
                else:
                    _upan.log.autolog(f"Please choose a different name '{name}'.")
        else:
            wikiPagesForEntries[currEntry] = {page: {name: searchText}}
        
        log.autolog(f"Adding link for '{currSection}:{currEntry}' to '{page}' with name '{name}' and text '{searchText}'")
        fsf.Data.Sec.wikiPages(currSection, wikiPagesForEntries)
    elif "deletePage" == request[1]: 
        '''
        'KIK://deletePage//" + wurl + "'"
        '''
        page = request[2]

        wikiPagesForEntries:dict = fsf.Data.Sec.wikiPages(currSection)

        if wikiPagesForEntries.get(currEntry) != None:
            wikiPages = wikiPagesForEntries[currEntry]

            if wikiPages.get(page) == None:
                _upan.log.autolog(f"Cannot delete page '{page}' since it is not present.")
            else:
                wikiPages.pop(page)
                wikiPagesForEntries[currEntry] = wikiPages
                fsf.Data.Sec.wikiPages(currSection, wikiPagesForEntries)
    elif "deleteName" == request[1]:
        '''
        " 'KIK://deleteName//" + wurl
                      + "//" + name + "'"
        '''
        page = request[2]
        name = request[3]

        wikiPagesForEntries:dict = fsf.Data.Sec.wikiPages(currSection)

        if wikiPagesForEntries.get(currEntry) != None:
            wikiPages = wikiPagesForEntries[currEntry]

            if wikiPages.get(page) == None:
                _upan.log.autolog(f"Cannot delete name '{name}' for page '{page}' since page is not present.")
            else:
                wikiPage:dict = wikiPages[page]

                if wikiPage.get(name) == None:
                    _upan.log.autolog(f"Cannot delete name '{name}' for page '{page}' since name is not present.")
                else:
                    wikiPage.pop(name)
                    wikiPages[page] = wikiPage
                    wikiPagesForEntries[currEntry] = wikiPages
                    fsf.Data.Sec.wikiPages(currSection, wikiPagesForEntries)
    elif "updateLinkName" == request[1]:
        '''
            'KIK://updateLinkName//" + url + "//" + newname + "//" + oldName '
        '''
        url = request[2]
        newName = request[3]
        oldName = request[4]

        wikiPagesForEntries:dict = fsf.Data.Sec.wikiPages(currSection)

        if wikiPagesForEntries.get(currEntry) != None:
            wikiPages = wikiPagesForEntries[currEntry]
            wikiPage = wikiPages[url]
            wikiPage[newName] = wikiPage.pop(oldName)
            wikiPages[url] = wikiPage
            wikiPagesForEntries[currEntry] = wikiPages
            fsf.Data.Sec.wikiPages(currSection, wikiPagesForEntries)
    elif "updateLinkSearchText" == request[1]:
        '''
            'KIK://updateLinkName//" + url + "//" + newname + "//" + oldName '
        '''
        url = request[2]
        name = request[3]
        newSerachText = request[4]

        wikiPagesForEntries:dict = fsf.Data.Sec.wikiPages(currSection)

        if wikiPagesForEntries.get(currEntry) != None:
            wikiPages = wikiPagesForEntries[currEntry]
            wikiPage = wikiPages[url]
            
            wikiPage[name] = newSerachText
            wikiPages[url] = wikiPage
            wikiPagesForEntries[currEntry] = wikiPages

            fsf.Data.Sec.wikiPages(currSection, wikiPagesForEntries)