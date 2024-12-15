
# definitions needed for standalone call
PIHOME=/home/pi
LIB=lib
LIB_PATH=$PIHOME/$LIB
SCRIPT=$LIB_PATH/script_tools
RFRTOOLS=$LIB_PATH/RFR_Tools
PYTHON_SCRIPTS=$RFRTOOLS/miscellaneous
REPO_PACKAGE=Dexter_AutoDetection_and_I2C_Mutex
OS_CODENAME=$(lsb_release --codename --short)

################################################
######## Parsing Command Line Arguments ########
################################################

# called way down bellow
check_if_run_with_pi() {
  ## if not running with the pi user then exit
  if [ $(id -ur) -ne $(id -ur pi) ]; then
    echo "RFR_Tools installer script must be run with \"pi\" user. Exiting."
    exit 4
  fi
}

parse_cmdline_arguments() {
  # the following option is required should the python package be installed
  # by default, the python package are not installed
  installpythonpkg=false

  # the following 3 options are mutually exclusive
  systemwide=true
  userlocal=false
  envlocal=false
  usepython3exec=true

  # the following 2 options can be used together
  updatedebs=false
  installdebs=false

  # the following option is not a dependent
  # and if installdebs is not enabled then this one cannot be enabled
  installgui=false

  # the following option tells which branch has to be used
  selectedbranch="master" # set to master by default

  # iterate through bash arguments
  for i; do
    case "$i" in
      --install-python-package)
        installpythonpkg=true
        ;;
      --user-local)
        userlocal=true
        systemwide=false
        ;;
      --env-local)
        envlocal=true
        systemwide=false
        ;;
      --system-wide)
        ;;
      --update-aptget)
        updatedebs=true
        ;;
      --install-deb-deps)
        installdebs=true
        ;;
      --use-python3-exe-too)
        usepython3exec=true
        ;;
      --install-gui)
        installgui=true
        ;;
      develop|feature/*|hotfix/*|fix/*|DexterOS*|v*)
        selectedbranch="$i"
        ;;
    esac
  done

  echo "Updating RFR_Tools with the following options:"
  echo "  --install-python-package=$installpythonpkg"
  echo "  --system-wide=$systemwide"
  echo "  --user-local=$userlocal"
  echo "  --env-local=$envlocal"
  echo "  --use-python3-exe-too=$usepython3exec"
  echo "  --update-aptget=$updatedebs"
  echo "  --install-deb-deps=$installdebs"
  echo "  --install-gui=$installgui"
}

################################################
###### Update and Install with Apt-Get  ########
################################################

# called way down bellow
update_install_aptget() {
  if [[ $updatedebs = "true" ]]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash - 
  fi
  [[ $installdebs = "true" ]] && \
    echo && \
    echo "Installing debian dependencies within RFR_Tools. This might take a while.." && \
    echo && \
    sudo apt-get install -y --no-install-recommends \
                         build-essential \
                         libi2c-dev \
                         i2c-tools \
                         python3-dev \
                         python3-setuptools \
                         python3-pip \
                         libffi-dev \
                         nodejs
}

install_pythons() {
  # needed on Bullseye
  if [[ $OS_CODENAME != "bookworm" ]]; then
  command -v python2 >/dev/null 2>&1 || { feedback "installing python2"; sudo apt install python2 -y; }
  else
     echo Bypassing python2 for Bookworm.
  fi
  # needed on Stretch
  command -v python3 >/dev/null 2>&1 || { feedback "installing python3" ;sudo apt install python3 -y; }

  # exit if python2/python3 are not installed in the current environment
  if [[ $installpythonpkg = "true" ]]; then
    if [[ $OS_CODENAME != "bookworm" ]]; then
      command -v python2 >/dev/null 2>&1 || { echo "Executable \"python\" couldn't be found. Aborting." >&2; exit 2; }
    fi
    if [[ $usepython3exec = "true" ]]; then
      command -v python3 >/dev/null 2>&1 || { echo "Executable \"python3\" couldn't be found. Aborting." >&2; exit 3; }
    fi
  fi
}

install_script_tools() {
  echo
  echo "Installing script_tools."
  echo
  # needs to be sourced from here when we call this as a standalone
  source $SCRIPT/functions_library.sh
  feedback "Done installing script_tools"
}

################################################
######## Install/Remove Python Packages ########
################################################

# called by <<install_python_pkgs_and_dependencies>>
install_python_packages() {
  cd $PYTHON_SCRIPTS
  install_python_setup
  
  cd $LIB_PATH/smbus-cffi
  install_python_setup

  cd
}

# called by <<install_python_pkgs_and_dependencies>>
remove_python_packages() {
  # the 1st and only argument
  # takes the name of the package that needs to removed
  rm -f $PIHOME/.pypaths

  # get absolute path to python package
  # saves output to file because we want to have the syntax highlight working
  # does this for both root and the current user because packages can be either system-wide or local
  # later on the strings used with the python command can be put in just one string that gets used repeatedly
  if [[ $OS_CODENAME != "bookworm" ]]; then
  python2 -c "import pkgutil; import os; \
              eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
              output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  sudo python2 -c "import pkgutil; import os; \
              eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
              output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  fi
  if [[ $usepython3exec = "true" ]]; then
    python3 -c "import pkgutil; import os; \
                eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
                output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
    sudo python3 -c "import pkgutil; import os; \
                eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
                output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  fi

  # removing eggs for $1 python package
  # ideally, easy-install.pth needs to be adjusted too
  # but pip seems to know how to handle missing packages, which is okay
  while read path;
  do
    if [ ! -z "${path}" -a "${path}" != " " ]; then
      echo "Removing ${path} egg"
      sudo rm -f "${path}"
    fi
  done < $PIHOME/.pypaths
}

# called way down bellow
install_remove_python_packages() {
  if [[ $installpythonpkg = "true" ]]; then
    echo
    echo "Removing \"$REPO_PACKAGE\" to make space for the new one"
    echo
    remove_python_packages "$REPO_PACKAGE"

    echo
    echo "Installing python package for RFR_Tools "
    echo
    # installing the package itself
    install_python_packages
  fi
}

install_guis() {
    if [[ $installgui = "true" ]]; then
      cd $RFRTOOLS/advanced_communication_options
      bash install.sh
      cd ../Scratch_GUI
      bash install.sh
      cd ../Troubleshooting_GUI
      bash install.sh
      cd
    fi
}
################################################
############ Calling All Functions  ############
################################################

check_if_run_with_pi
parse_cmdline_arguments "$@"
install_script_tools
install_pythons
update_install_aptget
install_remove_python_packages
install_guis
feedback "Done installing RFR_Tools library"
exit 0
