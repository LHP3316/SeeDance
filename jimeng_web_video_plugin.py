"""
即梦 Web 视频插件适配器
通过 Playwright 浏览器自动化调用即梦网页版生成视频

功能：
1. 控制浏览器操作即梦网页
2. 上传图片、输入提示词、选择参数
3. 等待视频生成完成
4. 下载视频到本地

使用方法：
    adapter = JimengWebVideoPlugin()
    result = adapter.generate_video(
        image_paths=["/path/to/image1.png", "/path/to/image2.png"],
        prompt="提示词",
        model="seedance-2.0",
        ratio="16:9",
        duration=5
    )
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright, Page

logger = logging.getLogger(__name__)


class JimengWebVideoPlugin:
    """即梦 Web 视频插件适配器"""
    
    def __init__(self, browser_exe: Optional[str] = None, headless: bool = False):
        """
        初始化插件
        
        Args:
            browser_exe: 浏览器可执行文件路径（留空则自动查找）
            headless: 是否无头模式（默认False，方便调试）
        """
        self.browser_exe = browser_exe
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # 即梦网页 URL
        self.jimeng_url = "https://jimeng.jianying.com"
        
        # 浏览器数据目录（持久化 Cookie 和登录状态）
        self.user_data_dir = str(Path(__file__).parent / "browser_data")
        Path(self.user_data_dir).mkdir(exist_ok=True)
        
        logger.info(f"[JimengWebVideoPlugin] 初始化完成")
        logger.info(f"  - 浏览器路径: {browser_exe or '自动查找'}")
        logger.info(f"  - 无头模式: {headless}")
        logger.info(f"  - 用户数据目录: {self.user_data_dir}")
    
    def _launch_browser(self):
        """启动浏览器"""
        try:
            # 先关闭旧的实例（避免冲突）
            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass
            
            self.playwright = sync_playwright().start()
            
            # 浏览器启动参数
            launch_args = {
                "headless": self.headless,
                "args": [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            }
            
            # 如果指定了浏览器路径
            if self.browser_exe:
                launch_args["executable_path"] = self.browser_exe
            
            # 使用 persistent_context 持久化 Cookie 和登录状态
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                **launch_args,
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 创建页面
            self.page = self.context.new_page()
            
            logger.info("[JimengWebVideoPlugin] 浏览器启动成功（持久化模式）")
            
        except Exception as e:
            logger.error(f"[JimengWebVideoPlugin] 浏览器启动失败: {e}")
            raise
    
    def _close_browser(self):
        """关闭浏览器"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            logger.info("[JimengWebVideoPlugin] 浏览器已关闭")
            
        except Exception as e:
            logger.error(f"[JimengWebVideoPlugin] 关闭浏览器失败: {e}")
    
    def open_login_browser(self):
        """
        打开登录浏览器（用户手动登录）
        自动检测登录状态，登录成功后自动继续
        
        Returns:
            {"ok": bool, "message": str, "error": str}
        """
        try:
            self._launch_browser()
            
            # 打开即梦网页
            self.page.goto(self.jimeng_url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
            
            logger.info("[JimengWebVideoPlugin] 已打开即梦网页")
            
            # 检查是否已经登录（持久化 Cookie）
            if self._check_is_logged_in():
                logger.info("[JimengWebVideoPlugin] 检测到已登录状态（持久化 Cookie）")
                return {
                    "ok": True,
                    "message": "已自动登录"
                }
            
            # 未登录，等待用户手动登录
            logger.info("[JimengWebVideoPlugin] 未检测到登录状态，请在浏览器中登录...")
            logger.info("[JimengWebVideoPlugin] 等待登录中（最多5分钟）...")
            
            # 循环检测登录状态（每 2 秒检测一次，最多等待 5 分钟）
            max_wait = 300  # 5分钟
            check_interval = 2
            elapsed = 0
            
            while elapsed < max_wait:
                time.sleep(check_interval)
                elapsed += check_interval
                
                if self._check_is_logged_in():
                    logger.info(f"[JimengWebVideoPlugin] 检测到用户已登录（等待了 {elapsed} 秒）")
                    return {
                        "ok": True,
                        "message": f"登录成功（等待了 {elapsed} 秒）"
                    }
                
                # 每 30 秒打印一次日志
                if elapsed % 30 == 0:
                    logger.info(f"[JimengWebVideoPlugin] 等待登录中... ({elapsed}/{max_wait}秒)")
            
            # 超时
            logger.error("[JimengWebVideoPlugin] 等待登录超时（5分钟）")
            return {
                "ok": False,
                "error": "等待登录超时"
            }
            
        except Exception as e:
            logger.error(f"[JimengWebVideoPlugin] 打开登录浏览器失败: {e}")
            return {
                "ok": False,
                "error": str(e)
            }
    
    def _check_is_logged_in(self) -> bool:
        """
        检查用户是否已登录
        
        Returns:
            True 已登录，False 未登录
        """
        try:
            # 方法1：检查是否存在用户头像或用户名元素
            user_elements = [
                '.avatar',           # 头像
                '.user-name',        # 用户名
                '[class*="avatar"]', # 包含 avatar 的类
                '[class*="user"]',   # 包含 user 的类
                'text="我的"',       # 我的按钮
                'text="空间"',       # 空间按钮
            ]
            
            for selector in user_elements:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        return True
                except:
                    continue
            
            # 方法2：检查是否有登录按钮（如果看不到登录按钮说明已登录）
            login_buttons = [
                'text="登录"',
                'text="登 录"',
                'text="扫码登录"',
            ]
            
            for selector in login_buttons:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        # 看到登录按钮，说明未登录
                        return False
                except:
                    continue
            
            # 如果看不到登录按钮，说明可能已登录
            return True
            
        except Exception as e:
            logger.debug(f"[JimengWebVideoPlugin] 检查登录状态失败: {e}")
            return False
    
    def generate_video(
        self,
        image_paths: List[str],
        prompt: str,
        model: str = "seedance-2.0",
        ratio: str = "16:9",
        duration: int = 5,
        generation_mode: str = "omni_reference",
        timeout: int = 900
    ) -> Dict:
        """
        通过浏览器自动化生成视频
        
        Args:
            image_paths: 本地图片路径列表
            prompt: 提示词
            model: 模型（seedance-2.0, seedance-2.0-fast, seedance-2.0-vip, seedance-2.0-fast-vip）
            ratio: 画幅比例（16:9, 9:16, 1:1, 4:3, 3:4, 21:9）
            duration: 时长（秒，4-15）
            generation_mode: 生成模式（first_end_frame 首尾帧, omni_reference 全能参考）
            timeout: 超时时间（秒）
            
        Returns:
            {
                "success": bool,
                "video_url": str,
                "saved_file": str,
                "error": str
            }
        """
        result = {
            "success": False,
            "video_url": None,
            "saved_file": None,
            "error": None
        }
        
        try:
            # 1. 启动浏览器
            logger.info("[1/6] 启动浏览器...")
            self._launch_browser()
            
            # 2. 打开即梦网页（带重试机制）
            logger.info("[2/6] 打开即梦网页...")
            max_retries = 3
            retry_count = 0
            page_loaded = False
            
            while retry_count < max_retries:
                try:
                    self.page.goto(self.jimeng_url, wait_until="domcontentloaded", timeout=30000)
                    self.page.wait_for_timeout(2000)
                    page_loaded = True
                    logger.info(f"[JimengWebVideoPlugin] 网页加载成功（尝试 {retry_count + 1}/{max_retries}）")
                    break
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"[JimengWebVideoPlugin] 网页加载失败（{retry_count}/{max_retries}）: {e}")
                    
                    if retry_count < max_retries:
                        logger.info(f"[JimengWebVideoPlugin] 等待 3 秒后重试...")
                        time.sleep(3)
                    else:
                        raise Exception(f"网页加载失败，已重试 {max_retries} 次")
            
            if not page_loaded:
                raise Exception("网页加载失败")
            
            # 3. 选择视频生成模式
            logger.info("[3/6] 选择视频生成模式...")
            self._navigate_to_video_gen()
            
            # 4. 上传图片
            logger.info("[4/6] 上传图片...")
            self._upload_images(image_paths)
            
            # 5. 输入参数（传递图片路径列表）
            logger.info("[5/6] 设置生成参数...")
            self._set_generation_params(
                prompt=prompt,
                model=model,
                ratio=ratio,
                duration=duration,
                generation_mode=generation_mode,
                image_paths=image_paths
            )
            
            # 6. 点击生成并等待
            logger.info("[6/6] 开始生成视频...")
            video_url = self._click_generate_and_wait(timeout=timeout)
            
            if video_url:
                result["success"] = True
                result["video_url"] = video_url
                logger.info(f"视频生成成功: {video_url}")
            else:
                result["error"] = "视频生成失败，未获取到视频URL"
                logger.error(result["error"])
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"[JimengWebVideoPlugin] 生成视频失败: {e}", exc_info=True)
        
        finally:
            # 关闭浏览器
            self._close_browser()
        
        return result
    
    def _navigate_to_video_gen(self):
        """导航到视频生成页面"""
        try:
            # 直接访问视频生成页面
            video_gen_url = f"{self.jimeng_url}/ai-tool/generate?workspace=0&type=video"
            logger.info(f"导航到视频生成页面: {video_gen_url}")
            
            self.page.goto(video_gen_url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(3000)  # 等待页面加载完成
            
            logger.info("已成功进入视频生成页面")
                
        except Exception as e:
            logger.error(f"导航到视频生成页面失败: {e}")
            raise
    
    def _upload_images(self, image_paths: List[str]) -> List:
        """
        上传图片
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            上传成功的图片元素列表
        """
        uploaded_elements = []
        
        try:
            # 查找上传按钮
            upload_button = self.page.query_selector('input[type="file"]')
            
            if not upload_button:
                raise Exception("未找到上传按钮")
            
            # 上传所有图片（多文件上传）
            file_input = self.page.query_selector('input[type="file"]')
            file_input.set_input_files(image_paths)
            
            logger.info(f"已上传 {len(image_paths)} 张图片")
            time.sleep(3)  # 等待上传完成
            
            # 等待图片上传完成后，查找页面上的图片元素
            # 即梦会显示上传的图片缩略图
            self.page.wait_for_timeout(2000)
            
            # 尝试获取上传的图片元素（根据实际网页结构调整选择器）
            # 通常会有图片预览区域
            image_elements = self.page.query_selector_all('.image-preview, .upload-item, [class*="image"]')
            
            if image_elements:
                logger.info(f"检测到 {len(image_elements)} 个图片元素")
                uploaded_elements = image_elements
            else:
                logger.warning("未检测到图片元素，将继续执行")
            
            return uploaded_elements
            
        except Exception as e:
            logger.error(f"上传图片失败: {e}")
            raise
    
    def _set_generation_params(
        self,
        prompt: str,
        model: str,
        ratio: str,
        duration: int,
        generation_mode: str,
        image_paths: List[str] = None
    ):
        """
        设置生成参数
        
        Args:
            prompt: 提示词（包含 @本地文件名是描述 格式）
            model: 模型
            ratio: 比例
            duration: 时长
            generation_mode: 生成模式
            image_paths: 图片路径列表（按顺序）
        """
        try:
            # 1. 找到提示词输入框（即梦使用的是 contenteditable div）
            prompt_input = self.page.query_selector('div[contenteditable="true"]')
            if not prompt_input:
                logger.warning("未找到提示词输入框")
                return
            
            # 2. 点击提示词框，聚焦
            prompt_input.click()
            time.sleep(1)
            
            # 3. 解析提示词
            # 格式：@文件名1是描述1，@文件名2是描述2，其他文本
            import re
            import os
            
            # 提取所有 @文件名是描述 的部分
            pattern = r'@([^，,。；;\s]+)是([^，,。；;]+)'
            matches = re.findall(pattern, prompt)
            
            # 提取纯文本部分（去掉所有 @引用）
            pure_text = re.sub(r'@[^，,。；;\s]+是[^，,。；;]+[,，]?', '', prompt).strip()
            pure_text = pure_text.lstrip('，,').strip()
            
            logger.info(f"解析到 {len(matches)} 个图片引用")
            logger.info(f"纯文本: {pure_text}")
            
            # 4. 按顺序处理每个图片引用
            for idx, (filename, desc) in enumerate(matches):
                logger.info(f"[{idx+1}/{len(matches)}] 处理图片: {filename} -> {desc}")
                
                # 输入 @ 触发选择器
                prompt_input.focus()
                self.page.keyboard.type('@')
                time.sleep(2)  # 等待选择器弹出
                
                # TODO: 选择第 idx+1 张图片
                # 需要根据实际网页结构调整选择器
                # 即梦的选择器应该会有图片列表，选择对应的图片
                
                # 暂时使用键盘方向键选择（需要根据实际情况调整）
                if idx > 0:
                    # 按右箭头键移动到下一个图片
                    for _ in range(idx):
                        self.page.keyboard.press('ArrowRight')
                        time.sleep(0.3)
                
                # 按回车选择图片
                self.page.keyboard.press('Enter')
                time.sleep(1)
                
                # 输入描述
                self.page.keyboard.type(desc)
                time.sleep(0.5)
                
                # 输入逗号（如果有）
                if idx < len(matches) - 1 or pure_text:
                    self.page.keyboard.type('，')
                    time.sleep(0.5)
            
            # 5. 输入纯文本部分
            if pure_text:
                logger.info(f"输入纯文本: {pure_text}")
                self.page.keyboard.type(pure_text)
                time.sleep(0.5)
            
            logger.info("提示词输入完成")
            
            # 2. 选择模型
            model_select = self.page.query_selector('select:has(option[value*="seedance"])')
            if model_select:
                model_select.select_option(value=model)
                logger.info(f"已选择模型: {model}")
            
            # 3. 选择比例
            ratio_select = self.page.query_selector(f'select:has(option[value="{ratio}"])')
            if ratio_select:
                ratio_select.select_option(value=ratio)
                logger.info(f"已选择比例: {ratio}")
            
            # 4. 选择时长
            duration_select = self.page.query_selector('select:has(option[value*="duration"])')
            if duration_select:
                duration_select.select_option(value=str(duration))
                logger.info(f"已选择时长: {duration}秒")
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"设置生成参数失败: {e}")
            raise
    
    def _click_generate_and_wait(self, timeout: int = 900) -> Optional[str]:
        """
        点击生成按钮并等待视频完成
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            视频 URL 或 None
        """
        try:
            # 1. 点击生成按钮（根据截图，按钮 class 为 lv-btn lv-btn-primary lv-btn-icon-only）
            generate_button = self.page.query_selector('button.lv-btn.lv-btn-primary.lv-btn-icon-only')
            if not generate_button:
                # 备用选择器：查找包含“生成”文本的按钮
                generate_button = self.page.query_selector('button:has-text("生成")')
            
            if not generate_button:
                raise Exception("未找到生成按钮")
            
            generate_button.click()
            logger.info("已点击生成按钮，等待视频生成...")
            
            # 2. 等待视频生成完成
            # 方法1：监听网络请求获取视频URL
            video_url = None
            
            def handle_response(response):
                nonlocal video_url
                # 监听视频相关的响应
                if '.mp4' in response.url and 'jimeng' in response.url:
                    video_url = response.url
                    logger.info(f"检测到视频URL: {video_url}")
            
            self.page.on("response", handle_response)
            
            # 3. 等待生成完成（最多等待 timeout 秒）
            start_time = time.time()
            while time.time() - start_time < timeout:
                # 检查是否生成完成
                try:
                    # 查找视频播放器或下载按钮
                    video_element = self.page.query_selector('video')
                    if video_element:
                        src = video_element.get_attribute('src')
                        if src:
                            video_url = src
                            logger.info(f"从video元素获取URL: {video_url}")
                            break
                    
                    # 查找下载按钮
                    download_button = self.page.query_selector('button:has-text("下载")')
                    if download_button:
                        logger.info("检测到下载按钮，视频已生成完成")
                        break
                        
                except:
                    pass
                
                time.sleep(2)
                
                # 检查是否失败
                error_text = self.page.query_selector('text="生成失败"')
                if error_text:
                    raise Exception("视频生成失败")
            
            if not video_url:
                logger.warning("未获取到视频URL，尝试从页面提取")
                # 尝试从页面中提取视频URL
                video_url = self._extract_video_url_from_page()
            
            return video_url
            
        except Exception as e:
            logger.error(f"等待视频生成失败: {e}")
            return None
    
    def _extract_video_url_from_page(self) -> Optional[str]:
        """从页面中提取视频URL"""
        try:
            # 尝试多种方式提取视频URL
            # 1. 从 video 标签
            video_src = self.page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    return video ? video.src : null;
                }
            """)
            
            if video_src:
                return video_src
            
            # 2. 从 a 标签的 href
            download_link = self.page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*=".mp4"]'));
                    return links.length > 0 ? links[0].href : null;
                }
            """)
            
            if download_link:
                return download_link
            
            # 3. 从 API 响应中提取（需要拦截网络请求）
            # 这部分比较复杂，暂时省略
            
            return None
            
        except Exception as e:
            logger.error(f"从页面提取视频URL失败: {e}")
            return None


# 测试代码
if __name__ == "__main__":
    import logging
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建插件实例
    plugin = JimengWebVideoPlugin(headless=False)
    
    # 测试打开登录浏览器
    print("测试打开登录浏览器...")
    result = plugin.open_login_browser()
    print(f"结果: {result}")
    
    # 等待用户手动登录后，再测试生成视频
    input("请手动完成登录后，按回车继续测试视频生成...")
    
    # 测试生成视频
    print("\n测试生成视频...")
    result = plugin.generate_video(
        image_paths=["test_image1.png", "test_image2.png"],
        prompt="测试提示词",
        model="seedance-2.0",
        ratio="16:9",
        duration=5
    )
    print(f"结果: {result}")
