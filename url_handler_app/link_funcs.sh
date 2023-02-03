#!/bin/bash

link () {
    BOOK_NAME=$0
    TOP_SECTION=$1
    SUBSECTION=$2
    POSITION_IDX=$3

    # get numbers that we add to the found lines
    pushd ${BOOKS_PY_APP_PATH}
        cmd="import rpyc; c = rpyc.connect(\"localhost\", 12345).root; c.processLink('${BOOK_NAME}', '${TOP_SECTION}', '${SUBSECTION}', '${POSITION_IDX}')"
        python3 -c "${cmd}"
    popd
}

local_link () {
    sec_place_id=$1
    sec_bookpath=$2
    bookpath=$3

    # get numbers that we add to the found lines
    pushd ${BOOKS_PY_APP_PATH}
        cmd="import outside_calls.link_local as ll; ll.processLocalLinkCall('${sec_place_id}', '${sec_bookpath}', '${bookpath}');"
        movenumbersarray=(`python3 -c "${cmd}"`)
    popd
}

global_link () {
    sec_place_id=$1
    sec_bookpath=$2
    bookpath=$3

    # get numbers that we add to the found lines
    pushd ${BOOKS_PY_APP_PATH}
        cmd="import outside_calls.link_local as ll; ll.processGlobalLinkCall('${sec_place_id}', '${sec_bookpath}', '${bookpath}');"
        movenumbersarray=(`python3 -c "${cmd}"`)
    popd
}
