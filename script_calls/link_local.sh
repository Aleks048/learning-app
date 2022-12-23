#!/bin/bash

local_link () {
    sec_place_id = $1
    sec_place_page = ${sec_place_id}

    # get numbers that we add to the found lines
    pushd ${BOOKS_PY_APP_PATH}
        cmd="import outside_calls.links_local as ll; ll.getCurrSectionMoveNumbers(${sec_place_id});"
        movenumbersarray=(`python3 -c "${cmd}"`)
    popd

    # move tex TOC file to desired
    tocline=${movenumbersarray[1]}
    code -g ${toc_tex_abs_path}:${tocline}:0

    # move tex content file to desired position
    conline=${movenumbersarray[0]}
    code -g ${con_tex_abs_path}:${conline}:0

    # move skim to desired position
    open "skim://${sec_pdf_abs_path}#page=${sec_pdf_page}"
}
