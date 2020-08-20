echo >/dev/null # >nul & GOTO WINDOWS & rem ^
set -e
first_arg="$1"
shift
cd ${PROJECT_ROOT}/first_arg
project work-on -w first_arg "$@"
activate first_arg
exit 0
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
REM experimental dont use
:WINDOWS
set _tail=%*
call set _tail=%%_tail:*%1=%%
cd %PROJECT_ROOT%\%1
project work-on -w %1 %_tail%
activate %1
