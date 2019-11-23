#
# Common functions, intented to be sources by scripts that need them.
#

# Output an error message
errmsg()
{
	echo "$@" 1>&2
}

msg()
{
	[[ "$1" == "done" ]] && symbol="👍"
	[[ "$1" == "check" ]] && symbol="✅"
	[[ "$1" == "skip" ]] && symbol="⏩"

	echo "$symbol $2"
}

# Extract command-line options
option_to_varname()
{
	# takes an option such as --with-foo as an argument
	# and returns the corresponding variable name (FOO)
	key="${1%=*}"
	key="${key#--}"
	key="${key#with-}"
	key="${key//-/_}"
	echo "$key" | awk '{print toupper($0)}'
}

# Convert a variable name to equivalent option
varname_to_option()
{
	opt="${1//_/-}"
	opt=$(echo "$opt" | awk '{print tolower($0)}')
	echo "--$opt"
}

# cp_with_subst <source> <dest>
# fill out the template written in our templating mini-language.
# language rules:
#   -- "##vars FOO BAR" defines FOO BAR as variables to expand
#   -- "text txt ##if -n $GAGA" means the line will appear in output only if [[ -n $GAGA ]] evals to true
#   -- "$FOO $BAZ" will expand $FOO (as it was define in ##vars but not $BAZ
cp_with_subst()
{
	VARS=()
	while IFS= read -r line
	do
		# check if this is the ##vars line
		if [[ $line == \#\#vars* ]]; then
			VARS+=(${line#"##vars "})
			continue
		fi
	
		# expected format:
		# ...text.. ##if PREDICATE
		TEXT="${line%"##if"*}"
		PRED="${line#*"##if"}"
		[[ "$TEXT" == "$line" ]] && PRED=

		# conditional lines
		if [[ ! -z $PRED ]]; then
			if eval "[[ $PRED ]]"; then
				line="$TEXT"
			else
				continue
			fi
		fi

		# variable expansion
		for VAR in "${VARS[@]}"; do
			##echo "[[$line]] VAR=$VAR=${!VAR}" 1>&2
			line=${line//"\${$VAR}"/"${!VAR}"} #" ## <-- work around a syntax highlighting bug in joe
			line=${line//"\$$VAR"/"${!VAR}"}   #" ## <-- work around a syntax highlighting bug in joe
		done

		echo "$line"
	done < "$1" > "$2"
	##cat "$2"
}

