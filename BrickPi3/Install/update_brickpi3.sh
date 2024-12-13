#! /bin/bash

PIHOME=/home/pi
BRICKPI3_DIR=$PIHOME/BrickPi3
LIB=lib
LIB_PATH=$PIHOME/$LIB
SCRIPT=$PIHOME/lib/script_tools

# the top-level module name of each package
# used for identifying present packages
REPO_PACKAGE=brickpi3

# called way down bellow
check_if_run_with_pi() {
  ## if not running with the pi user then exit
  if [ $(id -ur) -ne $(id -ur pi) ]; then
    echo "BrickPi3 installer script must be run with \"pi\" user. Exiting."
    exit 7
  fi
}

##############################################
######## Parse Command Line Arguments ########
##############################################

# called way down below
parse_cmdline_arguments() {

  # whether to install the dependencies or not (avrdude, apt-get, wiringpi, and so on)
  installdependencies=true
  updaterepo=true
  install_rfrtools=true
  install_pkg_rfrtools=true
  install_rfrtools_gui=true

  # the following 3 options are mutually exclusive
  systemwide=true
  userlocal=false
  envlocal=false
  usepython3exec=true

  # the following option tells which branch has to be used
  # duplicated from above
  # selectedbranch="master"

  declare -ga rfrtools_options=("--system-wide")
  # iterate through bash arguments
  for i; do
    case "$i" in
      --no-dependencies)
        installdependencies=false
        ;;
      --no-update-aptget)
        updaterepo=false
        ;;
      --bypass-rfrtools)
        install_rfrtools=false
        ;;
      --bypass-python-rfrtools)
        install_pkg_rfrtools=false
        ;;
      --bypass-gui-installation)
        install_rfrtools_gui=false
        ;;
      --user-local)
        userlocal=true
        systemwide=false
        declare -ga rfrtools_options=("--user-local")
        ;;
      --env-local)
        envlocal=true
        systemwide=false
        declare -ga rfrtools_options=("--env-local")
        ;;
      --system-wide)
        ;;
      develop|feature/*|hotfix/*|fix/*|DexterOS*|v*)
        selectedbranch="$i"
        ;;
    esac
  done

  # show some feedback on the console
  if [ -f $SCRIPT/functions_library.sh ]; then
    source $SCRIPT/functions_library.sh
    # show some feedback for the BrickPi3
    if [[ quiet_mode -eq 0 ]]; then
      echo "  _____            _                                ";
      echo " |  __ \          | |                               ";
      echo " | |  | | _____  _| |_ ___ _ __                     ";
      echo " | |  | |/ _ \ \/ / __/ _ \ '__|                    ";
      echo " | |__| |  __/>  <| ||  __/ |                       ";
      echo " |_____/ \___/_/\_\\\__\___|_|           _          ";
      echo " |_   _|         | |         | |      (_)           ";
      echo "   | |  _ __   __| |_   _ ___| |_ _ __ _  ___  ___  ";
      echo "   | | | '_ \ / _\ | | | / __| __| '__| |/ _ \/ __| ";
      echo "  _| |_| | | | (_| | |_| \__ \ |_| |  | |  __/\__ \ ";
      echo " |_____|_| |_|\__,_|\__,_|___/\__|_|  |_|\___||___/ ";
      echo "                                                    ";
      echo "                                                    ";
      echo "  ____       _      _    ____  _ _____ "
      echo " | __ ) _ __(_) ___| | _|  _ \(_)___ / "
      echo " |  _ \| '__| |/ __| |/ / |_) | | |_ \ "
      echo " | |_) | |  | | (__|   <|  __/| |___) |"
      echo " |____/|_|  |_|\___|_|\_\_|   |_|____/ "
      echo " "
    fi

    feedback "Welcome to BrickPi3 Installer."
  else
    echo "Welcome to BrickPi3 Installer."
  fi

  echo "Updating BrickPi3 with the following options:"
  ([[ $installdependencies = "true" ]] && echo "  --no-dependencies=false") || echo "  --no-dependencies=true"
  ([[ $updaterepo = "true" ]] && echo "  --no-update-aptget=false") || echo "  --no-update-aptget=true"
  ([[ $install_rfrtools = "true" ]] && echo "  --bypass-rfrtools=false") || echo "  --bypass-rfrtools=true"
  ([[ $install_pkg_rfrtools = "true" ]] && echo "  --bypass-python-rfrtools=false") || echo "  --bypass-python-rfrtools=true"
  ([[ $install_rfrtools_gui = "true" ]] && echo "  --bypass-gui-installation=false") || echo "  --bypass-gui-installation=true"
  echo "  --user-local=$userlocal"
  echo "  --env-local=$envlocal"
  echo "  --system-wide=$systemwide"

  # create rest of list of arguments for rfrtools call
  [[ $usepython3exec = "true" ]] && rfrtools_options+=("--use-python3-exe-too")
  [[ $updaterepo = "true" ]] && rfrtools_options+=("--update-aptget")
  [[ $installdependencies = "true" ]] && rfrtools_options+=("--install-deb-deps")
  [[ $install_pkg_rfrtools = "true" ]] && rfrtools_options+=("--install-python-package")
  [[ $install_rfrtools_gui = "true" ]] && rfrtools_options+=("--install-gui")

  echo "Options used for RFR_Tools script: \"${rfrtools_options[@]}\""
}

################################################
######### Cloning BrickPi3 & RFR_Tools #########
################################################

# called in <<install_rfrtools_repo>>
check_dependencies() {
  command -v git >/dev/null 2>&1 || { echo "This script requires \"git\" but it's not installed. Error occurred with RFR_Tools installation." >&2; exit 1; }
  command -v python >/dev/null 2>&1 || { echo "Executable \"python\" couldn't be found. Error occurred with RFR_Tools installation." >&2; exit 2; }
  command -v pip >/dev/null 2>&1 || { echo "Executable \"pip\" couldn't be found. Error occurred with RFR_Tools installation." >&2; exit 3; }
  if [[ $usepython3exec = "true" ]]; then
    command -v python3 >/dev/null 2>&1 || { echo "Executable \"python3\" couldn't be found. Error occurred with RFR_Tools installation." >&2; exit 4; }
    command -v pip3 >/dev/null 2>&1 || { echo "Executable \"pip3\" couldn't be found. Error occurred with RFR_Tools installation." >&2; exit 5; }
  fi
}

# called way down below
install_rfrtools_repo() {

  # if rfrtools is not bypassed then install it
  if [[ $install_rfrtools = "true" ]]; then
    echo "Installing RFR_Tools. This might take a moment.."
    bash $LIB_PATH/RFR_Tools/scripts/install_tools.sh ${rfrtools_options[@]} # > /dev/null
    ret_val=$?
    if [[ $ret_val -ne 0 ]]; then
      echo "RFR_Tools failed installing with exit code $ret_val. Exiting."
      exit 7
    fi
    echo "Done installing RFR_Tool"
  fi

  # check if all deb packages have been installed with RFR_Tools
  check_dependencies

  source $SCRIPT/functions_library.sh
}

################################################
######## Install Python Packages & Deps ########
################################################

install_python_packages() {
  cd $BRICKPI3_DIR/Software/Python
  install_python_setup
  cd
}

remove_python_packages() {
  # the 1st and only argument
  # takes the name of the package that needs to removed
  rm -f $PIHOME/.pypaths

  # get absolute path to python package
  # saves output to file because we want to have the syntax highlight working
  # does this for both root and the current user because packages can be either system-wide or local
  # later on the strings used with the python command can be put in just one string that gets used repeatedly
  python -c "import pkgutil; import os; \
              eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
              output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
  sudo python -c "import pkgutil; import os; \
              eggs_loader = pkgutil.find_loader('$1'); found = eggs_loader is not None; \
              output = os.path.dirname(os.path.realpath(eggs_loader.get_filename('$1'))) if found else ''; print(output);" >> $PIHOME/.pypaths
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

install_python_pkgs_and_dependencies() {
  # installing dependencies if required
  if [[ $installdependencies = "true" ]]; then
    sudo bash $BRICKPI3_DIR/Install/install.sh
  fi

  feedback "Removing \"$REPO_PACKAGE\" to make space for the new one"
  remove_python_packages "$REPO_PACKAGE"

  # installing the package itself
  install_python_packages

  # Install C++ drivers
  echo "Installing BrickPi3 C++ drivers"
  echo "Copying BrickPi3.h and BrickPi3.cpp to /usr/local/include"
  sudo rm -f /usr/local/include/BrickPi3.h
  sudo rm -f /usr/local/include/BrickPi3.cpp
  sudo cp $BRICKPI3_DIR/Software/C/BrickPi3.h /usr/local/include/BrickPi3.h
  sudo cp $BRICKPI3_DIR/Software/C/BrickPi3.cpp /usr/local/include/BrickPi3.cpp

  # install openocd
  echo "Installing OpenOCD for BrickPi3"
  bash $LIB_PATH/openocd/openocd_install.sh
}

################################################
######## Call all functions - main part ########
################################################

check_if_run_with_pi

parse_cmdline_arguments "$@"
install_rfrtools_repo

install_python_pkgs_and_dependencies

exit 0
