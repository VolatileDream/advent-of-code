#!/bin/bash

permutations() {
  python3 -c "
import itertools
for p in itertools.permutations([5,6,7,8,9]):
  print(p[0], p[1], p[2], p[3], p[4]);
"
}

run() {
  local -ra phases=($@)

  # Where we dump all the fifos.
  local -r tmpdir=`mktemp -d`

  # Setup fifos.
  mkfifo "${tmpdir}/e-to-a"
  mkfifo "${tmpdir}/a-to-b"
  mkfifo "${tmpdir}/b-to-c"
  mkfifo "${tmpdir}/c-to-d"
  mkfifo "${tmpdir}/d-to-e"

  ./main.py input --start-io="${phases[0]},0" 0<"${tmpdir}/e-to-a" 1>"${tmpdir}/a-to-b" &
  ./main.py input --start-io="${phases[1]}" 0<"${tmpdir}/a-to-b" 1>"${tmpdir}/b-to-c" &
  ./main.py input --start-io="${phases[2]}" 0<"${tmpdir}/b-to-c" 1>"${tmpdir}/c-to-d" &
  ./main.py input --start-io="${phases[3]}" 0<"${tmpdir}/c-to-d" 1>"${tmpdir}/d-to-e" &
  # Last one is special, we wait for it to exit.
  ./main.py input --start-io="${phases[4]}" 0<"${tmpdir}/d-to-e" | tee "${tmpdir}/e-to-a" "${tmpdir}/e-output" > /dev/null

  tail -n 1 "${tmpdir}/e-output" | tr -d '\n' ; echo " -- ${phases[@]}"
  rm -r "$tmpdir"
}

main() {
  permutations |
    while read line; do
      # no escape, we want to split the string of permutations
      run $line
    done | sort -n
}

main
