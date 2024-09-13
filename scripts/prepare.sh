#!/bin/bash
set -o errexit -o nounset -o pipefail

mkdir --parents --verbose data
wget --output-document data/ICT-FaceKit-master.zip https://github.com/ICT-VGL/ICT-FaceKit/archive/refs/heads/master.zip
unzip data/ICT-FaceKit-master.zip -d data/
