#!/bin/bash
WHITE='\033[0;37m' 
BLUE='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BWhite='\033[1;37m' 
NC='\033[0m'
set -e

packages_ubuntu=(
	gcc
	libbsd-dev
	libncurses-dev
	valgrind
	python3-pip
	git
)

#which clang

packages_arch=(
	gcc
	clang
	postgresql
	libbsd
	ncurses
	valgrind
	python-pip
	git
)

## check if 

check=1

cd

if [ -z "${INSTALL_DIR}" ]; then
    INSTALL_DIR=$HOME
    read -p "Install Directory (default: $INSTALL_DIR): " user_input
    INSTALL_DIR=${user_input:-$INSTALL_DIR}
fi
export INSTALL_DIR

if [ "$(uname)" != "Darwin" ]; then
	case $(lsb_release -is) in
		"Ubuntu")
			for package in "${packages_ubuntu[@]}"; do
				  if dpkg -s "$package" &> /dev/null; then
				        echo "✔️ $package is installed."
				    else
				        echo "❌ $package is not installed."
					check=0
				    fi
			done
			;;
		"Debian")
			for package in "${packages_ubuntu[@]}"; do
				  if dpkg -s "$package" &> /dev/null; then
				        echo "✔️ $package is installed."
				    else
				        echo "❌ $package is not installed."
					check=0
				    fi
			done
			;;
  		"Arch")
			for package in "${packages_arch[@]}"; do
				if pacman -Qi "$package" &> /dev/null; then
			        	echo "✔️ $package is installed."
				else
			        	echo "❌ $package is not installed."
					check=0
			    	fi
			done
			;;
   		"EndeavourOS")
			for package in "${packages_arch[@]}"; do
				if pacman -Qi "$package" &> /dev/null; then
			        	echo "✔️ $package is installed."
				else
			        	echo "❌ $package is not installed."
					check=0
			    	fi
			done
			;;
		*)
			check=0
			;;
	esac
else
	check=0
fi

if [ "$check" -eq 1 ]; then
	rm -rf $INSTALL_DIR/.tmp_francinette
	echo -e "${BLUE} [Francinette] The francinette-image is useless!${RESET}"
	read -p "Do you want to force the installation of francinette-image? (y/N) " answer
	if [ -z "$answer" ]; then
	    answer="n"
	fi
	if [[ "$answer" =~ ^[Yy]$ ]]; then
		check=0;
	else
		if [ -d "$INSTALL_DIR/francinette" ]; then
			rm -rf "$INSTALL_DIR/francinette"
			echo -e "${BLUE}Francinette${GREEN} Uninstalled OK${NC}"
		fi
		echo -e "${GREEN} Installation of the original francinette in progress${NC}"
		git clone --recursive https://github.com/xicodomingues/francinette.git "$INSTALL_DIR/francinette"
		python3 -m venv "$INSTALL_DIR/francinette/venv"
		if "$INSTALL_DIR/francinette/venv/bin/pip" install -r "$INSTALL_DIR/francinette/requirements.txt" \
			&& "$INSTALL_DIR/francinette/venv/bin/pip" install norminette; then
			find "$INSTALL_DIR/francinette" -name '*.py' -print0 \
				| xargs -0 sed -i 's/from pipes import quote/from shlex import quote/g'
			RC_FILE="$HOME/.zshrc"
			touch "$RC_FILE"
			sed -i '/^alias paco=/d; /^alias francinette=/d' "$RC_FILE"
			printf "alias paco='%s/francinette/tester.sh'\n" "$INSTALL_DIR" >> "$RC_FILE"
			printf "alias francinette='%s/francinette/tester.sh'\n" "$INSTALL_DIR" >> "$RC_FILE"
		else
			echo -e "${RED}Francinette installation failed${NC}"
			check=0
		fi
	fi
fi
if [ "$check" -eq 0 ]; then
	rm -rf $INSTALL_DIR/.tmp_francinette
	echo -e "${GREEN} Installation of the francinette-image in progress${RESET}"
	
	if ls -l $INSTALL_DIR | grep "francinette" &> /dev/null; then
		rm -rf $INSTALL_DIR/francinette
		echo -e "${BLUE}Francinette${GREEB} Uninstalled OK${RESET}"
 	fi

	if ! ls -l $INSTALL_DIR | grep "francinette-image" &> /dev/null; then
		git clone https://github.com/WaRtr0/francinette-image.git $INSTALL_DIR/francinette-image
	fi
	
	chmod +x $INSTALL_DIR/francinette-image/run.sh
	
	if ! ls -l $INSTALL_DIR/francinette-image | grep "francinette.tar" &> /dev/null; then
		if hostname | grep "42lyon.fr" &> /dev/null; then
	 		if ls -l /sgoinfre/goinfre/Perso/mmorot/share | grep "francinette.tar" &> /dev/null; then
	   			echo -e "${BLUE}[Francinette] ${WHITE}Copy of francinette.tar (${BWhite}/sgoinfre/goinfre/Perso/mmorot/share${WHITE})${RESET}"
	      			cp /sgoinfre/goinfre/Perso/mmorot/share/francinette.tar $INSTALL_DIR/francinette-image/
		 		echo -e "${BLUE}[Francinette] ${WHITE}Copy ${GREEN}OK${RESET}"
	   		fi
	 	fi
	fi
	
	if ! ls -l $INSTALL_DIR/francinette-image | grep "francinette.tar" &> /dev/null; then
		docker build -t francinette-image $INSTALL_DIR/francinette-image
		docker image save francinette-image > $INSTALL_DIR/francinette-image/francinette.tar
	fi
	if ls -l $INSTALL_DIR/francinette-image | grep "francinette.tar" &> /dev/null; then
		docker load < $INSTALL_DIR/francinette-image/francinette.tar
	fi
	
	source $INSTALL_DIR/francinette-image/utils/install_zshrc.sh
fi

echo -e "${BLUE}[Francinette] ${GREEN}Installation completed!\n${WHITE}Use the ${BWhite}paco${WHITE} or ${BWhite}francinette${WHITE} commands in your project folder.${RESET}"

exec "$SHELL"

