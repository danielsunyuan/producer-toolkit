#!/bin/zsh
cd -- "${0:A:h}"
./bin/u 'https://www.youtube.com/watch?v=wg_cpdaBYs8' -a -o "$HOME/Downloads"
result=$?
if [ "$result" -eq 0 ]; then
    open "$HOME/Downloads"
else
    printf '\nDownload failed. Check the error above and your internet connection.\n'
fi
read '?Press Return to close…'
exit "$result"
