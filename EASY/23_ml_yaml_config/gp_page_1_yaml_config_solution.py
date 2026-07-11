"""Convert nested YAML configs to environment variables and back."""

import yaml


def yaml_to_env(config_file: str) -> str:
    """Convert a YAML config string to environment variables."""
    config = yaml.safe_load(config_file)
    env_lines = []

    def flatten(data: dict, parent_key: str = "") -> None:
        """Recursively collect leaf values from a nested dictionary."""
        for key, value in data.items():
            if parent_key:
                full_key = f"{parent_key}.{key}"
            else:
                full_key = str(key)

            if isinstance(value, dict):
                flatten(value, full_key)
            else:
                if value is None:
                    env_value = "null"
                else:
                    env_value = str(value)

                env_lines.append(f"{full_key}={env_value}")

    if isinstance(config, dict):
        flatten(config)

    return "\n".join(env_lines)


def env_to_yaml(env_list: str) -> str:
    """Convert environment variables to a nested YAML config string."""
    config = {}

    for raw_line in env_list.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        key, separator, raw_value = line.partition("=")

        if not separator:
            raise ValueError(
                "Each environment variable must contain '='."
            )

        path = key.strip().split(".")
        value_text = raw_value.strip()

        if value_text == "":
            value = ""
        else:
            value = yaml.safe_load(value_text)

        current_level = config

        for path_part in path[:-1]:
            current_level = current_level.setdefault(path_part, {})

        current_level[path[-1]] = value

    return yaml.safe_dump(
        config,
        sort_keys=False,
        allow_unicode=True,
    )
