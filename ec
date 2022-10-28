#!/bin/bash 

params=()

if [ "`hostname`" == "chl-spdsiml7" ]; then
  for p in "$@"; do
    params+=( "$p" ) 
  done

else
  params+=("-c")
  for p in "$@"; do
    params+=( "/ssh:"`hostname`":"$(readlink -f $p) )
  done

  scp -q chl-spdsiml7:emacs-server ~
fi

params+=("-f")
params+=(`readlink -f ~/emacs-server` )

echo emacsclient "${params[@]}"
emacsclient -n "${params[@]}"
