echo >/dev/null # >nul & GOTO WINDOWS & rem ^
set -e
first_arg="$1"
shift
cd ${PROJECT_ROOT}/first_arg
project work-on -w first_arg "$@"
exit 0
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
:WINDOWS
set "after_1st= "
:parse_args
if "%~1" NEQ "" (
 after_1st=%afterfirst% "%~1"
 goto :parse_args
)
cd %PROJECT_ROOT%\%1
project work-on -w %1 %afterfirst%
