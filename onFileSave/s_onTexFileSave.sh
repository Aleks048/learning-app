# set -e
CALLER_TEX_FILEPATH=${1%????????}_main.tex
CALLER_TEX_DIR_FILEPATH=$2

pushd ${BOOKS_PY_APP_PATH}
    CMD="from tex_file import tex_file_manager as tm; tm.Wr.TexFile._populateMainFile()"
    echo "Running command: "$CMD
    python3 -c "$CMD"
popd

pushd ${CALLER_TEX_DIR_FILEPATH}
    CMD="pdflatex  --shell-escape -xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=${CALLER_TEX_DIR_FILEPATH}/_out ${CALLER_TEX_FILEPATH}"
    echo "Running command:"$CMD
    $CMD

    CMD="cp ${CALLER_TEX_DIR_FILEPATH}/_out/*.pdf ./"
    echo "Running command:"$CMD
    $CMD

popd