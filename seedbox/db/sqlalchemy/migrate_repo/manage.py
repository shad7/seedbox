#!/usr/bin/env python
"""
Execution entry point for database migration
"""
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(debug='False')
