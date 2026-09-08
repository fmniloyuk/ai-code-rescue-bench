import pytest

from rescuebench.patches import changed_lines, normalize_patch, validate_patch_paths


def test_patch_normalization_strips_markdown_fence() -> None:
    patch = "```diff\n--- a/app.py\n+++ b/app.py\n@@ -1 +1 @@\n-old\n+new\n```"
    normalized = normalize_patch(patch)
    assert normalized.startswith("--- a/app.py")
    assert changed_lines(normalized) == 2


def test_patch_path_traversal_is_rejected() -> None:
    patch = "--- a/app.py\n+++ ../../escape.py\n@@ -1 +1 @@\n-a\n+b\n"
    with pytest.raises(ValueError, match="unsafe path"):
        validate_patch_paths(patch)
