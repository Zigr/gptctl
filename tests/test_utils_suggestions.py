import pytest

from gptctl.utils.suggestions import extract_text  # adjust to your actual module path


@pytest.mark.parametrize("msg,expected", [
    # 1️⃣ Normal assistant message
    ({
        "message": {
            "author": {"role": "assistant"},
            "content": {"parts": ["Hello there!"]}
        }
    }, "Hello there!"),

    # 2️⃣ User message
    ({
        "message": {
            "author": {"role": "user"},
            "content": {"parts": ["Can you summarize this?"]}
        }
    }, "Can you summarize this?"),

    # 3️⃣ Message with multiple parts
    ({
        "message": {
            "author": {"role": "assistant"},
            "content": {"parts": ["Step 1", "Step 2", "Final answer"]}
        }
    }, "Final answer"),

    # 4️⃣ Missing content
    ({
        "message": {
            "author": {"role": "assistant"}
        }
    }, ""),

    # 5️⃣ Null content
    ({
        "message": {
            "author": {"role": "assistant"},
            "content": None
        }
    }, ""),

    # 6️⃣ Flat message object (no nested "message")
    ({
        "author": {"role": "assistant"},
        "content": {"parts": ["Direct format works too"]}
    }, "Direct format works too"),

    # 7️⃣ Parts are not a list
    ({
        "message": {
            "author": {"role": "assistant"},
            "content": {"parts": "not-a-list"}
        }
    }, "not-a-list"),

    # 8️⃣ Parts list is empty
    ({
        "message": {
            "author": {"role": "assistant"},
            "content": {"parts": []}
        }
    }, ""),

    # 9️⃣ Parts contain non-string types
    ({
        "message": {
            "author": {"role": "assistant"},
            "content": {"parts": [123, {"foo": "bar"}, "final"]}
        }
    }, "final"),

])
def test_extract_text(msg, expected):
    assert extract_text(msg) == expected