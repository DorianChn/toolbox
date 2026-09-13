"""Tests for git hook install/uninstall idempotency."""
import pytest

from devcapsule.hook import HOOK_SCRIPT, install, is_installed, uninstall


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A fake git repo dir: <tmp>/.git/hooks."""
    gd = tmp_path / ".git"
    (gd / "hooks").mkdir(parents=True)

    def _git_dir(cwd):
        return gd

    monkeypatch.setattr("devcapsule.hook.git_dir", _git_dir)
    return gd


def test_install_creates_hook(repo):
    hook = install(".")
    assert hook.exists()
    assert "devcapsule" in hook.read_text(encoding="utf-8")


def test_install_is_idempotent(repo):
    install(".")
    # append extra content as if the user added their own hook later
    hook = repo / "hooks" / "post-commit"
    extra = "\n# user's own hook\necho hello\n"
    with hook.open("a", encoding="utf-8") as f:
        f.write(extra)

    install(".")  # second install must NOT clobber the user's additions
    text = hook.read_text(encoding="utf-8")
    assert text.count("devcapsule") == 1, "duplicate devcapsule snippet"
    assert "echo hello" in text, "user's own hook was clobbered"


def test_install_preserves_existing_non_devcapsule_hook(repo):
    hook = repo / "hooks" / "post-commit"
    hook.write_text("#!/bin/sh\necho pre-existing\n", encoding="utf-8")

    install(".")
    text = hook.read_text(encoding="utf-8")
    assert "echo pre-existing" in text, "existing hook was lost"
    assert "devcapsule" in text, "devcapsule snippet not appended"


def test_uninstall_removes_only_devcapsule(repo):
    install(".")
    assert is_installed(".")
    assert uninstall(".")
    assert not is_installed(".")
    # uninstall on an already-clean repo is a no-op (False)
    assert not uninstall(".")
