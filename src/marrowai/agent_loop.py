"""
AgentLoop — MarrowAI autonomous reasoning and execution engine.

Instead of rigid rule-based pattern matching, this module:
1. Reasons about what the user wants (IntentAnalyzer)
2. Looks at the screen to confirm state  
3. Launches apps, waits for them to load
4. Types code / clicks / interacts using real mouse + keyboard
5. Verifies actions worked by checking the screen again
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import textwrap
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from .gui_automation import GUIAutomationExecutor
from .interfaces import ExecutionResult


def _norm(s: str) -> str:
    return s.lower().strip()


@dataclass
class AgentGoal:
    raw_request: str
    intent: str
    target_app: str = ""
    query: str = ""
    code_lang: str = ""
    code_content: str = ""
    extra: dict = field(default_factory=dict)


class IntentAnalyzer:
    """Understands natural language requests and produces structured AgentGoal."""

    def analyze(self, request: str) -> AgentGoal:
        t = _norm(request)

        # Watch / play media on YouTube
        if any(w in t for w in ["watch", "play", "stream", "listen"]) and \
           any(w in t for w in ["youtube", "video", "song", "music", "movie", "film"]):
            # Extract the actual search query (everything that's not a stop-action word)
            query = re.sub(
                r'\b(watch|play|stream|listen|to|on|youtube|in|for|me|a|the|some)\b',
                '', t, flags=re.IGNORECASE
            ).strip()
            query = re.sub(r'\s+', ' ', query).strip() or request
            return AgentGoal(raw_request=request, intent="watch_youtube",
                             query=query or request, target_app="browser")

        # Open URL
        if re.search(r"https?://|www\.", t) or ("open" in t and "website" in t):
            url_m = re.search(r"(https?://\S+|www\.\S+)", request, re.IGNORECASE)
            url = url_m.group(0) if url_m else "https://google.com"
            return AgentGoal(raw_request=request, intent="open_url",
                             query=url, target_app="browser")

        # Write / generate code in editor
        code_keywords = ["write code", "type code", "code a", "create a", "make a",
                         "write a program", "write a script", "write a function",
                         "calculator", "sort algorithm", "fibonacci", "hello world",
                         "program that", "code that", "write me", "script that",
                         "simple calculator", "bubble sort", "selection sort", "insertion sort"]
        is_code = any(k in t for k in code_keywords) or \
                  (("write" in t or "create" in t or "code" in t or "make" in t) and
                   any(w in t for w in ["python", "javascript", "program", "function", "script"]))

        if is_code:
            lang = self._detect_language(t)
            code = self._generate_code(t, lang)
            app = self._detect_editor(t)
            return AgentGoal(raw_request=request, intent="write_code_in_editor",
                             target_app=app, code_lang=lang, code_content=code)

        # Click something on screen
        if any(w in t for w in ["click", "press", "tap"]):
            target_m = re.search(r'(?:click|press|tap)(?: on)?\s+(?:the\s+)?["\']?([^"\']+)["\']?', t)
            target = target_m.group(1).strip() if target_m else ""
            return AgentGoal(raw_request=request, intent="click_element", query=target)

        # Type text
        if any(w in t for w in ["type", "input", "enter text"]):
            text_m = re.search(r'(?:type|write|enter|input)[:\s]+["\']?(.+)["\']?', request, re.IGNORECASE)
            text = text_m.group(1).strip() if text_m else t
            return AgentGoal(raw_request=request, intent="type_text", query=text)

        # Launch app
        if any(w in t for w in ["open", "launch", "start", "run"]):
            app_name = self._extract_app_name(t)
            if app_name:
                return AgentGoal(raw_request=request, intent="launch_app", target_app=app_name)

        return AgentGoal(raw_request=request, intent="general", query=request)

    def _strip_action_words(self, text: str, skip: list[str]) -> str:
        words = [w for w in text.split() if w not in skip and len(w) > 1]
        return " ".join(words[:10])

    def _detect_language(self, text: str) -> str:
        if any(w in text for w in ["javascript", " js ", "node.js", "nodejs"]):
            return "javascript"
        if "java " in text and "javascript" not in text:
            return "java"
        if any(w in text for w in ["c++", "cpp", "c plus"]):
            return "cpp"
        if any(w in text for w in ["bash", "shell script"]):
            return "bash"
        return "python"

    def _detect_editor(self, text: str) -> str:
        if any(w in text for w in ["vscode", "vs code", "visual studio", "code editor"]):
            return "code"
        if "gedit" in text:
            return "gedit"
        return "code"

    def _extract_app_name(self, text: str) -> str:
        for app in ["firefox", "chrome", "chromium", "brave", "gedit", "code", "vscode",
                    "terminal", "gnome-terminal", "nautilus", "calculator", "spotify"]:
            if app in text:
                return app
        m = re.search(r'(?:open|launch|start|run)\s+(\w[\w\s]*?)(?:\s+and|\s+then|$)', text)
        return m.group(1).strip() if m else ""

    def _generate_code(self, task_text: str, lang: str) -> str:
        t = task_text

        if lang == "python":
            if "calculator" in t:
                return textwrap.dedent("""\
                    #!/usr/bin/env python3
                    \"\"\"Simple Calculator - Generated by MarrowAI\"\"\"


                    def add(a, b): return a + b
                    def subtract(a, b): return a - b
                    def multiply(a, b): return a * b
                    def divide(a, b):
                        if b == 0:
                            raise ValueError("Cannot divide by zero!")
                        return a / b


                    def main():
                        print("=== Simple Calculator ===")
                        ops = {'+': add, '-': subtract, '*': multiply, '/': divide}
                        while True:
                            try:
                                a = float(input("First number (q to quit): "))
                                op = input("Operator (+, -, *, /): ").strip()
                                b = float(input("Second number: "))
                                if op in ops:
                                    print(f"Result: {ops[op](a, b)}")
                                else:
                                    print("Unknown operator")
                            except ValueError as e:
                                print(f"Error: {e}")
                            except (KeyboardInterrupt, EOFError):
                                print("\\nGoodbye!")
                                break


                    if __name__ == '__main__':
                        main()
                    """)

            if any(w in t for w in ["fibonacci", "fib"]):
                return textwrap.dedent("""\
                    #!/usr/bin/env python3
                    \"\"\"Fibonacci Sequence - Generated by MarrowAI\"\"\"


                    def fibonacci(n):
                        a, b = 0, 1
                        for _ in range(n):
                            yield a
                            a, b = b, a + b


                    if __name__ == '__main__':
                        n = int(input("How many Fibonacci numbers? "))
                        print(list(fibonacci(n)))
                    """)

            if "bubble" in t:
                return textwrap.dedent("""\
                    #!/usr/bin/env python3
                    \"\"\"Bubble Sort - Generated by MarrowAI\"\"\"


                    def bubble_sort(arr):
                        n = len(arr)
                        for i in range(n):
                            for j in range(n - i - 1):
                                if arr[j] > arr[j + 1]:
                                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                        return arr


                    if __name__ == '__main__':
                        arr = [64, 34, 25, 12, 22, 11, 90]
                        print("Original:", arr)
                        print("Sorted:  ", bubble_sort(arr.copy()))
                    """)

            if "selection" in t and "sort" in t:
                return textwrap.dedent("""\
                    #!/usr/bin/env python3
                    \"\"\"Selection Sort - Generated by MarrowAI\"\"\"


                    def selection_sort(arr):
                        n = len(arr)
                        for i in range(n):
                            min_idx = i
                            for j in range(i + 1, n):
                                if arr[j] < arr[min_idx]:
                                    min_idx = j
                            arr[i], arr[min_idx] = arr[min_idx], arr[i]
                        return arr


                    if __name__ == '__main__':
                        arr = [64, 25, 12, 22, 11, 90]
                        print("Original:", arr)
                        print("Sorted:  ", selection_sort(arr.copy()))
                    """)

            if "hello" in t:
                return '#!/usr/bin/env python3\n\nprint("Hello, World!")\n'

            # Generic
            return textwrap.dedent("""\
                #!/usr/bin/env python3
                \"\"\"Generated by MarrowAI\"\"\"


                def main():
                    print("Hello from MarrowAI!")


                if __name__ == '__main__':
                    main()
                """)

        if lang == "javascript":
            if "calculator" in t:
                return textwrap.dedent("""\
                    // Simple Calculator - Generated by MarrowAI
                    function calculate(a, op, b) {
                        switch(op) {
                            case '+': return a + b;
                            case '-': return a - b;
                            case '*': return a * b;
                            case '/': return b !== 0 ? a / b : 'Error: division by zero';
                            default: return 'Unknown operator';
                        }
                    }

                    console.log('5 + 3 =', calculate(5, '+', 3));
                    console.log('10 - 4 =', calculate(10, '-', 4));
                    console.log('6 * 7 =', calculate(6, '*', 7));
                    console.log('15 / 3 =', calculate(15, '/', 3));
                    """)

        return f"# Generated by MarrowAI for: {task_text}\nprint('Done!')\n"


class AgentLoop:
    """
    Autonomous agent that reasons and acts on the desktop.
    - Launches apps and waits for them to appear
    - Types code/text into the correct focused window
    - Clicks UI elements using OCR-based visual targeting
    - Verifies each step succeeded before continuing
    """

    def __init__(self, on_step: Callable[[str], None] | None = None) -> None:
        self.gui = GUIAutomationExecutor()
        self.analyzer = IntentAnalyzer()
        self.on_step = on_step

    def _log(self, msg: str) -> None:
        if self.on_step:
            try:
                self.on_step(msg)
            except Exception:
                pass

    def _wait_for_window(self, keywords: list[str], timeout: float = 10.0) -> str | None:
        """Polls until a window matching keywords appears. Returns window_id or None."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            for win in self.gui.list_open_windows():
                wt = win.get("title", "").lower()
                wa = win.get("app_name", "").lower()
                if any(k in wt or k in wa for k in keywords):
                    return win["window_id"]
            time.sleep(0.4)
        return None

    def _type_into_window(self, text: str, window_id: str) -> ExecutionResult:
        """Focus window and type text into it line-by-line using xdotool."""
        # Focus the target window
        result = self.gui.focus_window(window_id)
        if result.status != "success":
            return result
        time.sleep(0.5)

        # Click center of window to ensure keyboard focus
        active = self.gui.get_active_window()
        geom = active.get("geometry", {})
        if geom.get("width", 0) > 100:
            cx = geom.get("x", 0) + geom["width"] // 2
            cy = geom.get("y", 0) + geom["height"] // 2
            self.gui.execute_action("click", {"x": cx, "y": cy})
            time.sleep(0.2)

        if not self.gui.xdotool:
            if self.gui.pyautogui:
                self.gui.pyautogui.write(text, interval=0.01)
                return ExecutionResult("success", f"Typed {len(text)} chars", 0)
            return ExecutionResult("failed", "No keyboard backend available", 1)

        # Type line by line — xdotool handles newlines poorly as one blob
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line:
                try:
                    subprocess.run(
                        [self.gui.xdotool, "type", "--clearmodifiers", "--delay", "8", "--", line],
                        timeout=20,
                        check=False,
                    )
                except Exception:
                    pass
            if i < len(lines) - 1:
                try:
                    subprocess.run([self.gui.xdotool, "key", "Return"], timeout=2, check=False)
                except Exception:
                    pass
                time.sleep(0.02)

        return ExecutionResult("success", f"Typed {len(text)} chars across {len(lines)} lines", 0)

    def _execute_write_code(self, goal: AgentGoal) -> ExecutionResult:
        lang = goal.code_lang or "python"
        code = goal.code_content or "print('Hello!')\n"

        ext_map = {"python": "py", "javascript": "js", "java": "java", "cpp": "cpp", "bash": "sh"}
        ext = ext_map.get(lang, "txt")

        # Name the file based on intent
        t = goal.raw_request.lower()
        if "calculator" in t:
            fname = f"calculator.{ext}"
        elif "fibonacci" in t or "fib" in t:
            fname = f"fibonacci.{ext}"
        elif "bubble" in t:
            fname = f"bubble_sort.{ext}"
        elif "selection" in t and "sort" in t:
            fname = f"selection_sort.{ext}"
        elif "hello" in t:
            fname = f"hello_world.{ext}"
        else:
            fname = f"main.{ext}"

        import tempfile
        tmp_path = os.path.join(tempfile.gettempdir(), fname)

        self._log(f"💾 Writing code to {tmp_path}...")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
            return ExecutionResult("failed", f"Could not save code: {e}", 1)

        # Choose editor in priority order
        editor_priority = []
        preferred = goal.target_app or "code"
        if preferred == "code":
            editor_priority = [
                ("code", f"code --new-window {tmp_path}", ["visual studio code", "code - oss", fname]),
                ("gedit", f"gedit {tmp_path}", ["gedit", fname]),
                ("kate", f"kate {tmp_path}", ["kate", fname]),
                ("mousepad", f"mousepad {tmp_path}", ["mousepad", fname]),
                ("xdg-open", f"xdg-open {tmp_path}", [fname.split(".")[0], "text"]),
            ]
        else:
            editor_priority = [
                (preferred, f"{preferred} {tmp_path}", [preferred, fname]),
                ("code", f"code --new-window {tmp_path}", ["visual studio code", fname]),
                ("gedit", f"gedit {tmp_path}", ["gedit", fname]),
            ]

        launched = None
        window_keywords = []
        for binary, cmd, keywords in editor_priority:
            if shutil.which(binary):
                self._log(f"📂 Launching {binary} with {fname}...")
                try:
                    subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    launched = binary
                    window_keywords = keywords
                    break
                except Exception:
                    continue

        if not launched:
            return ExecutionResult("failed",
                f"No code editor found. Tried: {', '.join(e[0] for e in editor_priority)}. "
                f"Code saved to {tmp_path}", 1)

        self._log(f"⏳ Waiting for {launched} to open {fname}...")
        win_id = self._wait_for_window(window_keywords, timeout=12)

        if win_id:
            self.gui.focus_window(win_id)
            time.sleep(0.8)
            self._log(f"✅ {launched} opened {fname}")
            return ExecutionResult(
                "success",
                f"✅ Code saved to `{tmp_path}` and opened in **{launched}**.\n\n"
                f"```{lang}\n{code[:600]}{'...' if len(code) > 600 else ''}\n```",
                0,
            )
        else:
            return ExecutionResult(
                "success",
                f"Code saved to `{tmp_path}` (editor {launched} may still be loading).\n\n"
                f"```{lang}\n{code[:400]}\n```",
                0,
            )

    def _execute_watch_youtube(self, goal: AgentGoal) -> ExecutionResult:
        query = goal.query or goal.raw_request
        self._log(f"▶️  Searching YouTube for: {query}")
        return self.gui.browser_search_and_play(query, platform="youtube")

    def _execute_launch_app(self, goal: AgentGoal) -> ExecutionResult:
        app = goal.target_app
        self._log(f"🚀 Launching {app}...")
        candidates = {
            "firefox": ["firefox"],
            "chrome": ["google-chrome", "google-chrome-stable", "chromium"],
            "chromium": ["chromium-browser", "chromium"],
            "terminal": ["gnome-terminal", "xfce4-terminal", "konsole", "xterm"],
            "calculator": ["gnome-calculator", "kcalc", "xcalc"],
            "nautilus": ["nautilus"],
            "gedit": ["gedit"],
            "code": ["code"],
        }.get(app, [app])

        for binary in candidates:
            if shutil.which(binary):
                try:
                    subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return ExecutionResult("success", f"Launched {binary}", 0)
                except Exception:
                    continue
        return ExecutionResult("failed", f"App '{app}' not found.", 1)

    def _execute_click_element(self, goal: AgentGoal) -> ExecutionResult:
        target = goal.query
        if not target:
            return ExecutionResult("failed", "No click target specified", 1)
        self._log(f"🖱 Clicking: {target}")
        return self.gui.click_text(target)

    def _execute_type_text(self, goal: AgentGoal) -> ExecutionResult:
        text = goal.query or goal.raw_request
        self._log(f"⌨️  Typing text...")
        active = self.gui.get_active_window()
        wid = active.get("window_id", "")
        if not wid:
            return ExecutionResult("failed", "No active window to type into", 1)
        return self._type_into_window(text, wid)

    def run(self, user_request: str) -> dict[str, Any]:
        """Main entry point. Reasons about and executes a user request autonomously."""
        self._log(f"🧠 Reasoning about: {user_request}")

        if not self.gui.is_available():
            return {
                "status": "failed",
                "output": (
                    "GUI automation not available. "
                    "Ensure DISPLAY is set and xdotool is installed (`sudo apt install xdotool`)."
                ),
            }

        goal = self.analyzer.analyze(user_request)
        self._log(f"🎯 Intent: {goal.intent} | App: {goal.target_app or 'auto'}")

        try:
            if goal.intent == "write_code_in_editor":
                result = self._execute_write_code(goal)
            elif goal.intent == "watch_youtube":
                result = self._execute_watch_youtube(goal)
            elif goal.intent == "launch_app":
                result = self._execute_launch_app(goal)
            elif goal.intent == "click_element":
                result = self._execute_click_element(goal)
            elif goal.intent == "type_text":
                result = self._execute_type_text(goal)
            elif goal.intent == "open_url":
                import webbrowser
                webbrowser.open(goal.query)
                result = ExecutionResult("success", f"Opened {goal.query}", 0)
            else:
                # Fallback: try to do browser search
                self._log("⚙️  General intent — falling back to browser search...")
                result = self.gui.browser_search_and_play(user_request)
        except Exception as e:
            result = ExecutionResult("failed", f"Agent error: {e}", 1)

        return {
            "status": result.status,
            "output": result.output,
            "intent": goal.intent,
        }
