export foundPyEnvironment=false
export way=0

echo "=================================="
echo "     Sinote Launcher 1.0.0"
echo "       Win12Home (C) 2025"
echo "=================================="
echo
echo "Finding Python..."

if command -v python >/dev/null 2>&1; then
  echo "Successfully to find python!"
  foundPyEnvironment=true
  way=0
elif [ -f /bin/python ]; then
  echo "Successfully to find python!"
  foundPyEnvironment=true
  way=1
fi

if [ $foundPyEnvironment ]; then
  echo "Checking Python Version..."
  if [ $way = 0 ]; then
    if ! python -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" 2>/dev/null; then
      echo "Error: Python is lower than 3.12!"
      echo "Sinote needed 3.12 or higher!"
      exit 1
    fi
  elif [ $way = 1 ]; then
    if ! /bin/python -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" 2>/dev/null; then
      echo "Error: Python is lower than 3.12"
      echo "Sinote needed 3.12 or higher!"
      exit 1
    fi
  fi
  cd ..
  python -m pip install -r requirements.txt
  python main.py -ow -nc
else
  echo "Error: Cannot find python environment!"
  echo "This script only can find \"python\" executable, cannot find \"python3\" executable!"
  echo "Use \"python3 main.py\" if you've got Python."
  exit 2
fi

