import time
import json
import os
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional


class BrowserManager:
    def __init__(self, cookie_file: str = "cookies.json", headless: bool = False):
        self.cookie_file = cookie_file
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def setup(self):
        """初始化浏览器和上下文"""
        self.playwright = await async_playwright().start()
        
        # 启动浏览器
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',  # 启动时最大化窗口
                '--window-size=1920,1080',  # 设置窗口大小
            ]
        )
        
        # 创建浏览器上下文 - 使用更大的视口，不限制高度
        self.context = await self.browser.new_context(
            viewport=None,  # 不设置固定视口，允许页面自然滚动
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 添加反检测脚本
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await self.context.new_page()
        
        print("✓ 浏览器初始化完成")
        
    async def load_cookies(self) -> bool:
        """加载保存的Cookie"""
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                
                # 先访问网站，然后添加cookie
                await self.page.goto("https://jimeng.jianying.com", wait_until='domcontentloaded')
                await self.page.wait_for_timeout(2000)
                
                # 添加cookie
                await self.context.add_cookies(cookies)
                print(f"✓ 已从 {self.cookie_file} 加载Cookie")
                return True
            except Exception as e:
                print(f"✗ 加载Cookie失败: {e}")
                return False
        return False
    
    async def save_cookies(self):
        """保存Cookie到文件"""
        try:
            cookies = await self.context.cookies()
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"✓ Cookie已保存到 {self.cookie_file}")
            return True
        except Exception as e:
            print(f"✗ 保存Cookie失败: {e}")
            return False
    
    async def login_with_douyin(self) -> bool:
        """使用抖音扫码登录"""
        try:
            print("正在访问即梦AI网站...")
            # 使用 domcontentloaded 避免长时间等待
            await self.page.goto("https://jimeng.jianying.com/ai-tool/home", wait_until='domcontentloaded', timeout=30000)
            print(f"✓ 页面加载完成，当前URL: {self.page.url}")
            await self.page.wait_for_timeout(3000)
            
            # 保存页面截图以便调试
            await self.page.screenshot(path='login_page.png')
            print("✓ 已保存页面截图: login_page.png")
            
            # 检查是否已经登录
            content = await self.page.content()
            if "登录" not in content or "扫码" not in content:
                print("✓ 检测到已登录状态")
                await self.save_cookies()
                return True
            
            # 尝试点击登录按钮
            print("\n查找登录按钮...")
            try:
                # 尝试多种选择器
                selectors = [
                    "button:has-text('登录')",
                    "a:has-text('登录')",
                    "div:has-text('登录')",
                    "[class*='login']",
                    "text=登录"
                ]
                
                login_btn = None
                for selector in selectors:
                    try:
                        login_btn = await self.page.wait_for_selector(selector, timeout=5000)
                        if login_btn:
                            print(f"✓ 找到登录按钮，使用选择器: {selector}")
                            break
                    except:
                        continue
                
                if login_btn:
                    await login_btn.click()
                    print("✓ 已点击登录按钮")
                    await self.page.wait_for_timeout(3000)
                else:
                    print("⚠ 未找到登录按钮，可能已登录")
                    return True
                    
            except Exception as e:
                print(f"⚠ 点击登录按钮失败: {e}")
                print("尝试继续执行...")
            
            # 尝试选择抖音登录
            print("\n查找抖音登录选项...")
            try:
                douyin_selectors = [
                    "div:has-text('抖音')",
                    "span:has-text('抖音')",
                    "text=抖音",
                    "[class*='douyin']"
                ]
                
                douyin_login = None
                for selector in douyin_selectors:
                    try:
                        douyin_login = await self.page.wait_for_selector(selector, timeout=5000)
                        if douyin_login:
                            print(f"✓ 找到抖音登录，使用选择器: {selector}")
                            break
                    except:
                        continue
                
                if douyin_login:
                    await douyin_login.click()
                    print("✓ 已选择抖音登录")
                    await self.page.wait_for_timeout(3000)
                else:
                    print("⚠ 未找到抖音登录选项，可能默认就是抖音登录")
                    
            except Exception as e:
                print(f"⚠ 选择抖音登录失败: {e}")
            
            # 保存登录页面截图
            await self.page.screenshot(path='qrcode_page.png')
            print("✓ 已保存二维码页面截图: qrcode_page.png")
            
            # 等待扫码登录完成
            print("\n" + "="*60)
            print("请使用抖音扫描二维码完成登录...")
            print("提示：查看 qrcode_page.png 可以看到二维码")
            print("等待登录中，最多等待180秒...")
            print("="*60 + "\n")
            
            # 等待登录成功（URL变化或出现用户信息）
            start_time = time.time()
            while time.time() - start_time < 180:
                current_url = self.page.url
                elapsed = int(time.time() - start_time)
                
                # 每30秒打印一次进度
                if elapsed % 30 == 0 and elapsed > 0:
                    print(f"⏳ 等待中... 已等待 {elapsed} 秒")
                
                # 检查是否登录成功
                if "login" not in current_url.lower() and "home" in current_url.lower():
                    # 再次检查页面内容
                    new_content = await self.page.content()
                    if "登录" not in new_content or "扫码" not in new_content:
                        print(f"\n✓ 登录成功！(耗时 {elapsed} 秒)")
                        await self.save_cookies()
                        return True
                
                # 检查是否有用户头像等元素
                try:
                    user_selectors = [
                        "div.user-info",
                        "div.avatar",
                        "img.avatar",
                        ".user-name",
                        "[class*='user'] [class*='name']"
                    ]
                    
                    for selector in user_selectors:
                        user_element = await self.page.query_selector(selector)
                        if user_element and await user_element.is_visible():
                            print(f"\n✓ 登录成功！(检测到用户元素，耗时 {elapsed} 秒)")
                            await self.save_cookies()
                            return True
                except Exception:
                    pass
                
                await self.page.wait_for_timeout(2000)
            
            print(f"\n✗ 登录超时（180秒）")
            print("提示：如果二维码已过期，请重新运行程序")
            return False
            
        except Exception as e:
            print(f"\n✗ 登录过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def check_login_status(self) -> bool:
        """检查登录状态"""
        try:
            # 使用 domcontentloaded 而不是 networkidle，避免长时间等待
            print("正在检查登录状态...")
            await self.page.goto("https://jimeng.jianying.com/ai-tool/home", wait_until='domcontentloaded', timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # 保存截图以便调试
            try:
                await self.page.screenshot(path='check_login.png')
                print("✓ 已保存登录检查截图: check_login.png")
            except:
                pass
            
            # 检查页面内容
            content = await self.page.content()
            print(f"当前URL: {self.page.url}")
            
            # 更严格的登录检查
            # 如果页面包含"登录"和"扫码"，说明需要登录
            needs_login = ("登录" in content and "扫码" in content)
            
            # 检查是否有用户相关元素
            has_user_info = False
            user_selectors = [
                "div.user-info",
                "div.avatar", 
                "img.avatar",
                ".user-name",
                "[class*='user']",
                "text=我的"
            ]
            
            for selector in user_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        has_user_info = True
                        print(f"✓ 检测到用户元素: {selector}")
                        break
                except:
                    continue
            
            # 检查URL
            is_login_page = "login" in self.page.url.lower() or "passport" in self.page.url.lower()
            
            print(f"需要登录: {needs_login}")
            print(f"有用户信息: {has_user_info}")
            print(f"是登录页: {is_login_page}")
            
            # 判断逻辑：
            # 1. 如果需要登录且是登录页 -> 未登录
            # 2. 如果有用户信息 -> 已登录
            # 3. 如果不需要登录 -> 已登录
            
            if needs_login and is_login_page:
                print("⚠ 检测到登录页面，Cookie可能已过期或未设置")
                return False
            
            if has_user_info:
                print("✓ Cookie登录状态检查通过（检测到用户信息）")
                return True
                
            if not needs_login:
                print("✓ Cookie登录状态检查通过（页面不需要登录）")
                return True
            
            # 如果不确定，截图并返回False
            print("⚠ 无法确定登录状态，请检查截图")
            return False
            
        except Exception as e:
            print(f"✗ 检查登录状态失败: {e}")
            # 即使检查失败，也尝试继续（可能是网络问题）
            print("⚠ 尝试继续执行，跳过登录检查")
            return True
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            print("✓ 浏览器已关闭")
