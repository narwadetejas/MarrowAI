from __future__ import annotations

from marrowai.interactive import InteractiveSession


def test_interactive_session_can_be_constructed():
    session = InteractiveSession()
    assert session is not None
    assert session.interactive_mode is True
