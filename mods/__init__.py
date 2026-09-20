"""
Mods 模块加载器
自动扫描 mods/ 下的所有工具模块，加载 tool.json 和 handler.py
"""

import os
import json
import importlib.util


MODS_DIR = os.path.dirname(os.path.abspath(__file__))

_loaded_tools = {}
_tool_definitions = []


def _discover_modules():
    modules = []
    for entry in sorted(os.listdir(MODS_DIR)):
        mod_path = os.path.join(MODS_DIR, entry)
        if not os.path.isdir(mod_path):
            continue
        if entry.startswith('_') or entry.startswith('.'):
            continue
        json_path = os.path.join(mod_path, 'tool.json')
        handler_path = os.path.join(mod_path, 'handler.py')
        if os.path.exists(json_path) and os.path.exists(handler_path):
            modules.append((entry, json_path, handler_path))
    return modules


def load_tools(context=None):
    """
    加载所有工具模块
    context: 共享依赖字典，传递给每个 handler.execute()
    返回: (tool_definitions_list, dispatch_dict)
    """
    global _loaded_tools, _tool_definitions
    _loaded_tools = {}
    _tool_definitions = []

    modules = _discover_modules()
    for name, json_path, handler_path in modules:
        with open(json_path, 'r', encoding='utf-8') as f:
            tool_def = json.load(f)

        _tool_definitions.append({
            "type": "function",
            "function": tool_def
        })

        spec = importlib.util.spec_from_file_location(
            f"mods.{name}.handler", handler_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, 'execute'):
            print(f"[WARN] {name}/handler.py 缺少 execute() 函数，跳过")
            continue

        def make_executor(mod, tool_name):
            def executor(args):
                try:
                    return mod.execute(args, context or {})
                except Exception as e:
                    return f"工具执行失败 [{tool_name}]: {str(e)}"
            return executor

        _loaded_tools[name] = make_executor(module, name)
        print(f"[MOD] 加载工具: {name}")

    return list(_tool_definitions), dict(_loaded_tools)


def get_tools_definition():
    """获取当前所有工具的 Function Calling 定义列表"""
    return list(_tool_definitions)


def execute_tool(tool_name, args):
    """执行指定工具"""
    if tool_name not in _loaded_tools:
        return f"未知工具: {tool_name}"
    return _loaded_tools[tool_name](args)