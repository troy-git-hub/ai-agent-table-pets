def execute(args, context):
    image_camera = context.get('image_camera')
    image_to_oss = context.get('image_to_oss')
    qwenLV = context.get('qwenLV')
    qwenLVcameraai = context.get('qwenLVcameraai')

    if not all([image_camera, image_to_oss, qwenLV, qwenLVcameraai]):
        return "摄像头工具依赖缺失"

    print("📷 AI调用了摄像头")
    img_path = image_camera()
    if img_path is None:
        return "摄像头无法打开或拍照失败"
    oss_url = image_to_oss(img_path)
    if oss_url is None:
        return "照片上传到OSS失败"
    qwen = qwenLV(oss_url, airenshe=qwenLVcameraai)
    print('摄像头分析:', qwen)
    return f"摄像头照片分析结果：{qwen}"