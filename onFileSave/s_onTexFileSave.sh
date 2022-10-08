CALLER_TEX_FILEPATH=${1%????????}_main.tex
CALLER_TEX_DIR_FILEPATH=$2

pushd ${BOOKS_PY_APP_PATH}
    python3 -c "from _utils import _utils; _utils.TexFile._populateMainFile()"
popd

pushd ${CALLER_TEX_DIR_FILEPATH}
    pdflatex  --shell-escape -xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=${CALLER_TEX_DIR_FILEPATH}/latex_output ${CALLER_TEX_FILEPATH}
    cp ${CALLER_TEX_DIR_FILEPATH}/latex_output/*.pdf ./
popd