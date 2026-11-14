#!/bin/zsh
cd -- "${0:A:h}"
export PATH="$PWD/bin:$PATH"
printf 'PTK terminal ready. Commands: ptk doctor | u "URL" -a | ptk "/path/song.wav" -s\n'
exec /bin/zsh -i
