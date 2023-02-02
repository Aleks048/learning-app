#!/bin/bash
DIR_NAME=`dirname -- "$( readlink -f -- "$0"; )"`
LINK_SCRIPT_PATH=${DIR_NAME}/link_funcs.sh
echo "sourcing: "${LINK_SCRIPT_PATH}
source ${LINK_SCRIPT_PATH}

# extract the data
URL=$1
IFS='//' read -a removeUrlName <<< ${URL}
removeUrlNameArr=(${removeUrlName})
IFS='.' read -a data <<< ${removeUrlNameArr[1]}
dataArr=(${data})
BOOK_NAME=${dataArr[0]}
TOP_SECTION=${dataArr[1]}
SUBSECTION=${dataArr[2]}
POSITION_IDX=${dataArr[3]}

echo "The data is: "
echo "BOOK_NAME: "${BOOK_NAME}
echo "TOP_SECTION: "${TOP_SECTION}
echo "SUBSECTION: "${SUBSECTION}
echo "POSITION_IDX: "${POSITION_IDX}

# call the pyapp
link ${POSITION_IDX} ${TOP_SECTION} ${SUBSECTION} ${BOOK_NAME}