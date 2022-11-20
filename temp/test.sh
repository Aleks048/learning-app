
# get stdout from python script
pushd ${BOOKS_PY_APP_PATH}
    cmd="from _utils import _utils_main as _u; _u.getCurrSectionMoveNumber();"
    outarray=(`python3 -c "${cmd}"`)
    # outarray=($out)
    echo ${outarray[0]}
    echo ${outarray[1]}
popd