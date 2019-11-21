#!/bin/bash
#
# in-place patch a yaml file tagged at a location tagged with the #automator entry
# example: $0 ../../etc/values.yaml hub.image mjuric/k8s-hub-dirac:0.9.0-alpha.1.020.c70f016-mjuric1
#

[[ -z "$3" ]] && { echo "usage; $0 <file> <tag> <image_name:image_tag>" 1>&2; exit -1; }

YAML="$1"
TAG="$2"
IMAGE_NAME="${3%%:*}"
IMAGE_TAG="${3##*:}"

set -e

LINE=$(grep -n "#automator: $TAG" "$YAML")
[[ -z $LINE ]] && { echo "no #automator tag found, exiting." 1>&2; exit -1; }

# line number
AT=${LINE%%:*}
# prefix length
PREFIX=${LINE#*:}
PREFIX=${PREFIX%%"#automator:"*}

(
	# print front
	head -n $AT "$YAML"

	echo "${PREFIX}name: $IMAGE_NAME"
	echo "${PREFIX}tag: $IMAGE_TAG"

	# print back
	tail -n +$((AT+3)) "$YAML"
) > "$1.tmp"

# replace old file
mv "$1.tmp" "$1"
