#!/bin/bash

local_link () {
    sec_bookpath=$1
    sec_place_id=$2
    bookpath=$3

    # get numbers that we add to the found lines
    pushd ${BOOKS_PY_APP_PATH}
        cmd="import outside_calls.link_local as ll; ll.processLinkCall('${sec_place_id}', '${sec_bookpath}', '${bookpath}');"
        movenumbersarray=(`python3 -c "${cmd}"`)
    popd
}