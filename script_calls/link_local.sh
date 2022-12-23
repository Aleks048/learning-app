#!/bin/bash

local_link () {
    con_tex_abs_path = $1
    toc_tex_abs_path = $2
    sec_pdf_abs_path = $3
    sec_place_id = $4
    sec_place_page = ${sec_place_id}

    # conIDX_line=`grep -n "% THIS IS CONTENT id: ${sec_place_id}" "${con_tex_abs_path}" | cut -d: -f1`
    # tocIDX_line=`grep -n "% THIS IS CONTENT id: ${sec_place_id}" "${toc_tex_abs_path}" | cut -d: -f1`

    # get numbers that we add to the found lines
    pushd ${BOOKS_PY_APP_PATH}
        cmd="import outside_calls.links_local as ll; ll.;"
        movenumbersarray=(`python3 -c "${cmd}"`)
    popd

    # move tex TOC file to desired
    # tocline=`expr $tocIDX_line + ${movenumbersarray[1]}`
    tocline=${movenumbersarray[1]}
    code -g ${toc_tex_abs_path}:${tocline}:0

    # move tex content file to desired position
    # conline=`expr $conIDX_line + ${movenumbersarray[0]}`
    conline=${movenumbersarray[0]}
    code -g ${con_tex_abs_path}:${conline}:0

    # move skim to desired position
    open "skim://${sec_pdf_abs_path}#page=${sec_pdf_page}"
}
