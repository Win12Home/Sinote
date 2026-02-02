# Variable define
foundPyEnvironment := false
pyPath := python

ifneq ($(PYTHON_PATH),)
	foundPyEnvironment := true
	pyPath := $(PYTHON_PATH)
endif


# Color define
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
NC := \033[0m

# Compile/Make Argument define
ifeq ($(NUITKA_ARGS),)
	NUITKA_ARGS = --mode=standalone --follow-imports --enable-plugins=pyside6 --lto=yes --assume-yes-for-download --include-qt-plugins=platforms,xcbglintegrations --show-progress
endif

ifeq ($(PYINSTALLER_ARGS),)
	PYINSTALLER_ARGS = -i ./resources/icon.py --exclude PySide6-Addons --onedir -w
endif

# I won't tell you why not I use UPPER_CASE!!!

.PHONY: clean check_py_env check_py_ver pip_install_packages copy_to_tmp pyinstaller_build build make_all all clean_source make_with_cli nuitka nuitka_build nuitka_build_original

# Make all!
make_all: clean pip_install_packages pyinstaller_build clean_source
	@echo -e "$(GREEN)=== Finished all build! ===$(NC)"; \
	echo -e "Binary file is in $(YELLOW)./make-temporary/$(NC)";

all: make_all;

# Clean makes!
clean:
	@echo -e "Cleaning before makes..."
	@-rm -rf ./make-temporary 2>/dev/null || \
		echo -e "$(RED)Failed$(NC) to clean! Just first $(RED)make$(NC)?\nOf course this script $(RED)Continue run!$(NC)";
	@-rm -rf ./temporary 2>/dev/null || \
		echo -e "$(RED)Failed$(NC) to clean! Just first $(RED)make$(NC)?\nOf course this script $(RED)Continue run!$(NC)"
	@echo -e "$(GREEN)Clean OK$(NC)"

# Check Python Environment, look ./shell/run.sh!
check_py_env:
	@echo -e "$(YELLOW)Checking Python environment...$(NC)"; \
	if [ "$(foundPyEnvironment)" = "false" ]; then \
		if command -v python >/dev/null 2>&1; then \
			echo -e "$(GREEN)Successfully to find python! (in PATH)$(NC)"; \
			foundPyEnvironment=true; \
			pyPath=python; \
		elif [ -f /bin/python ]; then \
			echo -e "$(GREEN)Successfully to find python! (in /bin)$(NC)"; \
			foundPyEnvironment=true; \
			pyPath=/bin/python; \
		else \
			foundPyEnvironment=false; \
		fi; \
	else \
		echo -e "$(GREEN)Note: $(NC) PYTHON_PATH has been defined, Makefile will use this value to run python."; \
	fi
	@if [ "$$foundPyEnvironment" = "false" ]; then \
		echo -e "$(RED)Failed to find python environment!$(NC)"; \
		exit 1; \
	fi; \
	echo -e "$(GREEN)OK$(NC) Python is in $(pyPath)";

# Check python version
check_py_ver: check_py_env
	@echo -e "$(GREEN)Checking python version...$(NC)"; \
		if ! "$(pyPath)" -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" 2>/dev/null; then \
		echo -e "$(RED)Error$(NC) Python version needed 3.12 and above!"; \
		exit 1; \
	else \
		echo -e "$(GREEN)Passed$(NC) Python Version check!"; \
	fi

clean_source:
	@echo -e "$(RED)Attempting$(NC) to clean sources..."; \
	rm -rf ./temporary; \
	echo -e "$(GREEN)Successfully$(NC) to clean sources!";

pip_install_packages: check_py_ver
	@echo -e "$(RED)Attempting$(NC) to install PIP packages..."; \
	if ! $(pyPath) -m ensurepip; then \
	    echo -e "$(RED)Error:$(NC) Unknown error when installing PIP!"; \
	fi; \
	if ! $(pyPath) -m pip install -r requirements.txt pyinstaller nuitka; then \
		echo -e "$(RED)Error:$(NC) Unknown error when installing PIP packages!"; \
		exit 1; \
	else \
		echo -e "$(GREEN)Successfully$(NC) to install PIP packages!"; \
	fi

copy_to_tmp:
	@mkdir -p ./temporary
	@echo -e "$(RED)Attempting$(NC) to copy source file to a temporary directory (./temporary)"
	@cp -rf ./core/ ./temporary/core/
	@cp -rf ./ui/ ./temporary/ui/
	@cp -rf ./utils/ ./temporary/utils/
	@cp -rf ./resources/ ./temporary/resources/
	@cp main.py ./temporary/ 2>/dev/null || echo -e "$(YELLOW)Note: main.py not found, skipping$(NC)"
	@echo -e "$(GREEN)Successfully$(NC) to copy!"

pyinstaller_build: copy_to_tmp
	@echo -e "$(RED)Attempting$(NC) to build..."; \
	cd ./temporary/ && \
	if ! pyinstaller main.py -n Sinote $(PYINSTALLER_ARGS); then \
		echo -e "$(RED)Failed to build!$(NC)"; \
		exit 1; \
	fi; \
	echo -e "$(GREEN)Successfully$(NC) to build Sinote!"; \
	echo -e "$(RED)Attempting$(NC) to add needed resources..."; \
	mkdir -p ./../make-temporary/resources; \
	cp -rf ./dist/Sinote/* ./../make-temporary/; \
	cp -rf ./resources/* ./../make-temporary/resources/; \
	echo -e "$(GREEN)Finished$(NC) build task!"

help:
	@-echo -e "$(GREEN)Help$(NC) of $(YELLOW)Sinote Build$(NC)"; \
	echo -e "  $(GREEN)clean$(NC): Clean before makes (./temporary & ./make-temporary)"; \
	echo -e "  $(GREEN)build$(NC): Quick build (No pip install and check python suitable)"; \
	echo -e "  $(GREEN)all$(NC): All build"; \
	echo -e "  $(GREEN)make_with_cli$(NC): All build with CLI"; \
	echo -e "  $(GREEN)requirements$(NC): Automatically check and install requirements"; \
	echo -e "  $(GREEN)version$(NC): Version of Makefile and tested in what version"; \
	echo -e "  $(GREEN)nuitka_build$(NC): Quick build with nuitka"; \
	echo -e "  $(GREEN)nuitka$(NC): All build with nuitka"; \
	echo ""; \
	echo -e "$(GREEN)Help$(NC) of $(YELLOW)Environment Variable$(NC) of $(YELLOW)Sinote Build$(NC)"; \
	echo -e "  $(GREEN)PYTHON_PATH: $(NC)The Python Path that customizable (e.g. /bin/python3.12, /bin/python3.13)"; \
	echo -e "  $(GREEN)NUITKA_ARGS: $(NC)The Nuitka Compiling Arguments (e.g. --debug)"; \
	echo -e "  $(GREEN)PYINSTALLER_ARGS: $(NC)The Pyinstaller Making Arguments (e.g. --onefile)"; \
	echo -e "$(RED)Note: $(NC)These environment variable is not necessary."

sinote_help: help

# Requirements
requirements: pip_install_packages

# Quick build
build: pyinstaller_build clean_source	
	@echo -e "$(GREEN)=== Build completed! ===$(NC)"; \
	echo -e "Binary file is in $(YELLOW)./make-temporary/$(NC)";

# Make With CLI
make_with_cli: pip_install_packages pyinstaller_build
	@echo -e "$(GREEN)Starting$(NC) to make CLI..."; \
	mkdir ./temporary/; \
	cp ./SinoteCLI.py ./temporary/SinoteCLI.py; \
	cd ./temporary/; \
	rm -rf ./dist; \
	pyinstaller -F -c -i ./../resources/images/plugins.png SinoteCLI.py; \
	echo -e "$(GREEN)Made$(NC) CLI Successfully!"; \
	echo -e "$(GREEN)Copying$(NC) dist..."; \
	cd ..; \
	cp ./temporary/dist/* ./make-temporary/; \
	echo -e "$(GREEN)Finished copy$(NC) task!"; \
	echo -e "$(GREEN)Cleaning$(NC) environment..."; \
	rm -rf ./temporary; \
	echo -e "$(GREEN)=== Build completed! ===$(NC)"; \
	echo -e "Binary file is in $(YELLOW)./make-temporary/$(NC)";

# Version Information of Makefile
version:
	@echo -e "$(GREEN)Sinote$(NC) Maker 1.0.1"; \
	echo -e "$(GREEN)Test and passed$(NC) in Sinote version 0.06.26014"; \
	echo ""; \
	echo -e "By $(YELLOW)Win12Home$(NC), GitHub Site: $(GREEN)https://github.com/Win12Home/Sinote$(NC)"; \
	echo "Open-Source in MIT License.";

# Nuitka Build (No Clean Source)
nuitka_build_original: copy_to_tmp
	@echo -e "$(RED)Attempting$(NC) to build..."; \
	cd ./temporary/; \
	if ! $(pyPath) -m nuitka $(NUITKA_ARGS) main.py; then \
		echo -e "$(RED)Failed$(NC) to build! Use \"build\" option instead!"; \
		exit 1; \
	fi; \
	echo -e "$(GREEN)Successfully$(NC) to build Sinote!"; \
	echo -e "$(RED)Attempting$(NC) to add needed resources..."; \
	mkdir -p ./../make-temporary/resources; \
	cp -rf ./main.dist/* ./../make-temporary/; \
	cp -rf ./resources/* ./../make-temporary/resources/; \
	mv ./../make-temporary/main.bin ./../make-temporary/Sinote; \
	echo -e "$(GREEN)Finished$(NC) build task!"

nuitka_build: nuitka_build_original clean_source
	@echo -e "$(GREEN)=== Build completed! ===$(NC)"; \
	echo -e "Binary file is in $(YELLOW)./make-temporary/$(NC)";

nuitka: clean pip_install_packages nuitka_build_original clean_source
	@echo -e "$(GREEN)=== Finished all build! ===$(NC)"; \
	echo -e "Binary file is in $(YELLOW)./make-temporary/$(NC)";

make_with_cli_nuitka: clean pip_install_packages nuitka_build_original clean_source
	@echo -e "$(GREEN)Starting$(NC) to make CLI..."; \
	mkdir ./temporary/; \
	cp ./SinoteCLI.py ./temporary/SinoteCLI.py; \
	cd ./temporary/; \
	rm -rf ./dist; \
	pyinstaller -F -c -i ./../resources/images/plugins.png SinoteCLI.py; \
	echo -e "$(GREEN)Made$(NC) CLI Successfully!"; \
	echo -e "$(GREEN)Copying$(NC) dist..."; \
	cd ..; \
	cp ./temporary/dist/* ./make-temporary/; \
	echo -e "$(GREEN)Finished copy$(NC) task!"; \
	echo -e "$(GREEN)Cleaning$(NC) environment..."; \
	rm -rf ./temporary; \
	echo -e "$(GREEN)=== Build completed! ===$(NC)"; \
	echo -e "Binary file is in $(YELLOW)./make-temporary/$(NC)";