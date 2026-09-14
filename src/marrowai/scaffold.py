from __future__ import annotations

from pathlib import Path


class ProjectScaffold:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or ".")

    def create_backend_project(self, project_name: str) -> bool:
        root = self.base_dir / project_name
        root.mkdir(parents=True, exist_ok=True)

        (root / "README.md").write_text(
            f"# {project_name}\n\nA simple backend scaffold created by MarrowAI.\n",
            encoding="utf-8",
        )
        (root / "app.py").write_text(
            "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef home():\n    return {'status': 'ok'}\n",
            encoding="utf-8",
        )
        (root / "requirements.txt").write_text("fastapi\nuvicorn\n", encoding="utf-8")
        tests_dir = root / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "test_project.py").write_text(
            "from pathlib import Path\n\n\ndef test_project_files_exist():\n"
            "    assert Path('app.py').is_file()\n"
            "    assert Path('requirements.txt').is_file()\n",
            encoding="utf-8",
        )
        return True


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Create a backend project scaffold")
    parser.add_argument("project_name", help="Name of the project to scaffold")
    args = parser.parse_args()

    scaffold = ProjectScaffold()
    success = scaffold.create_backend_project(args.project_name)
    print(f"Scaffold created: {success}")


if __name__ == "__main__":
    main()
