#!/usr/bin/env python3
"""
DigitoolDB Server Executable (digid)
"""
import argparse
import os
import sys

from .server import DigitoolDBServer


def main():
    """
    Main entry point for the DigitoolDB server
    """
    parser = argparse.ArgumentParser(description='DigitoolDB Server')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--host', help='Server hostname')
    parser.add_argument('--port', type=int, help='Server port')
    parser.add_argument('--data-dir', help='Data directory')
    parser.add_argument('--log-level', choices=['debug', 'info', 'warning', 'error'], help='Log level')
    args = parser.parse_args()
    
    # Create server with config
    server = DigitoolDBServer(args.config)
    
    # Override config with command line arguments
    if args.host:
        server.config['host'] = args.host
    if args.port:
        server.config['port'] = args.port
    if args.data_dir:
        server.config['data_dir'] = args.data_dir
    if args.log_level:
        server.config['log_level'] = args.log_level
    
    # Start server
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
