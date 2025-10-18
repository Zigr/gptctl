from gptctl.config import AppConfig
import sys


def test_load_config():
    dflt_cfg = AppConfig().load()
    cfg = AppConfig()
    # existing path
    config_path = "./tests/data/config.json"
    file_cfg = cfg.load(config_path=config_path, verbosity=2)
    assert isinstance(file_cfg, AppConfig)
    assert dflt_cfg != file_cfg
    # not existing path
    config_path = "./not_existing/config.json"
    file_cfg = cfg.load(config_path=config_path, verbosity=2)
    assert dflt_cfg is not None
    assert file_cfg is not None
    assert dflt_cfg == file_cfg


def test_resolve_config():
    config_path = "./data/config.json"
    args = {
        "input": "./tests/data/conversations.json",
        "output": "./tests/data/messages_summary.json",
        "output_dir": "./tests/data/conversations",
        "combined_file": "my_conversations.md",
        "prefix_with_date": False,
        "truncate_len": 1200,
        "clear_noisy_fields": True,
    }
    verbosity = 1
    cfg = AppConfig()
    file_config = cfg.load(config_path="./data/config.json", verbosity=2)
    cfg = cfg.resolve(
        config_path=config_path,
        file_config=file_config,
        args=args,
        verbosity=verbosity,
    )
    assert isinstance(cfg, AppConfig)


def test_get_config():
    config_path = "./tests/data/config.json"
    args = {
        "input": "./tests/data/conversations.json",
        "output": "./tests/data/messages_summary.json",
        "output_dir": "./tests/data/conversations",
        "combined_file": "my_conversations.md",
        "prefix_with_date": False,
        "truncate_len": 1200,
        "clear_noisy_fields": True,
    }
    verbosity = 1
    cfg = AppConfig()
    eff_cfg = cfg.get_config(config_path=config_path, args=args, verbosity=verbosity)
    assert isinstance(eff_cfg, AppConfig)


def test_default_to_dict():
    dflt_cfg = AppConfig().load()
    assert dflt_cfg is not None
    assert isinstance(dflt_cfg, AppConfig)
    assert len(dflt_cfg.to_dict()) > 0


def test_to_dict():
    config_path = "./tests/data/config.json"
    args = {
        "input": "./tests/data/conversations.json",
        "output": "./tests/data/messages_summary.json",
        "output_dir": "./tests/data/conversations",
        "combined_file": "my_conversations.md",
        "prefix_with_date": False,
        "truncate_len": 1200,
        "clear_noisy_fields": True,
    }
    verbosity = 1
    cfg = AppConfig()
    eff_cfg = cfg.get_config(config_path=config_path, args=args, verbosity=verbosity)
    assert eff_cfg is not None
    assert isinstance(eff_cfg, AppConfig)
    assert isinstance(eff_cfg.to_dict(), dict)
