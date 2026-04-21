#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
即梦AI爬虫主程序 - Playwright版本
功能：抖音扫码登录、图片生成自动化、定时任务
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from browser_manager import BrowserManager
from image_generator import ImageGenerator


class JimengBot:
    """即梦AI机器人"""
    
    def __init__(self, config: dict):
        self.config = config
        
    async def run_task(self):
        """执行单次任务"""
        print(f"\n{'='*60}")
        print(f"任务开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        browser = BrowserManager(
            cookie_file=self.config.get('cookie_file', 'cookies.json'),
            headless=self.config.get('headless', False)
        )
        
        try:
            # 1. 初始化浏览器
            print("正在初始化浏览器...")
            await browser.setup()
            
            # 2. 尝试加载Cookie进行二次登录
            force_login = self.config.get('force_login', False)
            if not force_login and await browser.load_cookies():
                print("尝试使用保存的Cookie登录...")
                if await browser.check_login_status():
                    print("✓ Cookie登录成功！")
                else:
                    print("⚠ Cookie已过期，需要重新登录")
                    force_login = True
            else:
                force_login = True
            
            # 3. 如果需要登录
            if force_login:
                print("\n需要进行登录...")
                if not await browser.login_with_douyin():
                    print("✗ 登录失败，任务终止")
                    return False
                print("✓ 登录成功！")
            
            # 4. 初始化图片生成器
            generator = ImageGenerator(browser.page)
            
            # 5. 执行图片生成
            if self.config.get('prompt'):
                print(f"\n准备生成图片，提示词: {self.config['prompt']}")
                success = await generator.generate_image(
                    prompt=self.config['prompt'],
                    image_paths=self.config.get('images'),
                    model_name=self.config.get('model', ''),
                    ratio=self.config.get('ratio', '1:1'),
                    save_dir=self.config.get('output', 'generated_images')
                )
                
                if success:
                    print("\n✓ 图片生成成功！")
                    return True
                else:
                    print("\n✗ 图片生成失败")
                    return False
            else:
                print("\n⚠ 未提供提示词，仅完成登录。")
                return True
            
        except Exception as e:
            print(f"\n✗ 任务执行出错: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 关闭浏览器
            await browser.close()
            print(f"\n任务结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="即梦AI图片生成爬虫 - Playwright版本")
    
    # 任务参数
    parser.add_argument("--prompt", type=str, help="图片生成提示词")
    parser.add_argument("--images", type=str, nargs="+", help="参考图片路径（支持多张）")
    parser.add_argument("--model", type=str, default="", help="图片模型名称")
    parser.add_argument("--ratio", type=str, default="1:1", help="图片比例，如 1:1, 16:9, 9:16")
    parser.add_argument("--output", type=str, default="generated_images", help="生成图片保存目录")
    
    # 浏览器参数
    parser.add_argument("--headless", action="store_true", help="无头模式运行浏览器")
    parser.add_argument("--force-login", action="store_true", help="强制重新登录")
    parser.add_argument("--cookie-file", type=str, default="cookies.json", help="Cookie文件路径")
    
    # 定时任务参数
    parser.add_argument("--schedule", type=str, choices=['cron', 'interval'], help="定时任务类型")
    parser.add_argument("--cron", type=str, help="Cron表达式，如 '0 */2 * * *' (每2小时)")
    parser.add_argument("--interval", type=int, help="间隔时间（分钟）")
    parser.add_argument("--config", type=str, help="从配置文件加载（YAML格式）")
    
    return parser.parse_args()


def load_config_from_file(config_file: str) -> dict:
    """从YAML配置文件加载配置"""
    import yaml
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


async def main():
    """主函数"""
    args = parse_args()
    
    # 加载配置
    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = {
            'prompt': args.prompt,
            'images': args.images,
            'model': args.model,
            'ratio': args.ratio,
            'output': args.output,
            'headless': args.headless,
            'force_login': args.force_login,
            'cookie_file': args.cookie_file,
        }
    
    # 创建机器人实例
    bot = JimengBot(config)
    
    # 判断是否使用定时任务
    if args.schedule == 'cron' and args.cron:
        # Cron定时任务
        print(f"\n启动Cron定时任务: {args.cron}")
        scheduler = AsyncIOScheduler()
        scheduler.add_job(bot.run_task, CronTrigger.from_crontab(args.cron), id='jimeng_cron')
        scheduler.start()
        
        print("定时任务已启动，按Ctrl+C停止\n")
        try:
            # 立即执行一次
            await bot.run_task()
            
            # 保持运行
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            print("\n定时任务已停止")
            
    elif args.schedule == 'interval' and args.interval:
        # 间隔定时任务
        print(f"\n启动间隔定时任务: 每{args.interval}分钟执行一次")
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            bot.run_task, 
            IntervalTrigger(minutes=args.interval), 
            id='jimeng_interval'
        )
        scheduler.start()
        
        print("定时任务已启动，按Ctrl+C停止\n")
        try:
            # 立即执行一次
            await bot.run_task()
            
            # 保持运行
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            print("\n定时任务已停止")
            
    else:
        # 单次执行
        await bot.run_task()


if __name__ == "__main__":
    asyncio.run(main())
