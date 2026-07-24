"""Train the reference ALS model and build solution.zip."""

import argparse
import importlib.util
import shutil
import sys
import zipfile
from pathlib import Path


EXPECTED_IMPLICIT_VERSION = "0.6.1"
SOURCE_FILE = (
    "gp_page_6_implicit_als_reference_solution.py"
)


def load_solution_module(solution_path: Path):
    """Load prepared solution.py as a module."""
    spec = importlib.util.spec_from_file_location(
        "solution",
        solution_path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("Could not import solution.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules["solution"] = module
    spec.loader.exec_module(module)

    return module


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Train the reference implicit ALS model and "
            "create solution.zip."
        )
    )

    parser.add_argument(
        "data_path",
        type=Path,
        help="Path to the course CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("gp_page_6_submission"),
        help="Directory for the final submission files.",
    )

    return parser.parse_args()


def main() -> None:
    """Train the model and create the final ZIP archive."""
    arguments = parse_arguments()

    if not arguments.data_path.is_file():
        raise FileNotFoundError(
            f"Dataset was not found: {arguments.data_path}"
        )

    try:
        import implicit
    except ImportError as error:
        raise RuntimeError(
            "Install implicit==0.6.1 before training."
        ) from error

    if implicit.__version__ != EXPECTED_IMPLICIT_VERSION:
        raise RuntimeError(
            "Expected implicit==0.6.1, "
            f"but found {implicit.__version__}."
        )

    source_dir = Path(__file__).resolve().parent
    source_solution = source_dir / SOURCE_FILE

    if not source_solution.is_file():
        raise FileNotFoundError(
            f"Prepared solution was not found: {source_solution}"
        )

    arguments.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    solution_path = arguments.output_dir / "solution.py"
    model_path = arguments.output_dir / "model.pkl"
    archive_path = arguments.output_dir / "solution.zip"

    shutil.copy2(
        source_solution,
        solution_path,
    )

    solution_module = load_solution_module(
        solution_path
    )

    _, sparse_user_item = solution_module.process_data(
        str(arguments.data_path)
    )

    solution_module.fit_model(
        sparse_user_item=sparse_user_item,
        model_path=str(model_path),
        iterations=12,
        factors=100,
        regularization=0.2,
        alpha=100,
        random_state=42,
    )

    with zipfile.ZipFile(
        archive_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.write(
            solution_path,
            arcname="solution.py",
        )
        archive.write(
            model_path,
            arcname="model.pkl",
        )

    print(f"Created model: {model_path}")
    print(f"Created submission: {archive_path}")


if __name__ == "__main__":
    main()
