"""Search nutrition data with fuzzy and semantic matching."""

import csv
from difflib import get_close_matches
from typing import Any, Dict, List, Optional

from sentence_transformers import SentenceTransformer, util


class IngredientNutritionSearch:
    """Search nutrition information for recognized ingredients."""

    def __init__(
        self,
        dataset_path: str,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        """Load the dataset and initialize the embedding model."""
        self.dataset_path = dataset_path
        self.data = self._load_data()
        self._ingredients = list(self.data.keys())

        try:
            self.encoder = SentenceTransformer(model_name)
        except Exception as error:
            raise RuntimeError(
                f"Failed to load `{model_name}`. Error: {error}"
            ) from error

        self._embeddings = self.encoder.encode(
            self._ingredients,
            convert_to_tensor=True,
        )

    def _load_data(self) -> Dict[str, Dict[str, float]]:
        """Load nutrition values from the CSV file into a dictionary."""
        try:
            with open(
                self.dataset_path,
                mode="r",
                encoding="utf-8",
            ) as file:
                csv_reader = csv.DictReader(file)

                return {
                    row["name"].lower(): {
                        "calories": float(row["calories"]),
                        "fats": float(
                            row["total_fat"].replace("g", "").strip()
                        ),
                        "proteins": float(
                            row["protein"].replace("g", "").strip()
                        ),
                        "carbohydrates": float(
                            row["carbohydrate"].replace("g", "").strip()
                        ),
                    }
                    for row in csv_reader
                }

        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Error: The file '{self.dataset_path}' was not found."
            ) from error
        except KeyError as error:
            raise KeyError(
                f"Error: Missing expected column in CSV file: {error}"
            ) from error
        except Exception as error:
            raise RuntimeError(
                f"An error occurred while reading the file: {error}"
            ) from error

    def _fuzzy_search(
        self,
        ingredient_name: str,
        threshold: float = 0.6,
    ) -> Optional[str]:
        """Find the closest ingredient by character similarity."""
        matches = get_close_matches(
            ingredient_name.lower(),
            self._ingredients,
            n=1,
            cutoff=threshold,
        )

        return matches[0] if matches else None

    def _semantic_search(
        self,
        ingredient_name: str,
        threshold: float = 0.6,
    ) -> Optional[str]:
        """Find the closest ingredient by semantic similarity."""
        ingredient_embedding = self.encoder.encode(
            ingredient_name.lower(),
            convert_to_tensor=True,
        )

        cosine_scores = util.pytorch_cos_sim(
            ingredient_embedding,
            self._embeddings,
        )

        max_index = int(cosine_scores.argmax().item())
        max_score = cosine_scores[0][max_index].item()

        if max_score >= threshold:
            return self._ingredients[max_index]

        return None

    def search(
        self,
        img_ingredients: Dict[str, float],
        search_type: str = "fuzzy",
    ) -> List[Dict[str, Any]]:
        """Search ingredients and scale nutrition values by weight."""
        if search_type not in {"fuzzy", "semantic"}:
            raise ValueError(
                "`search_type` must be either 'fuzzy' or 'semantic'"
            )

        results = []

        for ingredient_name, ingredient_weight in img_ingredients.items():
            if ingredient_weight <= 0:
                continue

            if search_type == "fuzzy":
                match = self._fuzzy_search(ingredient_name)
            else:
                match = self._semantic_search(ingredient_name)

            if match is None:
                results.append({ingredient_name: {}})
                continue

            ingredient_data = self.data[match]
            result_data = {
                "match": match,
                "weight": ingredient_weight,
            }

            result_data.update(
                {
                    key: round(
                        value * (ingredient_weight / 100.0),
                        0,
                    )
                    for key, value in ingredient_data.items()
                }
            )

            results.append({ingredient_name: result_data})

        return results
