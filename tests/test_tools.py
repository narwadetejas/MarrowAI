from __future__ import annotations

from marrowai.tools import (
    EchoTool,
    ListFilesTool,
    ReadFileTool,
    RunTestsTool,
    ScaffoldBackendTool,
    ToolRegistry,
    WriteFileTool,
)


def test_tool_registry_has_defaults():
    registry = ToolRegistry()
    assert registry.has("ls")
    assert registry.has("list_files")
    assert registry.has("scaffold_backend")
    assert registry.has("run_tests")
    assert registry.has("echo")
    assert registry.has("read_file")
    assert registry.has("write_file")


def test_list_files_tool(tmp_path):
    (tmp_path / "hello.txt").write_text("world", encoding="utf-8")
    tool = ListFilesTool()
    result = tool.execute({"path": str(tmp_path)})
    assert result.status == "success"
    assert "hello.txt" in result.output

    # Nonexistent directory test
    bad = tool.execute({"path": str(tmp_path / "does_not_exist")})
    assert bad.status == "failed"


def test_echo_tool():
    tool = EchoTool()
    result = tool.execute({"text": "testing 1 2 3"})
    assert result.status == "success"
    assert result.output == "testing 1 2 3"


def test_read_and_write_file_tools(tmp_path):
    write_tool = WriteFileTool()
    read_tool = ReadFileTool()

    target = tmp_path / "subdir" / "note.txt"
    w_res = write_tool.execute({"path": str(target), "content": "MarrowAI offline intelligence"})
    assert w_res.status == "success"
    assert target.exists()

    r_res = read_tool.execute({"path": str(target)})
    assert r_res.status == "success"
    assert r_res.output == "MarrowAI offline intelligence"


def test_scaffold_backend_tool(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tool = ScaffoldBackendTool()
    result = tool.execute({"project_name": "test_service"})
    assert result.status == "success"
    assert (tmp_path / "test_service" / "app.py").exists()

    # Invalid project name test
    bad_result = tool.execute({"project_name": "../unsafe"})
    assert bad_result.status == "blocked"


def test_tool_registry_blocks_unknown():
    registry = ToolRegistry()
    res = registry.execute("non_existent_tool", {})
    assert res.status == "blocked"
    assert "not allowlisted" in res.output
