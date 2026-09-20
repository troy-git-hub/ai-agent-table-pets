def execute(args, context):
    image_screen = context.get('image_screen')
    image_to_oss = context.get('image_to_oss')
    qwenLV = context.get('qwenLV')
    qwenLVscreenai = context.get('qwenLVscreenai')

    if not all([image_screen, image_to_oss, qwenLV, qwenLVscreenai]):
        return "屏幕工具依赖缺失"

    print("🖥️ AI调用了屏幕截图")
    img_path = image_screen()
    if img_path is None:
        return "屏幕截图失败"
    oss_url = image_to_oss(img_path)
    if oss_url is None:
        return "截图上传到OSS失败"
    qwen = qwenLV(oss_url, airenshe=qwenLVscreenai)
    print('屏幕分析:', qwen)
    return f"屏幕截图分析结果：{qwen}"