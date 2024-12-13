##############################################################
##############################################################
# 
# A SERIES OF HELPER FUNCTIONS TO HELP OUT IN 
# HANDLING SCRIPTS THAT ARE GROWING IN COMPLEXITY
#
##############################################################
##############################################################

quiet_mode() {
  # verify quiet mode
  # returns 0 if quiet mode is enabled
  # returns 1 otherwise
  if [ -f /home/pi/quiet_mode ]
  then
    return 0
  else
    return 1
  fi
}

set_quiet_mode(){
  touch /home/pi/quiet_mode
}

unset_quiet_mode(){
  delete_file /home/pi/quiet_mode
}


feedback() {
  # first parameter is text to be displayed
  # this sets the text color to a yellow color for visibility
  # the last tput resets colors to default
  # one could also set background color with setb instead of setaf
  #http://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x405.html
  echo -e "$(tput setaf 3)$1$(tput sgr0)"
}

#########################################################################
#
#  SCRIPT HELPERS
#
#########################################################################
where_am_i() {
  # return the directory where the script resides, 
  # path is relative to where it was called from
  # includes the filename
  # call like this:  here=$(where_am_i)
  echo $(dirname $(readlink -f $0))
}

where_am_i_fullpath() {
  # returns the full path to the folder containing the current script
  # does not contain the script name
  echo $( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )
}

who_called_me() {
  # returns the calling script if any
  # path is relative
  # otherwise returns empty
  echo ${BASH_SOURCE[1]}
}

check_internet() {
    # check if there's internet access
    # and if there's not, exit the script
    if ! quiet_mode ; then
        feedback "Check for internet connectivity..."
        feedback "=================================="
        wget -q --tries=2 --timeout=20 --output-document=/dev/null https://raspberrypi.org
        if [ $? -eq 0 ];then
            echo "Connected to the Internet"
        else
            echo "Unable to Connect, try again !!!"
            exit 0
        fi
    fi
}

#########################################################################
#
#  FILE EDITION
#
#########################################################################
delete_line_from_file() {
  # first parameter is the string to be matched
  # the lines that contain that string will get deleted
  # second parameter is the filename
  if [ -f $2 ]
  then
    sudo sed -i "/$1/d" $2
  fi
}

insert_before_line_in_file() {
  # first argument is the line that needs to be inserted DO NOT USE PATHS WITH / in them
  # second argument is a partial match of the line we need to find to insert before
  # third arument is filename

  if [ -f $3 ]
  then
    sudo sed -i "/$2/i $1" $3
  fi
}

add_line_to_end_of_file() {
  # first parameter is what to add
  # second parameter is filename
  if [ -f $2 ]
  then
    echo "$1" >> "$2"
  fi 
}

sudo_add_line_to_end_of_file() {
  if [ -f $2 ]
  then
      if ! grep "$1"  "$2" 
      then
        sudo bash -c "echo $1 >> $2"
      fi
  fi 
}

replace_first_this_with_that_in_file() {
  # replaces the first occurence
  # first parameter is the string to be replaced
  # second parameter is the string which replaces
  # third parameter is the filename
  if grep -q "$1" $3
  then
    sudo sed -i "s/$1/$2/" "$3"
     return 0
  else
      #feedback "Line - $1 not found"
      return 1
  fi
}
replace_all_this_with_that_in_file(){
  # does a global replace
  # first argument: what needs to be replaced
  # second argument: the new stuff
  # third argument: the file in question
  # returns 0 if file exists (may or may not have succeeded in the substitution)
  # return 1 if file does not exists
  #feedback "replacing $1 with $2 in $3"
  if file_exists "$3"
  then
    sudo sed -i "s/$1/$2/g" "$3"
    return 0
  else
    return 1
  fi
}

find_in_file() {
  # first argument is what to look for
  # second argument is the filename
  if grep -q "$1" $2
  then
    return 0
  else
    return 1
  fi
}

find_in_file_strict() {
  # first argument is what to look for
  # second argument is the filename
  # looks for a complete word and not part of a word
  if grep -w -q "$1[\D]" $2
  then
    return 0
  else
    return 1
  fi
}

#########################################################################
#
#  FILE HANDLING - detection, deletion
#
#########################################################################
file_exists() {
  # Only one argument: the file to look for
  # returns 0 on SUCCESS
  # returns 1 on FAIL
  if [ -f "$1" ]
  then
    return 0
  else
    return 1
  fi
}

file_exists_in_folder(){
  # can only be run using bash, not sh
  # first argument: file to look for
  # second argument: folder path
  pushd $2 > /dev/null
  status = file_exists $1
  popd > /dev/null
  return status
}

file_does_not_exists(){
  # Only one argument: the file to look for
  # returns 0 on SUCCESS
  # returns 1 on FAIL
  if [ ! -f $1 ]
  then
    return 0
  else
    return 1
  fi
}

delete_file (){
  # One parameter only: the file to delete
  if file_exists "$1"
  then
    sudo rm "$1"
  fi
}

wget_file() {
  # One parameter: the URL of the file to wget
  # this will look if ther's already a file of the same name
  # if there's one, it will delete it before wgetting the new one
  # this is to avoid creating multiple files with .1, .2, .3 extensions
  echo $1
  # extract the filename from the provided path
  target_file=${1##*/}
  echo $target_file
  delete_file $target_file
  wget $1 --no-check-certificate


}

#########################################################################
#
#  FOLDER HANDLING - detection, deletion
#
#########################################################################
create_folder(){
  if ! folder_exists "$1"
  then
    sudo mkdir -p "$1"
  fi
}

create_folder_nosudo(){
  if ! folder_exists "$1"
  then
    mkdir -p "$1"
  fi
}

create_folder_nosudo(){
  if ! folder_exists "$1"
  then
    mkdir -p "$1"
  fi
}


folder_exists(){
  # Only one argument: the folder to look for
  # returns 0 on SUCCESS
  # returns 1 on FAIL
  if [ -d "$1" ]
  then
    return 0
  else
    return 1
  fi
}

delete_folder(){
  if folder_exists "$1"
  then
    sudo rm -r "$1"
  fi
}

install_python_setup(){
  if [[ $systemwide = "true" ]]; then
      if [[ $usepython3exec = "true" ]]; then
          sudo python3 setup.py install
      else
          sudo python2 setup.py install
      fi
  fi

  if [[ $userlocal = "true" ]]; then
      if [[ $usepython3exec = "true" ]]; then
          python3 setup.py install --user
      else
          python2 setup.py install --user
      fi
  fi

  if [[ $envlocal = "true" ]]; then
      if [[ $usepython3exec = "true" ]]; then
          python3 setup.py install
      else
          python2 setup.py install
      fi
  fi
}
