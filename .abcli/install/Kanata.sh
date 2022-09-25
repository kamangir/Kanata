#! /usr/bin/env bash

function abcli_install_Kanata() {
    abcli_youtube install
    abcli_faces install
}

if [ "$abcli_is_mac" == true ] || [ "$ec" == true ] ; then
    abcli_install_module Kanata 103
fi