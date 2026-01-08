# INIT -- Define ERROR, IS_VENV functions.  Define PYFILES.
#
# Usage
#     source INIT.sh

ERROR () { printf "ERROR\t%s\n" "$(printf "$@")" >& 2; }
INFO () { printf "INFO\t%s\n" "$(printf "$@")" >& 2; }
DEBUG () { printf "DEBUG\t%s\n" "$(printf "$@")" >& 2; }

# like python's sys.exit function, EXIT is called with either no args,
# an integer arg, or a message.
# "EXIT" is equivalent to "exit 0"
# "EXIT $?" is equivalent to "exit"
# "EXIT 2" is equivalent to "exit 2"
# "EXIT -2" is equivalent to "exit -2" and "exit 254"
EXIT () {
    [ $# -eq 0 ] && exit 0
    [ $# -eq 1 ] && IS_INT $1 && exit $1
    { ERROR "$@"; exit 1; }
}


IS_VENV () { [ -n "$VIRTUAL_ENV+1" ]; }  # works in sh, bash, and zsh
IS_INT () { [ $# -eq 1 ] && expr $1 + 0 > /dev/null 2>& 1; }

AWK () { awk "$@"; }
    
PYFILES=$(cd .. && echo *.py)
# printf "%s: %s\n" "\$PYFILES" "$PYFILES"

# To use sh behavior...
# setopt SH_WORD_SPLIT 2> /dev/null || true

return
# if return failed, then this script is being executed in its own shell
ERROR "bad usage -- source $0 instead of executing it in its own shell"
exit 1
