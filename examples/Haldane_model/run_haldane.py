
import os
import sys

# Import the installed package
try:
    from wannier_tools import run
    print("Successfully imported wannier_tools.run")
except ImportError as e:
    print(f"Error importing wannier_tools: {e}")
    sys.exit(1)

# Execute the main logic
print("Running wannier_tools calculation...")
run()
print("Calculation finished.") 