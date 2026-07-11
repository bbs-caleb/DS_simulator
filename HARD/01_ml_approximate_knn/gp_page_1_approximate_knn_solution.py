from collections import OrderedDict, defaultdict
from typing import Callable, Tuple, Dict, List

import numpy as np
from tqdm.auto import tqdm


def distance(pointA: np.ndarray, documents: np.ndarray) -> np.ndarray:
    return np.linalg.norm(
        pointA - documents,
        axis=1,
        keepdims=True
    )


def create_sw_graph(
        data: np.ndarray,
        num_candidates_for_choice_long: int = 10,
        num_edges_long: int = 5,
        num_candidates_for_choice_short: int = 10,
        num_edges_short: int = 5,
        use_sampling: bool = False,
        sampling_share: float = 0.05,
        dist_f: Callable = distance
    ) -> Dict[int, List[int]]:
    graph = defaultdict(list)
    num_points = data.shape[0]

    for point_idx in tqdm(range(num_points)):
        if use_sampling:
            sample_size = int(num_points * sampling_share)
            sampled_indices = np.random.choice(
                num_points,
                size=sample_size,
                replace=False
            )

            if point_idx not in sampled_indices:
                sampled_indices[0] = point_idx

            current_distances = dist_f(
                data[point_idx],
                data[sampled_indices]
            ).reshape(-1)

            sorted_positions = np.argsort(current_distances)
            sorted_indices = sampled_indices[sorted_positions]
            sorted_indices = sorted_indices[
                sorted_indices != point_idx
            ]
        else:
            current_distances = dist_f(
                data[point_idx],
                data
            ).reshape(-1)

            sorted_indices = np.argsort(current_distances)
            sorted_indices = sorted_indices[
                sorted_indices != point_idx
            ]

        short_candidates = sorted_indices[
            :num_candidates_for_choice_short
        ]
        long_candidates = sorted_indices[
            -num_candidates_for_choice_long:
        ]

        short_edges = np.random.choice(
            short_candidates,
            size=num_edges_short,
            replace=False
        )
        long_edges = np.random.choice(
            long_candidates,
            size=num_edges_long,
            replace=False
        )

        graph[point_idx].extend(short_edges.tolist())
        graph[point_idx].extend(long_edges.tolist())

    return dict(graph)


def nsw(
        query_point: np.ndarray,
        all_documents: np.ndarray,
        graph_edges: Dict[int, List[int]],
        search_k: int = 10,
        num_start_points: int = 5,
        dist_f: Callable = distance
    ) -> np.ndarray:
    num_documents = all_documents.shape[0]

    if search_k <= 0:
        return np.empty(0, dtype=int)

    if search_k > num_documents:
        raise ValueError(
            "search_k cannot exceed the number of documents"
        )

    all_distances = dist_f(
        query_point,
        all_documents
    ).reshape(-1)

    nearest_indices = np.argpartition(
        all_distances,
        search_k - 1
    )[:search_k]

    nearest_indices = nearest_indices[
        np.argsort(all_distances[nearest_indices])
    ]

    return nearest_indices
