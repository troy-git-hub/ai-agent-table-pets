def execute(args, context):
    if isinstance(args, dict):
        command = args.get("command", "")
    else:
        command = str(args) if args else ""
    deepseekcodeaihandle = context.get('deepseekcodeaihandle')

    if not deepseekcodeaihandle:
        return "电脑操作工具依赖缺失"
    if not command:
        return "未提供操作指令"

    print(f"💻 AI要执行电脑操作: {command}")
    return deepseekcodeaihandle(command)