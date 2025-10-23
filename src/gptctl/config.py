from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
from typing import Any, Optional
from rich.console import Console
import typer


@dataclass
class ViewFormat:
    noisy_fields: list[str] = field(default_factory=list)
    max_examples: int = 5
    collapse_threshold: int = 2000
    clear_noisy_fields: bool = False


@dataclass()
class AppConfig:
    format: ViewFormat = field(default_factory=ViewFormat)
    input_file: str = "./data/conversations.json"
    output_file: str = "./data/messages_summary.json"
    output_dir: str = "./data/conversations"
    combined_file: str = "all_conversations.md"
    prefix_with_date: bool = True
    truncate_len: int = 120
    console: Optional[Console] = field(
        compare=False, repr=False, default=None
    )  # class defaults: eq=True, frozen=False

    @classmethod
    def load(cls, config_path: str = "", verbosity: int = 0):
        dflt = cls()
        try:
            if config_path and Path(config_path).exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                    format = ViewFormat(
                        noisy_fields=file_config.get("format", {}).get("noisy_fields"),
                        max_examples=file_config.get("format", {}).get("max_examples"),
                        collapse_threshold=file_config.get("format", {}).get(
                            "collapse_threshold"
                        ),
                    )
                    u_config = AppConfig(
                        format=format,
                        input_file=file_config.get("input_file", cls.input_file),
                        output_file=file_config.get("output_file", cls.output_file),
                        output_dir=file_config.get("output_dir", cls.output_dir),
                        combined_file=file_config.get(
                            "combined_file", cls.combined_file
                        ),
                        prefix_with_date=file_config.get(
                            "prefix_with_date", cls.prefix_with_date
                        ),
                        truncate_len=file_config.get("truncate_len", cls.truncate_len),
                    )
                    if verbosity >= 2:
                        print(f"[verbose] Loaded config from {config_path}")
                    return u_config
            return dflt
        except FileNotFoundError as e:
            if cls.console:
                cls.console.print(e)
            else:
                print(e)

    @classmethod
    def resolve(
        cls,
        config_path: str = "",
        file_config: Any = {},
        args: dict[str, Any] = {},
        verbosity: int = 0,
        console: Any = None,
    ):
        # 1) Start with defaults
        # eff_cfg = AppConfig()

        if Path(config_path).exists():
            eff_cfg = AppConfig.load(config_path=config_path, verbosity=verbosity)
            if eff_cfg and isinstance(eff_cfg, AppConfig):
                eff_cfg = AppConfig(**eff_cfg.to_dict())
        elif file_config and isinstance(file_config, AppConfig):
            eff_cfg = AppConfig(**file_config.to_dict())
        else:
            eff_cfg = AppConfig()

        if eff_cfg is not None:
            eff_cfg = eff_cfg.to_dict()
        else:
            eff_cfg = {}

        # 2) Load from config.json if provided
        if hasattr(args, "config") and Path(args["config"]).exists():
            with open(args["config"], "r", encoding="utf-8") as f:
                eff_cfg = json.load(f)

        # 3) Apply CLI overrides
        if args.get("input") and eff_cfg.get("input_file") is not None:
            eff_cfg["input_file"] = args["input"]
        if args.get("output") and eff_cfg.get("output_file") is not None:
            eff_cfg["output_file"] = args["output"]
        if args.get("output_dir") and eff_cfg.get("output_dir") is not None:
            eff_cfg["output_dir"] = args["output_dir"]

        if args.get("combined_file") and eff_cfg.get("combined_file") is not None:
            eff_cfg["combined_file"] = args["combined_file"]
        if args.get("prefix_with_date") and eff_cfg.get("prefix_with_date") is not None:
            eff_cfg["prefix_with_date"] = args["prefix_with_date"]
        if args.get("truncate_len") and eff_cfg.get("truncate_len") is not None:
            eff_cfg["truncate_len"] = args["truncate_len"]

        # Format options
        if (
            args.get("max_examples") is not None
            and isinstance(eff_cfg, dict)
            and "max_examples" in eff_cfg["format"]
        ):
            eff_cfg["format"]["max_examples"] = args["max_examples"]
        if (
            args.get("collapse_threshold") is not None
            and isinstance(eff_cfg, dict)
            and "collapse_threshold" in eff_cfg["format"]
        ):
            eff_cfg["format"]["collapse_threshold"] = args["collapse_threshold"]
        if (
            args.get("max_examples") is not None
            and isinstance(eff_cfg, dict)
            and "max_examples" in eff_cfg["format"]
        ):
            eff_cfg["format"]["max_examples"] = args["max_examples"]
        if (
            args.get("collapse_threshold") is not None
            and isinstance(eff_cfg, dict)
            and "collapse_threshold" in eff_cfg["format"]
        ):
            eff_cfg["format"]["collapse_threshold"] = args["collapse_threshold"]
        if (
            args.get("max_examples") is not None
            and isinstance(eff_cfg, dict)
            and "max_examples" in eff_cfg["format"]
        ):
            eff_cfg["format"]["max_examples"] = args["max_examples"]
        if (
            args.get("collapse_threshold") is not None
            and isinstance(eff_cfg, dict)
            and "collapse_threshold" in eff_cfg["format"]
        ):
            eff_cfg["format"]["collapse_threshold"] = args["collapse_threshold"]
        if (
            args.get("max_examples") is not None
            and isinstance(eff_cfg, dict)
            and "max_examples" in eff_cfg["format"]
        ):
            eff_cfg["format"]["max_examples"] = args["max_examples"]
        if (
            args.get("collapse_threshold") is not None
            and isinstance(eff_cfg, dict)
            and "collapse_threshold" in eff_cfg["format"]
        ):
            eff_cfg["format"]["collapse_threshold"] = args["collapse_threshold"]
            # Handle noisy fields
        if (
            args.get("clear_noisy_fields") is not None
            and isinstance(eff_cfg, dict)
            and "noisy_fields" in eff_cfg["format"]
        ):
            eff_cfg["format"]["noisy_fields"] = []
        if (
            args.get("noisy_fields") is not None
            and isinstance(eff_cfg, dict)
            and "noisy_fields" in eff_cfg["format"]
        ):
            eff_cfg["format"]["noisy_fields"] = args["noisy_fields"]

        if verbosity >= 2:
            if console:
                console.print(f"Effective config: {eff_cfg}")
            else:
                print(f"Effective config: {eff_cfg}")

        return AppConfig(**eff_cfg)

    @classmethod
    def get_config(cls, config_path: str = "", args: dict = {}, verbosity: int = 0):
        file_config = cls.load(config_path=config_path, verbosity=verbosity)
        cfg = cls.resolve(
            config_path=config_path,
            file_config=file_config,
            args=args,
            verbosity=verbosity,
        )
        return cfg

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        my_dict = asdict(self)
        del my_dict["console"]
        return my_dict


def default_config_path(app_name: str = "gptctl") -> Path:
    app_dir = typer.get_app_dir(app_name)
    default_config_path = Path(app_dir) / "config.json"
    return default_config_path


def check_config_exists(config: Path, console: Optional[Console] = None) -> bool:
    if not config.exists():
        if console:
            console.print(
                f"The config file [bold magenta]{config}[bold magenta] doesn't exist."
            )
        else:
            print(f"The config file {config} doesn't exist. Using internal defaults")
        return False
    return True
