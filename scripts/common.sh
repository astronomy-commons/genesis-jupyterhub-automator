#
# Common functions
#

assert_defined()
{
	for VAR in "$@"; do
		#echo $VAR: $(eval echo "\${$VAR+x}")
		if [ x$(eval echo "\${$VAR+x}") != "xx" ]; then
			echo "error: $VAR not set. aborting.";
			exit -1
		fi
		#echo "$VAR=${!VAR}"
	done
}
