import sys
from agent.tools.bash.bash import Bash

def test_bare_dotenv_key_does_not_break_native_shell(tmp_path, monkeypatch):
    home = tmp_path / "home"
    folder = home / ".maliang"
    folder.mkdir(parents=True)
    (folder / ".env").write_text("MALIANG_BARE_KEY\nMALIANG_EMPTY_KEY=\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("MALIANG_BARE_KEY", "inherited")
    monkeypatch.setenv("MALIANG_EMPTY_KEY", "old")
    command = f"{sys.executable} -c \"import os; print(os.environ['MALIANG_BARE_KEY'] + ':' + os.environ['MALIANG_EMPTY_KEY'])\""
    result = Bash({"cwd": str(tmp_path)}).execute({"command": command})
    assert result.status == "success", result.result
    assert "inherited:" in result.result["output"]
