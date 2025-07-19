#!/usr/bin/env python3
"""
WannierTools Command Line Interface

This script provides a command-line interface to WannierTools.
It can be used as a standalone executable.
"""

import argparse
import sys
import os
from . import run, create_sample_input

def main():
    """Main command line interface"""
    parser = argparse.ArgumentParser(
        description="WannierTools Python Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wt-py                    # Run with default wt.in
  wt-py -i input.in        # Run with custom input file
  wt-py -o output.log      # Redirect output to file
  wt-py --sample           # Create sample input file
  wt-py -i input.in -o out.log  # Custom input and output
        """
    )
    
    parser.add_argument(
        '-i', '--input', 
        default='wt.in',
        help='Input file path (default: wt.in)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: print to console)'
    )
    
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Create a sample wt.in input file and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='WannierTools Python Interface 2.7.1'
    )
    
    args = parser.parse_args()
    
    if args.sample:
        create_sample_input()
        print("Sample input file created. You can now edit wt.in and run the calculation.")
        return 0
    
    # Run WannierTools
    return run(input_file=args.input, output_file=args.output)

if __name__ == '__main__':
    sys.exit(main()) 