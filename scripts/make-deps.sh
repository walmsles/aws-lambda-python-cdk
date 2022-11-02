#!/bin/bash

for folder in $(ls -d ${WORKDIR:-${PWD}}/services/* | grep -v __pycache__)
do
    if [[ -d ${folder}/runtime ]]; then
        group=$(basename ${folder})
        if [[ $(poetry show --only=${group}) ]]; then
            echo creating requirements in ${folder}/runtime
            poetry export --without-hashes --with=${group} > ${folder}/runtime/requirements.txt
        fi
    fi
done
