"""
即梦AI 纯API调用示例
无需浏览器，直接通过API生成图片
"""

import os
import sys
import logging
from jimeng_api_client import JimengAPIClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """主函数"""
    
    # 从环境变量或配置文件获取sessionid
    sessionid = os.getenv("JIMENG_SESSIONID", "")
    
    if not sessionid:
        print("=" * 50)
        print("请设置环境变量 JIMENG_SESSIONID")
        print("或者在代码中直接填写sessionid")
        print("=" * 50)
        print("\n如何获取sessionid：")
        print("1. 在浏览器中登录即梦AI (https://jimeng.jianying.com)")
        print("2. 按F12打开开发者工具")
        print("3. 找到 Application/存储 -> Cookies")
        print("4. 复制 sessionid 的值")
        print("=" * 50)
        
        # 也可以直接在这里填写
        sessionid = input("\n请输入你的sessionid: ").strip()
    
    if not sessionid:
        print("未提供sessionid，程序退出")
        return
    
    # 创建API客户端
    client = JimengAPIClient(sessionid)
    
    print("\n" + "=" * 50)
    print("即梦AI 图片生成 - 纯API模式")
    print("=" * 50)
    
    # 示例1: 文生图
    print("\n【示例1】文生图")
    result = client.generate_text_to_image(
        prompt="一只可爱的猫咪，坐在窗台上，阳光照射进来，温馨的氛围",
        model="3.0",  # 可选: 2.0, 2.1, 3.0, 4.0
        ratio="1:1"   # 可选: 1:1, 16:9, 9:16, 4:3, 3:4
    )
    
    if result["success"]:
        print(f"\n✅ 生成成功！")
        print(f"history_id: {result['history_id']}")
        print(f"图片数量: {len(result['urls'])}")
        print(f"图片URL:")
        for i, url in enumerate(result['urls'], 1):
            print(f"  {i}. {url}")
        
        # 下载图片
        print("\n开始下载图片...")
        saved_paths = client.download_images(result['urls'], save_dir="output")
        print(f"已保存 {len(saved_paths)} 张图片到 output 目录")
        for path in saved_paths:
            print(f"  - {path}")
    else:
        print(f"\n❌ 生成失败: {result.get('error', '未知错误')}")
    
    # 示例2: 图生图（可选）
    print("\n" + "=" * 50)
    print("【示例2】图生图（如果有参考图片）")
    
    # 检查是否有测试图片
    test_images = []
    if os.path.exists("test_image.png"):
        test_images.append("test_image.png")
    
    if test_images:
        print(f"\n使用参考图片: {test_images}")
        result = client.generate_image_to_image(
            image_paths=test_images,
            prompt="转换成水彩画风格，色彩柔和，笔触细腻",
            model="4.0",
            ratio="1:1"
        )
        
        if result["success"]:
            print(f"\n✅ 图生图成功！")
            print(f"图片数量: {len(result['urls'])}")
            
            # 下载图片
            saved_paths = client.download_images(result['urls'], save_dir="output_i2i")
            print(f"已保存 {len(saved_paths)} 张图片到 output_i2i 目录")
        else:
            print(f"\n❌ 图生图失败: {result.get('error', '未知错误')}")
    else:
        print("未找到test_image.png，跳过图生图示例")
        print("如需测试图生图，请将参考图片命名为test_image.png放在当前目录")
    
    print("\n" + "=" * 50)
    print("程序执行完毕！")
    print("=" * 50)


if __name__ == "__main__":
    main()
