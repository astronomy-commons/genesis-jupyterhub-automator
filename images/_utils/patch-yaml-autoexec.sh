#!/bin/bash
#
# in-place patch a yaml file tagged at a location tagged with the #automator entry
# example: $0 ../values.yaml autoexec.sh
#

[[ -z "$1" ]] && { echo "usage; $0 <values.yaml> [autoexec.sh]" 1>&2; exit -1; }

YAML="$1"
AEX="$2"

set -e

find_line()
{
	TAG="$1"

	LINE=$(grep -n "#automator: $TAG" "$YAML")
	[[ -z $LINE ]] && { echo "no #automator tag found, exiting." 1>&2; exit -1; }

	# line number
	AT=${LINE%%:*}
	# prefix length
	PREFIX=${LINE#*:}
	PREFIX=${PREFIX%%"#automator:"*}
	
	echo "$AT"
}

ATBEG=$(find_line "autoexec_begin")
ATEND=$(find_line "autoexec_end")

(
	# print front
	head -n $ATBEG "$YAML"

	if [[ -n $AEX && -f $AEX ]]; then
		cat <<-EOF
		  lifecycleHooks:
		    postStart:
		      exec:
		        command:
		          - "/bin/sh"
		          - "-c"
		          - |
		$(sed 's/^/            /' "$AEX")
		EOF
	fi

	# print back
	tail -n +$((ATEND)) "$YAML"
) > "$1.tmp"

# replace old file
mv "$1.tmp" "$1"
