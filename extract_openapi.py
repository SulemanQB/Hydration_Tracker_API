import argparse
import json
import sys
from pathlib import Path

import yaml
from uvicorn.importer import import_from_string

def main():
    parser = argparse.ArgumentParser(prog="extract_openapi.py")
    parser.add_argument("app", nargs="?", help='App import string, for example "app:api"', default="app:api")
    parser.add_argument("--app-dir", help="Directory containing the app", default=None)
    parser.add_argument("--out", help="Output file ending in .json or .yaml", default="openapi.yaml")
    parser.add_argument("--out-dir", help="Output directory for the doc file", default="./docs/")
    args = parser.parse_args()

    if args.app_dir is not None:
        print(f"adding {args.app_dir} to sys.path")
        sys.path.insert(0, args.app_dir)

    print(f"importing app from {args.app}")
    app = import_from_string(args.app)
    openapi = app.openapi()
    version = openapi.get("openapi", "unknown version")
    
    output_path = Path(args.out_dir) / args.out
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"writing openapi spec v{version}")
    with output_path.open("w", encoding="utf-8") as f:
        if args.out.endswith(".json"):
            json.dump(openapi, f, indent=2)
        else:
            yaml.safe_dump(openapi, f, sort_keys=False)

    print(f"spec written to {output_path}")


if __name__ == "__main__":
    main()