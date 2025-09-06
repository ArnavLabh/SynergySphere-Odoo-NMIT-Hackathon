#!/usr/bin/env python3
"""
Migration management script for SynergySphere
Usage:
  python migrate.py init     - Initialize migrations
  python migrate.py migrate  - Generate new migration
  python migrate.py upgrade  - Apply migrations
  python migrate.py downgrade - Rollback migrations
"""
import sys
from flask_migrate import init, migrate, upgrade, downgrade
from api import create_app

app = create_app()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    with app.app_context():
        if command == 'init':
            init()
            print("Migration repository initialized")
        elif command == 'migrate':
            message = sys.argv[2] if len(sys.argv) > 2 else None
            migrate(message=message)
            print("Migration generated")
        elif command == 'upgrade':
            upgrade()
            print("Database upgraded")
        elif command == 'downgrade':
            revision = sys.argv[2] if len(sys.argv) > 2 else '-1'
            downgrade(revision=revision)
            print("Database downgraded")
        else:
            print(f"Unknown command: {command}")
            print(__doc__)

if __name__ == '__main__':
    main()