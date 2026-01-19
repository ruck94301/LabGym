# INIT -- Define ERROR, IS_VENV functions.
#
# Usage
#     source INIT.sh

# Like python's corresponding logger methods, these produce tagged
# messages on stderr.
ERROR () { printf "$(NOW)\tERROR\t%s\n" "$(printf "$@")" >& 2; }
INFO () { printf "$(NOW)\tINFO\t%s\n" "$(printf "$@")" >& 2; }
DEBUG () { printf "$(NOW)\tDEBUG\t%s\n" "$(printf "$@")" >& 2; }

# Like python's sys.exit function, EXIT is called with either no args,
# an integer arg, or a message arg.
#     "EXIT" is equivalent to "exit 0"
#     "EXIT $?" is equivalent to "exit" and "exit $?"
#     "EXIT 2" is equivalent to "exit 2"
#     "EXIT -2" is equivalent to "exit -2" and "exit 254"
#     'EXIT "lorem ipsum"' is equivalent to 'ERROR "lorem ipsum"; exit 1'
# To exit with both a message and a status other than 1, use separate 
# ERROR and EXIT statements.
EXIT () {
    [ $# -eq 0 ] && exit 0
    [ $# -eq 1 ] && IS_INT $1 && exit $1
    { ERROR "$@"; exit 1; }
}

IS_VENV () { [ -n "$VIRTUAL_ENV+1" ]; }  # works in sh, bash, and zsh
IS_INT () { [ $# -eq 1 ] && expr $1 + 0 > /dev/null 2>& 1; }

NOW () { date +%FT%T; }  # 2026-01-19T08:23:02
NOW_FS () { date +%FT%T | tr -d :; }  # 2026-01-19T082302, for filenames
NOW_HMS () { date +%T; }  # 08:23:02

AWK () { awk "$@"; }
    
# To use sh behavior...
# setopt SH_WORD_SPLIT 2> /dev/null || true

return
# if return failed, then this script is being executed in its own shell
ERROR "bad usage -- source $0 instead of executing it in its own shell"
exit 1
