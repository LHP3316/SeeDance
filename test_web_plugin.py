"""
测试 Web 插件功能

使用方法：
1. 测试打开登录浏览器
   python test_web_plugin.py --action login

2. 测试生成视频（需要先完成登录）
   python test_web_plugin.py --action generate

3. 测试完整流程
   python test_web_plugin.py --action full
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from jimeng_web_video_plugin import JimengWebVideoPlugin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_login():
    """测试打开登录浏览器"""
    logger.info("=" * 60)
    logger.info("测试：打开登录浏览器")
    logger.info("=" * 60)
    
    plugin = JimengWebVideoPlugin(headless=False)
    result = plugin.open_login_browser()
    
    logger.info(f"结果: {result}")
    
    if result.get("ok"):
        logger.info(f"✓ {result.get('message', '登录成功')}")
        return plugin
    else:
        logger.error(f"✗ 打开浏览器失败: {result.get('error')}")
        return None


def test_generate_video(plugin=None):
    """测试生成视频"""
    logger.info("=" * 60)
    logger.info("测试：生成视频")
    logger.info("=" * 60)
    
    # 测试图片路径（需要替换为实际路径）
    test_images = [
        "/mnt/d/Project/seedance/uploads/materials/52fbf9d3-a68b-439f-8d21-623cf15d88cc.png",
        "/mnt/d/Project/seedance/uploads/materials/6252f886-e810-40c6-bd30-1602b0d9541e.png"
    ]
    
    # 检查图片是否存在
    existing_images = [img for img in test_images if os.path.exists(img)]
    
    if not existing_images:
        logger.error("✗ 测试图片不存在，请修改 test_images 变量")
        logger.info(f"尝试查找的图片: {test_images}")
        return False
    
    logger.info(f"找到 {len(existing_images)} 张测试图片")
    
    # 创建插件实例（如果未提供）
    if not plugin:
        plugin = JimengWebVideoPlugin(headless=False)
    
    # 调用生成视频
    result = plugin.generate_video(
        image_paths=existing_images,
        prompt="@52fbf9d3-a68b-439f-8d21-623cf15d88cc.png是包子铺，@6252f886-e810-40c6-bd30-1602b0d9541e.png是狐奶奶，狐奶奶在包子铺内做包子呢",
        model="seedance-2.0",
        ratio="16:9",
        duration=5,
        generation_mode="omni_reference",
        timeout=900
    )
    
    logger.info(f"生成结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get("success"):
        logger.info("✓ 视频生成成功")
        logger.info(f"  - 视频 URL: {result.get('video_url')}")
        return True
    else:
        logger.error(f"✗ 视频生成失败: {result.get('error')}")
        return False


def test_full():
    """测试完整流程"""
    logger.info("=" * 60)
    logger.info("测试：完整流程")
    logger.info("=" * 60)
    
    # 1. 打开登录浏览器（自动检测登录状态）
    plugin = test_login()
    if not plugin:
        logger.error("✗ 登录失败，退出测试")
        return
    
    # 2. 自动生成视频（无需手动回车）
    logger.info("\n自动开始测试视频生成...")
    success = test_generate_video(plugin)
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✓ 完整流程测试通过")
        logger.info("=" * 60)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("✗ 完整流程测试失败")
        logger.error("=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试 Web 插件功能")
    parser.add_argument(
        "--action",
        choices=["login", "generate", "full"],
        default="full",
        help="测试动作（login: 打开登录浏览器, generate: 生成视频, full: 完整流程）"
    )
    
    args = parser.parse_args()
    
    if args.action == "login":
        test_login()
    elif args.action == "generate":
        test_generate_video()
    elif args.action == "full":
        test_full()


if __name__ == "__main__":
    main()
