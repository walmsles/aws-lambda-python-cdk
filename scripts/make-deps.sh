#!/bin/bash

for folder in $(ls -d ${WORKDIR:-${PWD}}/services/* | grep -v __pycache__)
do
    if [[ -d ${folder} ]]; then
        group=$(basename ${folder})

        # check if service group exists (to avoid poetry errors)
        poetry show --with=${group} --quiet
        group_exists=$?
        all_groups=""
        if [[ $group_exists -eq 0 ]]; then
            # export main dependencies AND specific group dependencies
            echo creating requirements in ${folder}

            # collect groups to export for testing which requires ALL deps
            all_groups="${all_groups} --with=${group}"
            poetry export --without-hashes --with=${group} --with main > ${folder}/runtime/requirements.txt
        else
            # export main only - so get centrally installed dependencies
            echo creating requirements in ${folder}
            poetry export --without-hashes --with main > ${folder}/runtime/requirements.txt
        fi
    fi
done

# export for testing
poetry export --without-hashes --with dev $all_groups > ${WORKDIR:-${PWD}}/tests/requirements.txt
