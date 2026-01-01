# Variable define
foundPyEnvironment := false
pyPath := python

# Color define
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
NC := \033[0m

# I won't tell you why not I use UPPER_CASE!!!

.PHONY: clean check_py_env check_py_ver pip_install_packages copy_to_tmp pyinstaller_build build make_all all

# Make all!
make_all: clean pip_install_packages pyinstaller_build
	@echo -e "$(GREEN)=== Finished all build! ===$(NC)"

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
	@echo -e "$(YELLOW)Checking Python environment...$(NC)"
	@if command -v python >/dev/null 2>&1; then \
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
	if [ "$$foundPyEnvironment" = "false" ]; then \
		echo -e "$(RED)Failed to find python environment!$(NC)"; \
		exit 1; \
	fi

# Check python version
check_py_ver: check_py_env
	@echo -e "$(GREEN)Checking python version...$(NC)"; \
	if ! $(pyPath) -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" 2>/dev/null; then \
		echo -e "$(RED)Error$(NC) Python version needed 3.12 and above!"; \
		exit 1; \
	else \
		echo -e "$(GREEN)Passed$(NC) Python Version check!"; \
	fi

pip_install_packages: check_py_ver
	@echo -e "$(RED)Attempting$(NC) to install PIP packages..."; \
	if ! $(pyPath) -m pip install -r requirements.txt; then \
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
	if ! pyinstaller main.py -i ./resources/icon.py --exclude PySide6-Addons --onedir -n Sinote -w; then \
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
	echo -e "  $(GREEN)requirements$(NC): Automatically check and install requirements"

sinote_help: help

# Requirements
requirements: pip_install_packages

# Quick build
build: pyinstaller_build
	@echo -e "$(GREEN)=== Build completed! ===$(NC)"