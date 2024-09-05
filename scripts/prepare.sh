#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

mkdir --parents --verbose data
wget --output-document data/ICT-FaceKit-master.zip https://github.com/ICT-VGL/ICT-FaceKit/archive/refs/heads/master.zip
ouch decompress --dir data/ data/ICT-FaceKit-master.zip
