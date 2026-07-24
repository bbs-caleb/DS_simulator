"""Train the ALS model and build the required solution.zip."""

import argparse
import importlib.util
import shutil
import sys
import zipfile
from pathlib import Path


EXPECTED_IMPLICIT_VERSION = "0.6.1"
SOLUTION_SOURCE_NAME = (
    "gp_page_6_implicit_als_recommender_system_solution.py"
)


def load_solution_module(solution_path: Path):
    """Import the prepared solution file as a Python module."""
    spec = importlib.util.spec_from_file_location(
        "solution",
        solution_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load solution.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules["solution"] = module
    spec.loader.exec_module(module)

    return module


def parse_arguments() -> argparse.Namespace:
    """Read command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Train implicit ALS on data_recsys.csv and create "
            "solution.zip with solution.py and model.pkl."
        )
    )
    parser.add_argument(
        "data_path",
        type=Path,
        help="Path to the CSV downloaded from the course page.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("gp_page_6_submission"),
        help="Directory for solution.py, model.pkl and solution.zip.",
    )
    parser.add_argument(
        "--factors",
        type=int,
        default=500,
        help="Number of ALS latent factors.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=12,
        help="Number of ALS iterations.",
    )
    parser.add_argument(
        "--regularization",
        type=float,
        default=0.2,
        help="ALS regularization.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=100.0,
        help="Confidence multiplier.",
    )

    return parser.parse_args()


def main() -> None:
    """Train the model and create the final submission archive."""
    arguments = parse_arguments()

    if not arguments.data_path.is_file():
        raise FileNotFoundError(
            f"Dataset was not found: {arguments.data_path}"
        )

    try:
        import implicit
    except ImportError as error:
        raise RuntimeError(
            "Install dependencies first, including implicit==0.6.1"
        ) from error

    if implicit.__version__ != EXPECTED_IMPLICIT_VERSION:
        raise RuntimeError(
            "The model must be trained with implicit==0.6.1. "
            f"Installed version: {implicit.__version__}"
        )

    source_dir = Path(__file__).resolve().parent
    prepared_solution = source_dir / SOLUTION_SOURCE_NAME

    if not prepared_solution.is_file():
        raise FileNotFoundError(
            f"Solution source was not found: {prepared_solution}"
        )

    arguments.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    submission_solution = (
        arguments.output_dir / "solution.py"
    )
    model_path = arguments.output_dir / "model.pkl"
    archive_path = arguments.output_dir / "solution.zip"

    shutil.copy2(
        prepared_solution,
        submission_solution,
    )

    solution_module = load_solution_module(
        submission_solution
    )

    _, sparse_user_item = solution_module.process_data(
        str(arguments.data_path)
    )

    solution_module.fit_model(
        sparse_user_item=sparse_user_item,
        model_path=str(model_path),
        iterations=arguments.iterations,
        factors=arguments.factors,
        regularization=arguments.regularization,
        alpha=arguments.alpha,
        random_state=42,
    )

    with zipfile.ZipFile(
        archive_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.write(
            submission_solution,
            arcname="solution.py",
        )
        archive.write(
            model_path,
            arcname="model.pkl",
        )

    print(f"Model: {model_path}")
    print(f"Submission archive: {archive_path}")


if __name__ == "__main__":
    main()
