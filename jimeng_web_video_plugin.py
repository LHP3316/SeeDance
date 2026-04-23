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
import json
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
        self._keep_browser_open = False  # 登录失败时保持浏览器打开
        
        # 即梦网页基础 URL
        self.jimeng_base_url = "https://jimeng.jianying.com"
        # 即梦首页（启动时访问）
        self.jimeng_home_url = f"{self.jimeng_base_url}/ai-tool/home/"
        
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
                    '--no-sandbox',
                    f'--window-size=1920,1080',  # 窗口大小
                    f'--window-position=0,0',  # 窗口位置（屏幕左上角）
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
            self.page.goto(self.jimeng_home_url, wait_until="domcontentloaded", timeout=30000)
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
            # 方法1：检查 URL 是否包含登录相关路径
            current_url = self.page.url
            if '/login' in current_url or '/auth' in current_url:
                logger.debug(f"[JimengWebVideoPlugin] 当前URL包含登录路径: {current_url}")
                return False
            
            # 方法2：检查页面是否有明显的“登录”按钮（多种可能的文本和位置）
            login_indicators = [
                'text="登录"',
                'text="登 录"',
                'text="扫码登录"',
                'text="立即登录"',
                'a:has-text("登录")',  # 链接中包含“登录”
                'button:has-text("登录")',  # 按钮中包含“登录”
            ]
            
            for selector in login_indicators:
                try:
                    elements = self.page.query_selector_all(selector)
                    for element in elements:
                        if element and element.is_visible():
                            text = element.inner_text().strip()
                            logger.debug(f"[JimengWebVideoPlugin] 找到登录按钮: {text}")
                            return False  # 找到登录按钮，说明未登录
                except Exception as e:
                    logger.debug(f"[JimengWebVideoPlugin] 检查登录指示器失败: {selector}, {e}")
                    continue
            
            # 方法3：检查是否有用户头像或用户名（已登录的标志）
            user_indicators = [
                'img.avatar',  # 头像图片
                '.user-avatar img',
                '[class*="avatar"] img',
            ]
            
            for selector in user_indicators:
                try:
                    elements = self.page.query_selector_all(selector)
                    for element in elements:
                        if element and element.is_visible():
                            src = element.get_attribute('src') or ''
                            # 头像应该有真实的图片URL，不是占位符
                            if src and 'placeholder' not in src and src != '#':
                                logger.debug(f"[JimengWebVideoPlugin] 找到用户头像: {src[:50]}")
                                return True  # 找到真实头像，说明已登录
                except Exception as e:
                    logger.debug(f"[JimengWebVideoPlugin] 检查用户标识失败: {selector}, {e}")
                    continue
            
            # 方法4：检查是否有 Cookie 中的登录标识
            cookies = self.context.cookies()
            for cookie in cookies:
                if cookie['name'] in ['session_id', 'passport_csrf_token', 'uid', 'user_id']:
                    if cookie['value'] and cookie['value'] != '':
                        logger.debug(f"[JimengWebVideoPlugin] 找到登录Cookie: {cookie['name']}")
                        return True
            
            # 如果以上都没找到，默认为未登录（更安全）
            logger.warning("[JimengWebVideoPlugin] 未能确定登录状态，默认为未登录")
            return False
            
        except Exception as e:
            logger.error(f"[JimengWebVideoPlugin] 检查登录状态异常: {e}")
            return False
    
    def generate_video(
        self,
        image_paths: List[str],
        prompt: str,
        model: str = "seedance-2.0",
        ratio: str = "16:9",
        duration: int = 5,
        generation_mode: str = "omni_reference",
        timeout: int = 900,
        output_dir: str = "output",
        on_history_id_captured=None
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
            output_dir: 视频保存目录
            on_history_id_captured: history_record_id 捕获后的回调函数，立即调用
            
        Returns:
            {
                "success": bool,
                "video_url": str,
                "saved_file": str,
                "history_record_id": str,  # 即梦平台历史记录ID
                "error": str
            }
        """
        # 方法入口日志
        logger.info("="*70)
        logger.info("🎬 [JimengWebVideoPlugin.generate_video] 方法被调用！")
        logger.info("="*70)
        logger.info(f"  → image_paths: {image_paths}")
        logger.info(f"  → prompt: {prompt[:50]}...")
        logger.info(f"  → model: {model}")
        logger.info(f"  → ratio: {ratio}")
        logger.info(f"  → duration: {duration}")
        logger.info(f"  → generation_mode: {generation_mode}")
        logger.info(f"  → timeout: {timeout}")
        logger.info(f"  → output_dir: {output_dir}")
        logger.info("="*70)
        
        result = {
            "success": False,
            "video_url": None,
            "saved_file": None,
            "history_record_id": None,  # 即梦平台历史记录ID
            "error": None
        }
        
        try:
            # 1. 启动浏览器
            logger.info("[1/6] 启动浏览器...")
            logger.info("[1/6]   → 正在初始化 Playwright...")
            self._launch_browser()
            logger.info("[1/6]   ✓ 浏览器启动成功")
            
            # 2. 打开即梦网页（带重试机制）
            logger.info("[2/6] 打开即梦网页...")
            logger.info(f"[2/6]   → URL: {self.jimeng_home_url}")
            max_retries = 3
            retry_count = 0
            page_loaded = False
            
            while retry_count < max_retries:
                try:
                    logger.info(f"[2/6]   → 尝试加载网页（{retry_count + 1}/{max_retries}）...")
                    self.page.goto(self.jimeng_home_url, wait_until="domcontentloaded", timeout=30000)
                    logger.info(f"[2/6]   → 等待页面稳定...")
                    self.page.wait_for_timeout(2000)
                    page_loaded = True
                    logger.info(f"[2/6]   ✓ 网页加载成功（尝试 {retry_count + 1}/{max_retries}）")
                    break
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"[2/6]   ✗ 网页加载失败（{retry_count}/{max_retries}）: {e}")
                    
                    if retry_count < max_retries:
                        logger.info(f"[2/6]   → 等待 3 秒后重试...")
                        time.sleep(3)
                    else:
                        raise Exception(f"网页加载失败，已重试 {max_retries} 次")
            
            if not page_loaded:
                raise Exception("网页加载失败")
            
            # 2.5 先导航到首页，等待30秒后再检测登录状态
            logger.info("[2.5/6] 导航到首页并等待加载...")
            logger.info(f"[2.5/6]   → 访问: {self.jimeng_home_url}")
            
            try:
                self.page.goto(self.jimeng_home_url, wait_until="domcontentloaded", timeout=30000)
                logger.info(f"[2.5/6]   → 等待30秒让页面完全加载...")
                self.page.wait_for_timeout(30000)  # 等待30秒
                logger.info(f"[2.5/6]   ✓ 首页加载完成")
            except Exception as e:
                logger.warning(f"[2.5/6]   ⚠️ 首页加载失败: {e}")
            
            # 2.6 检查登录状态
            logger.info("[2.6/6] 检查登录状态...")
            logger.info("[2.6/6]   → 开始检测页面登录状态...")
            
            try:
                is_logged = self._check_is_logged_in()
                logger.info(f"[2.6/6]   → 检测结果: {'已登录' if is_logged else '未登录'}")
            except Exception as e:
                logger.error(f"[2.6/6]   ✗ 登录检测异常: {e}")
                is_logged = False
            
            if not is_logged:
                logger.warning("[2.6/6]   ⚠️ 未检测到登录状态！")
                logger.info("[2.6/6]   → 浏览器将保持打开，请在浏览器中登录即梦账号")
                logger.info("[2.6/6]   → 等待登录中（最多300秒）...")
                logger.info("[2.6/6]   → 提示：请查看弹出的浏览器窗口，手动扫码登录")
                
                # 等待登录（较长超时，给用户时间登录）
                max_wait = 300
                check_interval = 2
                elapsed = 0
                logged_in = False
                
                while elapsed < max_wait:
                    try:
                        time.sleep(check_interval)
                        elapsed += check_interval
                        
                        try:
                            if self._check_is_logged_in():
                                logger.info(f"[2.6/6]   ✅ 检测到用户已登录（等待了 {elapsed} 秒）")
                                logged_in = True
                                break
                        except Exception as check_err:
                            logger.debug(f"[2.6/6]   → 检查登录状态异常: {check_err}")
                        
                        if elapsed % 10 == 0:
                            logger.info(f"[2.6/6]   → 等待登录中... ({elapsed}/{max_wait}秒) - 浏览器窗口应保持打开")
                    except Exception as e:
                        logger.error(f"[2.6/6]   ✗ 等待登录异常: {e}")
                        break
                
                if not logged_in:
                    result["error"] = f"未登录！请在浏览器中登录即梦账号（等待了{max_wait}秒超时）"
                    logger.error(f"[2.6/6]   ✗ {result['error']}")
                    logger.error("提示：浏览器窗口应该还在，请手动登录后重试任务")
                    # 不关闭浏览器，让用户可以继续操作
                    self._keep_browser_open = True
                    return result
            else:
                logger.info("[2.6/6]   ✅ 已登录，继续执行")
            
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
            generate_result = self._click_generate_and_wait(
                timeout=timeout, 
                output_dir=output_dir,
                on_history_id_captured=on_history_id_captured
            )
            
            if generate_result and generate_result.get("video_url"):
                result["success"] = True
                result["video_url"] = generate_result["video_url"]
                result["history_record_id"] = generate_result.get("history_record_id")
                logger.info(f"视频生成成功: {generate_result['video_url']}")
                logger.info(f"history_record_id: {generate_result.get('history_record_id')}")
            else:
                result["error"] = "视频生成失败，未获取到视频URL"
                logger.error(result["error"])
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"[JimengWebVideoPlugin] 生成视频失败: {e}", exc_info=True)
        
        finally:
            # 关闭浏览器（但如果是登录失败，保持浏览器打开让用户操作）
            if not getattr(self, '_keep_browser_open', False):
                self._close_browser()
            else:
                logger.info("[JimengWebVideoPlugin] 保持浏览器打开（登录失败场景）")
                self._keep_browser_open = False  # 重置标志
        
        return result
    
    def _navigate_to_video_gen(self):
        """导航到视频生成页面"""
        try:
            # 直接访问视频生成页面
            video_gen_url = f"{self.jimeng_base_url}/ai-tool/generate?workspace=0&type=video"
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
            logger.info("[4/6] 上传图片...")
            logger.info(f"  待上传图片数量: {len(image_paths)}")
            
            # 打印当前页面的URL
            logger.info(f"  当前页面URL: {self.page.url}")
            
            # 查找上传按钮
            upload_button = self.page.query_selector('input[type="file"]')
            
            if not upload_button:
                logger.error("✗ 未找到上传按钮 input[type='file']")
                # 尝试打印页面中的所有input元素
                all_inputs = self.page.query_selector_all('input')
                logger.info(f"  页面中找到 {len(all_inputs)} 个input元素:")
                for i, inp in enumerate(all_inputs[:10], 1):
                    input_type = inp.get_attribute('type') or 'unknown'
                    input_id = inp.get_attribute('id') or 'no-id'
                    input_class = inp.get_attribute('class') or 'no-class'
                    logger.info(f"    [{i}] type={input_type}, id={input_id}, class={input_class}")
                raise Exception("未找到上传按钮")
            
            logger.info("  ✓ 找到上传按钮 input[type='file']")
            
            # 逐个上传文件（即梦网页只支持单文件上传）
            file_input = self.page.query_selector('input[type="file"]')
            
            # 即梦可能需要先点击上传区域才能激活文件选择
            # 先尝试找到并点击上传按钮的视觉元素
            upload_area = self.page.query_selector('[class*="upload"], [class*="add"], [class*="reference"]')
            if upload_area:
                logger.info("  尝试点击上传区域...")
                upload_area.click()
                self.page.wait_for_timeout(1000)
            
            for idx, image_path in enumerate(image_paths, 1):
                # 转换为绝对路径（Windows下必须是绝对路径）
                abs_path = os.path.abspath(image_path)
                
                # 检查文件是否存在
                if not os.path.exists(abs_path):
                    logger.error(f"✗ 文件不存在: {abs_path}")
                    raise Exception(f"文件不存在: {abs_path}")
                
                file_size = os.path.getsize(abs_path)
                logger.info(f"\n  [{idx}/{len(image_paths)}] 开始上传图片:")
                logger.info(f"    文件名: {os.path.basename(abs_path)}")
                logger.info(f"    完整路径: {abs_path}")
                logger.info(f"    文件大小: {file_size / 1024:.2f} KB")
                
                # 上传前：记录页面状态
                logger.info(f"    上传前页面URL: {self.page.url}")
                
                # 方法1: 使用 set_input_files
                try:
                    file_input.set_input_files(abs_path)
                    logger.info(f"    ✓ set_input_files 调用成功")
                except Exception as e:
                    logger.error(f"    ✗ set_input_files 调用失败: {e}")
                    raise
                
                # 等待上传完成
                logger.info(f"    等待5秒让即梦处理上传...")
                self.page.wait_for_timeout(5000)
                
                # 上传后：检查页面变化
                logger.info(f"    上传后页面URL: {self.page.url}")
                
                # 尝试查找页面上的图片元素
                temp_images = self.page.query_selector_all('img')
                logger.info(f"    页面中img元素数量: {len(temp_images)}")
                
                # 检查是否有错误提示
                error_elements = self.page.query_selector_all('[class*="error"], [class*="fail"], [class*="alert"]')
                if error_elements:
                    logger.warning(f"    ⚠ 检测到 {len(error_elements)} 个错误提示元素")
                
                # 检查是否检测到新上传的图片（通过查找包含blob或data的图片）
                blob_images = self.page.query_selector_all('img[src*="blob:"]')
                data_images = self.page.query_selector_all('img[src*="data:"]')
                logger.info(f"    blob URL图片: {len(blob_images)}, data URL图片: {len(data_images)}")
                
                logger.info(f"  ✓ 第 {idx} 张图片上传完成\n")
            
            logger.info(f"\n✓ 已成功上传 {len(image_paths)} 张图片")
            
            # 等待即梦网页处理所有图片
            logger.info("等待8秒让即梦处理和显示所有图片...")
            time.sleep(8)
            
            # 尝试获取上传的图片元素
            logger.info("检测页面上的图片元素...")
            self.page.wait_for_timeout(3000)
            
            # 尝试多种选择器来检测上传的图片
            selectors = [
                '.image-preview',
                '.upload-item', 
                '[class*="image"]',
                '[class*="upload"]',
                'img[src*="blob:"]',
                'img[src*="data:"]',
                '[class*="preview"]'
            ]
            
            for selector in selectors:
                elements = self.page.query_selector_all(selector)
                if elements:
                    logger.info(f"  选择器 '{selector}' 找到 {len(elements)} 个元素")
                    if not uploaded_elements:
                        uploaded_elements = elements
            
            if uploaded_elements:
                logger.info(f"✓ 检测到 {len(uploaded_elements)} 个图片元素")
            else:
                logger.warning("⚠ 未检测到图片元素，但上传可能已成功，将继续执行")
                # 截图保存当前页面状态，便于调试
                screenshot_path = os.path.join(os.path.dirname(__file__), 'upload_debug.png')
                self.page.screenshot(path=screenshot_path)
                logger.info(f"  已保存页面截图到: {screenshot_path}")
            
            return uploaded_elements
            
        except Exception as e:
            logger.error(f"✗ 上传图片失败: {e}")
            import traceback
            traceback.print_exc()
            # 失败时也截图
            try:
                screenshot_path = os.path.join(os.path.dirname(__file__), 'upload_error.png')
                self.page.screenshot(path=screenshot_path)
                logger.info(f"  已保存错误截图到: {screenshot_path}")
            except:
                pass
            raise
    
    def _select_model(self, model_name: str):
        """
        选择模型（即梦使用的是自定义下拉选择器）
        
        Args:
            model_name: 模型名称，如 "Seedance 2.0 VIP"
        """
        try:
            # 1. 找到并点击模型选择器
            # 根据 HTML 代码，模型选择器是第二个 combobox，显示 "Seedance 2.0"
            # 查找所有 lv-select-view-value，找到包含 "Seedance" 的那个
            all_selectors = self.page.query_selector_all('span.lv-select-view-value')
            model_selector = None
            current_model = None
                        
            for selector in all_selectors:
                text = selector.inner_text()
                if 'Seedance' in text or 'seedance' in text.lower():
                    model_selector = selector
                    current_model = text.strip()
                    logger.info(f"当前模型: {current_model}")
                    break
                        
            if not model_selector:
                logger.warning(f"未找到模型选择器，跳过模型选择")
                return
                        
            # 2. 如果当前模型已经是目标模型，不需要选择
            if current_model == model_name:
                logger.info(f"当前模型已经是 {model_name}，无需选择")
                return
                        
            logger.info(f"点击模型选择器...")
            model_selector.click()
            time.sleep(5)  # 等待弹出列表
                        
            # 2.5. 先输出所有选项用于调试
            all_options = self.page.query_selector_all('li[role="option"]')
            logger.info(f"找到 {len(all_options)} 个模型选项:")
            for i, option in enumerate(all_options):
                # 只获取模型名称，不包含描述文字
                label_element = option.query_selector('div.option-label-Fv9c0E')
                if label_element:
                    # 使用 JavaScript 获取第一个文本节点
                    model_text = label_element.evaluate('''el => {
                        // 获取第一个文本节点的内容
                        for (let node of el.childNodes) {
                            if (node.nodeType === Node.TEXT_NODE) {
                                return node.textContent.trim();
                            }
                        }
                        return el.textContent.trim();
                    }''')
                    text_repr = repr(model_text)
                    logger.info(f"  [{i}] {text_repr}")
                        
            # 3. 在弹出的 listbox 中查找并点击目标模型
            # 使用完全精确匹配
            model_option = None
            for option in all_options:
                # 只获取模型名称，不包含描述文字
                label_element = option.query_selector('div.option-label-Fv9c0E')
                if not label_element:
                    continue
                            
                # 使用 JavaScript 获取第一个文本节点
                model_text = label_element.evaluate('''el => {
                    for (let node of el.childNodes) {
                        if (node.nodeType === Node.TEXT_NODE) {
                            return node.textContent.trim();
                        }
                    }
                    return el.textContent.trim();
                }''')
                            
                # 完全精确匹配（字面相等）
                if model_text == model_name:
                    model_option = option
                    logger.info(f"精确匹配到模型选项: {model_text}")
                    break
                        
            if not model_option:
                logger.warning(f"未找到模型选项: {model_name}")
                # 截图调试
                self.page.screenshot(path="debug_model_options.png")
                # 输出所有可用选项
                all_options = self.page.query_selector_all('li[role="option"]')
                logger.info(f"可用模型选项:")
                for option in all_options:
                    text = option.inner_text().strip()
                    logger.info(f"  - {text}")
                # 按 ESC 关闭下拉框
                self.page.keyboard.press('Escape')
                time.sleep(2)
                return
                        
            # 4. 点击目标模型
            logger.info(f"选择模型: {model_name}")
            model_option.click()
            time.sleep(3)
            
            # 5. 按 ESC 关闭下拉框（重要！避免影响后续操作）
            self.page.keyboard.press('Escape')
            time.sleep(2)
                        
            logger.info(f"模型选择完成: {model_name}")
            
        except Exception as e:
            logger.error(f"选择模型失败: {e}")
            # 尝试关闭下拉框
            try:
                self.page.keyboard.press('Escape')
                time.sleep(0.5)
            except:
                pass
    
    def _select_ratio(self, ratio: str):
        """
        选择比例（radio 单选按钮组）
        
        Args:
            ratio: 比例，如 "4:3"
        """
        try:
            # 1. 检查当前比例（底部工具栏显示比例的 button）
            # 模糊匹配包含 toolbar-button 的 button
            all_buttons = self.page.query_selector_all('button[class*="toolbar-button"]')
            logger.info(f"找到 {len(all_buttons)} 个 toolbar-button 按钮")
            
            current_ratio = None
            ratio_button = None
            
            for idx, btn in enumerate(all_buttons):
                text = btn.inner_text()
                logger.info(f"按钮 {idx}: 文本='{text}'")
                
                # 查找包含冒号（比例格式）的按钮
                if ':' in text:
                    logger.info(f"找到比例按钮，文本: {text}")
                    # 提取比例文本
                    import re
                    match = re.search(r'(\d+:\d+)', text)
                    if match:
                        current_ratio = match.group(1)
                    
                    # 如果是第一次找到的比例按钮，记录下来
                    if not ratio_button:
                        ratio_button = btn
                    
                    # 如果文本完全匹配目标比例，优先选择
                    if text.strip() == ratio:
                        ratio_button = btn
                        logger.info(f"精确匹配到比例按钮: {ratio}")
                        break
            
            logger.info(f"当前比例: {current_ratio}，目标比例: {ratio}")
            
            # 如果已经是目标比例，不需要选择
            if current_ratio == ratio:
                logger.info(f"当前比例已经是 {ratio}，无需选择")
                return
            
            if not ratio_button:
                logger.warning(f"未找到比例按钮: {ratio}")
                return
            
            logger.info(f"点击比例按钮...")
            ratio_button.click()
            time.sleep(5)  # 等待弹出比例选择面板
            
            # 2. 在弹出的面板中查找并点击目标比例
            # 比例选项是 label.lv-radio，包含 input[type="radio"][value="比例"]
            # 查找包含指定 value 的 radio input 的父 label
            ratio_label = self.page.query_selector(f'label.lv-radio:has(input[type="radio"][value="{ratio}"])')
            
            if not ratio_label:
                logger.warning(f"未找到比例选项: {ratio}")
                # 按 ESC 关闭面板
                self.page.keyboard.press('Escape')
                time.sleep(0.5)
                return
            
            # 3. 点击 label（会自动选中 radio）
            logger.info(f"选择比例: {ratio}")
            ratio_label.click()
            time.sleep(3)
            
            # 4. 按 ESC 关闭面板
            self.page.keyboard.press('Escape')
            time.sleep(2)
            
            logger.info(f"比例选择完成: {ratio}")
            
        except Exception as e:
            logger.error(f"选择比例失败: {e}")
            try:
                self.page.keyboard.press('Escape')
                time.sleep(0.5)
            except:
                pass
    
    def _select_duration(self, duration: str):
        """
        选择时长（垂直下拉列表）
        
        Args:
            duration: 时长字符串，如 "4s", "5s"
        """
        try:
            # 提取时长数字
            import re
            if isinstance(duration, str):
                match = re.search(r'(\d+)', duration)
                if match:
                    target_duration = int(match.group(1))
                else:
                    logger.warning(f"无法从 '{duration}' 中提取时长数字")
                    return
            else:
                target_duration = int(duration)
            
            # 1. 点击时长按钮（底部工具栏显示时长的 span）
            # 查找所有 lv-select-view-value 元素
            all_spans = self.page.query_selector_all('span.lv-select-view-value')
            
            # 调试：打印所有元素
            logger.info(f"[调试] 找到 {len(all_spans)} 个 span.lv-select-view-value 元素:")
            for idx, span in enumerate(all_spans):
                text = span.inner_text()
                logger.info(f"[调试]   索引[{idx}]: {repr(text)}")
            
            if len(all_spans) == 0:
                logger.warning(f"未找到任何 lv-select-view-value 元素")
                return
            
            # 使用最后一个元素作为时长按钮
            duration_span = all_spans[-1]  # 最后一个元素
            
            # 提取当前时长数字
            text = duration_span.inner_text()
            logger.info(f"[调试] 使用时长按钮（最后一个元素）: {repr(text)}")
            
            match = re.search(r'(\d+)', text)
            if match:
                current_duration = int(match.group(1))
            else:
                logger.warning(f"无法从时长按钮提取数字: {text}")
                return
            
            logger.info(f"当前时长: {current_duration}s，目标时长: {duration}")
            
            # 如果已经是目标时长，不需要选择
            if current_duration == target_duration:
                logger.info(f"当前时长已经是 {duration}，无需选择")
                return
            
            logger.info(f"点击时长按钮...")
            duration_span.click()
            time.sleep(5)  # 等待弹出时长选择列表完全展开
            
            # 2. 在列表中查找目标时长
            # 时长选项垂直排列：4s, 5s, 6s, 7s, 8s, 9s, 10s...
            # 需要根据当前时长和目标时长计算移动次数
            # 当前在 current_duration 的位置，要移动到 target_duration 的位置
            # 4s=索引0, 5s=索引1, 6s=索引2, 以此类推
            
            # 从当前项移动到目标项的步数
            steps = target_duration - current_duration
            
            logger.info(f"需要按 {abs(steps)} 次{'下' if steps > 0 else '上'}箭头选择 {duration}")
            
            if steps > 0:
                # 向下移动
                for i in range(steps):
                    self.page.keyboard.press('ArrowDown')
                    time.sleep(1.5)
                    logger.debug(f"按下箭头 {i+1}/{steps}")
            elif steps < 0:
                # 向上移动
                for i in range(abs(steps)):
                    self.page.keyboard.press('ArrowUp')
                    time.sleep(1.5)
                    logger.debug(f"按上箭头 {i+1}/{abs(steps)}")
            
            # 3. 按回车确认选择
            logger.info(f"按回车确认选择...")
            self.page.keyboard.press('Enter')
            time.sleep(2)
            
            # 4. 按 ESC 确保下拉框关闭（重要！避免影响后续操作）
            self.page.keyboard.press('Escape')
            time.sleep(2)
            
            logger.info(f"时长选择完成: {duration}")
            
        except Exception as e:
            logger.error(f"选择时长失败: {e}")
            try:
                self.page.keyboard.press('Escape')
                time.sleep(0.5)
            except:
                pass
    
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
            time.sleep(5)
            
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
                
                # 选择第 idx+1 张图片
                # 即梦的图片选择器会显示已上传的图片列表（图片1、图片2...）
                # 使用键盘方向键选择对应的图片
                logger.info(f"选择第 {idx+1} 张图片...")
                
                # 第1张图片不需要移动，第2张按1次下箭头，第3张按2次，以此类推
                if idx > 0:
                    for _ in range(idx):
                        self.page.keyboard.press('ArrowDown')
                        time.sleep(1)
                
                # 按回车确认选择
                self.page.keyboard.press('Enter')
                time.sleep(5)
                
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
            
            # 2. 选择模型（即梦使用的是自定义下拉选择器）
            logger.info(f"选择模型: {model}")
            self._select_model(model)
            
            # 3. 选择比例（4:3）
            logger.info(f"选择比例: {ratio}")
            self._select_ratio(ratio)
            time.sleep(3)  # 等待比例选择完成
            
            # 4. 选择时长（如 4s）
            logger.info(f"选择时长: {duration}")
            self._select_duration(duration)
            time.sleep(3)  # 等待时长选择完成
            
        except Exception as e:
            logger.error(f"设置生成参数失败: {e}")
            raise
    
    def _click_generate_and_wait(self, timeout: int = 900, output_dir: str = "output", 
                                  on_history_id_captured=None) -> Optional[Dict]:
        """
        点击生成按钮并等待视频完成
        
        Args:
            timeout: 超时时间（秒）
            output_dir: 视频保存目录
            on_history_id_captured: history_record_id 捕获后的回调函数
            
        Returns:
            {
                "video_url": str,
                "history_record_id": str
            } 或 None
        """
        try:
            # 1. 查找生成按钮（多种选择器尝试）
            generate_button = None
            
            # 尝试1：根据截图中的 class
            generate_button = self.page.query_selector('button.submit-button-s4a7XV')
            if generate_button:
                logger.info("找到生成按钮（submit-button-s4a7XV）")
            
            # 尝试2：查找包含向上箭头图标的按钮
            if not generate_button:
                generate_button = self.page.query_selector('button.lv-btn-primary:has(svg)')
                if generate_button:
                    logger.info("找到生成按钮（lv-btn-primary:has(svg)）")
            
            # 尝试3：查找最后一个 primary 按钮
            if not generate_button:
                all_primary = self.page.query_selector_all('button.lv-btn-primary')
                if all_primary:
                    generate_button = all_primary[-1]
                    logger.info(f"找到生成按钮（最后一个 primary 按钮，共 {len(all_primary)} 个）")
            
            # 尝试4：备用选择器
            if not generate_button:
                generate_button = self.page.query_selector('button:has-text("生成")')
                if generate_button:
                    logger.info("找到生成按钮（包含“生成”文本）")
            
            if not generate_button:
                logger.error("未找到生成按钮")
                # 截图调试
                self.page.screenshot(path="debug_no_button.png")
                raise Exception("未找到生成按钮")
            
            # 2. 检查按钮是否可用
            is_disabled = generate_button.get_attribute('disabled')
            logger.info(f"按钮禁用状态: {is_disabled}")
            
            if is_disabled:
                logger.warning("按钮处于禁用状态，等待 3 秒后重试...")
                time.sleep(3)
            
            # 2. 先设置监听器（在点击之前！）
            history_record_id = None
            video_url = None
            response_count = [0]  # 使用列表来捕获响应
            
            def handle_response(response):
                nonlocal history_record_id, video_url
                url = response.url
                method = response.request.method
                response_count[0] += 1
                
                # 输出所有 POST 请求用于调试
                if method == 'POST':
                    logger.info(f"📡 捕获到 POST 请求 #{response_count[0]}: {url[:100]}...")
                
                # 监听生成请求响应（排除 cancel_generate）
                if 'generate' in url.lower() and 'cancel' not in url.lower() and method == 'POST':
                    logger.info(f"✅ 检测到生成请求: {url[:150]}")
                    try:
                        data = response.json()
                        logger.info(f"✅ 捕获到生成请求响应 (第 {response_count[0]} 个响应)")
                        logger.info(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                        # 提取 history_record_id（修正键名：aigc_data 不是 aigo_data）
                        if data.get('data', {}).get('aigc_data', {}).get('history_record_id'):
                            history_record_id = data['data']['aigc_data']['history_record_id']
                            logger.info(f"✅ 获取到 history_record_id: {history_record_id}")
                            print(f"\n{'='*60}")
                            print(f"🎯 history_record_id: {history_record_id}")
                            print(f"{'='*60}\n")
                            
                            # 立即调用回调函数保存 history_record_id
                            if on_history_id_captured:
                                try:
                                    on_history_id_captured(history_record_id)
                                    logger.info(f"✅ 已通过回调函数保存 history_record_id")
                                except Exception as cb_err:
                                    logger.error(f"回调函数执行失败: {cb_err}")
                        elif data.get('data', {}).get('history_record_id'):
                            history_record_id = data['data']['history_record_id']
                            logger.info(f"✅ 获取到 history_record_id: {history_record_id}")
                            print(f"\n{'='*60}")
                            print(f"🎯 history_record_id: {history_record_id}")
                            print(f"{'='*60}\n")
                            
                            # 立即调用回调函数保存 history_record_id
                            if on_history_id_captured:
                                try:
                                    on_history_id_captured(history_record_id)
                                    logger.info(f"✅ 已通过回调函数保存 history_record_id")
                                except Exception as cb_err:
                                    logger.error(f"回调函数执行失败: {cb_err}")
                        else:
                            logger.warning(f"响应中没有 history_record_id，data keys: {list(data.get('data', {}).keys())}")
                    except Exception as e:
                        logger.warning(f"解析生成响应失败: {e}")
                        # 尝试获取文本内容
                        try:
                            text = response.text()
                            logger.warning(f"响应文本（前200字符）: {text[:200]}")
                        except:
                            pass
                
                # 监听视频 URL
                if '.mp4' in url and 'jimeng' in url:
                    if 'loading' not in url and 'animation' not in url:
                        video_url = url
                        logger.info(f"检测到视频URL: {video_url}")
            
            self.page.on("response", handle_response)
            logger.info("已设置网络监听器")
            
            # 3. 点击生成按钮
            logger.info("点击生成按钮...")
            
            # 尝试直接点击
            try:
                generate_button.click()
                logger.info("直接点击成功")
            except Exception as e:
                logger.warning(f"直接点击失败: {e}，尝试 JavaScript 点击...")
                # 使用 JavaScript 点击
                generate_button.evaluate('button => button.click()')
                logger.info("JavaScript 点击成功")
            
            time.sleep(2)  # 等待点击生效，避免网络延迟
            logger.info("已点击生成按钮，等待视频生成...")
            
            # 4. 等待获取 history_record_id（最多等待 120 秒）
            logger.info("等待获取 history_record_id...")
            start_wait = time.time()
            last_log_time = time.time()
            
            # 使用 page.wait_for_timeout 替代 time.sleep，让事件循环能够处理响应
            while not history_record_id and (time.time() - start_wait) < 120:
                elapsed = int(time.time() - start_wait)
                
                # 每 10 秒输出一次进度
                if time.time() - last_log_time >= 10:
                    logger.info(f"等待中... 已等待 {elapsed} 秒，已捕获 {response_count[0]} 个 POST 请求")
                    last_log_time = time.time()
                
                # 使用 page.wait_for_timeout 让出控制权，让事件循环处理响应
                self.page.wait_for_timeout(1000)  # 1秒
            
            # 再等待 3 秒，确保监听器有足够时间处理响应
            if history_record_id:
                logger.info("获取到 history_record_id，等待 3 秒确保处理完成...")
                self.page.wait_for_timeout(3000)
            else:
                logger.warning("等待超时，再等待 3 秒让监听器处理...")
                self.page.wait_for_timeout(3000)
            
            if not history_record_id:
                logger.error(f"❌ 未获取到 history_record_id（已捕获 {response_count[0]} 个 POST 请求）")
                # 关闭浏览器
                self._close_browser()
                raise Exception("未获取到 history_record_id")
            
            logger.info(f"✅ 成功获取 history_record_id: {history_record_id}")
            
            # 4. 获取 Cookie 并保存
            logger.info("保存浏览器 Cookie...")
            cookies = self.context.cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}
            
            # 保存 Cookie 到文件
            cookie_file = os.path.join(self.user_data_dir, "cookies.json")
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_dict, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Cookie 已保存到: {cookie_file}")
            
            # 5. 关闭浏览器
            logger.info("关闭浏览器...")
            self._close_browser()
            logger.info("✅ 浏览器已关闭")
            
            # 5. 通过 API 轮询任务状态并下载视频
            logger.info(f"开始轮询任务状态: {history_record_id}")
            video_url = self._poll_and_download_video(history_record_id, output_dir=output_dir)
            
            # 返回 video_url 和 history_record_id
            return {
                "video_url": video_url,
                "history_record_id": history_record_id
            }
            
            # 3. 轮询等待视频生成完成
            start_time = time.time()
            last_check_time = 0
            poll_count = 0
            
            while time.time() - start_time < timeout:
                # 每 10 秒检查一次，避免频繁查询
                if time.time() - last_check_time < 10:
                    time.sleep(1)
                    continue
                    
                last_check_time = time.time()
                elapsed = int(time.time() - start_time)
                poll_count += 1
                
                # 优先检查是否已经通过监听获取到视频 URL
                if video_url:
                    logger.info(f"通过网络监听获取到视频 URL")
                    break
                
                # 如果获取到 history_record_id，通过 API 轮询任务状态
                if history_record_id:
                    logger.info(f"等待视频生成中... 已等待 {elapsed} 秒（第 {poll_count} 次轮询）")
                    
                    # 调用 get_history_by_ids 接口查询状态
                    try:
                        task_status = self._poll_task_status(history_record_id)
                        if task_status:
                            status = task_status.get('status')
                            # status=50 表示完成
                            if status == 50:
                                logger.info("任务已完成，尝试获取视频 URL...")
                                video_url = self._extract_video_url_from_history(task_status)
                                if video_url:
                                    logger.info(f"成功获取视频 URL: {video_url}")
                                    break
                            elif status == 30:
                                logger.error(f"任务失败: {task_status.get('fail_msg', 'unknown')}")
                                raise Exception(f"视频生成失败: {task_status.get('fail_msg')}")
                            else:
                                logger.info(f"任务状态: {status}（处理中）")
                    except Exception as e:
                        logger.debug(f"轮询任务状态失败: {e}")
                else:
                    logger.info(f"等待视频生成中... 已等待 {elapsed} 秒（第 {poll_count} 次轮询）")
                    # 等待获取 history_record_id
                    time.sleep(3)
                    continue
                
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
            
            # 2. 从页面中的链接
            video_links = self.page.evaluate("""
                () => {
                    const links = document.querySelectorAll('a[href$=".mp4"]');
                    return Array.from(links).map(link => link.href);
                }
            """)
            
            if video_links and len(video_links) > 0:
                return video_links[0]
            
            return None
            
        except Exception as e:
            logger.error(f"提取视频URL失败: {e}")
            return None
    
    def _poll_and_download_video(self, history_record_id: str, output_dir: str = "output") -> Optional[str]:
        """
        轮询任务状态并下载视频
        
        Args:
            history_record_id: 历史记录 ID
            output_dir: 输出目录
            
        Returns:
            视频本地路径，如果失败返回 None
        """
        try:
            import requests
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"开始轮询任务: {history_record_id}")
            check_interval = 10  # 每 10 秒检查一次
            start_time = time.time()
            poll_count = 0
            last_log_time = time.time()
            
            # 不设置超时限制，一直轮询直到任务完成或失败
            while True:
                poll_count += 1
                elapsed = int(time.time() - start_time)
                
                # 每 60 秒输出一次等待时长提示
                if time.time() - last_log_time >= 60:
                    minutes = elapsed // 60
                    logger.info(f"⏱️ 已等待 {minutes} 分钟，任务仍在处理中...")
                    last_log_time = time.time()
                
                # 调用 API 查询任务状态
                task_status = self._poll_task_status_by_api(history_record_id)
                
                if not task_status:
                    logger.info(f"等待任务开始... ({elapsed}s / 第 {poll_count} 次轮询)")
                    time.sleep(check_interval)
                    continue
                
                status = task_status.get('status')
                
                # status=50: 任务完成
                if status == 50:
                    logger.info(f"✅ 任务已完成！耗时: {elapsed} 秒 ({elapsed//60} 分钟)")
                    
                    # 提取视频 URL（可能返回字典或字符串）
                    video_url = self._extract_video_url_from_history(task_status)
                    if not video_url:
                        logger.error("❌ 未找到视频 URL")
                        logger.debug(f"任务状态数据: {json.dumps(task_status, ensure_ascii=False, indent=2)[:1000]}")
                        return None
                    
                    logger.info(f"✓ 提取到视频 URL")
                    
                    # 如果是字典，打印清晰度信息
                    if isinstance(video_url, dict):
                        logger.info(f"  多清晰度: {list(video_url.keys())}")
                    
                    # 下载视频
                    video_path = self._download_video(video_url, output_dir, history_record_id)
                    return video_path
                
                # status=30: 任务失败
                elif status == 30:
                    fail_msg = task_status.get('fail_msg', 'unknown')
                    fail_code = task_status.get('fail_code', 'unknown')
                    logger.error(f"❌ 任务失败: {fail_msg} ({fail_code})")
                    return None
                
                # 其他状态: 处理中
                else:
                    logger.info(f"⏳ 任务处理中... 状态: {status} ({elapsed}s / 第 {poll_count} 次轮询)")
                    time.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"轮询并下载视频失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _poll_task_status_by_api(self, history_record_id: str) -> Optional[Dict]:
        """
        通过 API 轮询任务状态（使用 requests 库）
        
        Args:
            history_record_id: 历史记录 ID
            
        Returns:
            任务状态数据
        """
        try:
            import requests
            
            # 从 cookie 文件读取 Cookie
            cookie_file = os.path.join(self.user_data_dir, "cookies.json")
            if not os.path.exists(cookie_file):
                logger.error(f"Cookie 文件不存在: {cookie_file}")
                return None
            
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # 构造 Cookie 字符串
            cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            
            # 构造请求
            url = f"https://jimeng.jianying.com/mweb/v1/get_history_by_ids"
            params = {
                "aid": "513695",
                "device_platform": "web",
                "region": "cn",
                "web_id": cookies.get('passport_csrf_token', ''),
            }
            
            headers = {
                "Cookie": cookie_str,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Origin": "https://jimeng.jianying.com",
                "Referer": "https://jimeng.jianying.com/ai-tool/generate?workspace=0&type=video",
            }
            
            data = {
                "history_ids": [history_record_id],
                "image_info": {
                    "width": 2048,
                    "height": 2048,
                    "format": "webp",
                    "image_scene_list": [
                        {"scene": "normal", "width": 2400, "height": 2400, "uniq_key": "2400", "format": "webp"},
                        {"scene": "loss", "width": 1080, "height": 1080, "uniq_key": "1080", "format": "webp"}
                    ]
                }
            }
            
            # 发送请求
            response = requests.post(url, params=params, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # 打印 API 返回结果（调试信息）
            logger.debug(f"[轮询] API返回: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
            
            if result.get('ret') != '0':
                logger.warning(f"[轮询] API 返回错误: ret={result.get('ret')}, errmsg={result.get('errmsg')}")
                return None
            
            # 提取任务数据
            history_data = result.get('data', {}).get(history_record_id, {})
            if not history_data:
                logger.warning(f"[轮询] 未找到 history_id 对应的数据")
                logger.debug(f"[轮询] data keys: {list(result.get('data', {}).keys())}")
                return None
            
            # 打印任务状态信息
            status = history_data.get('status')
            fail_code = history_data.get('fail_code', '')
            logger.debug(f"[轮询] 任务状态: {status}")
            if fail_code:
                logger.debug(f"[轮询] 错误代码: {fail_code}")
            
            # 如果任务完成，打印 item_list 信息
            if status in [30, 50]:
                item_list = history_data.get('item_list', [])
                logger.info(f"[轮询] 任务完成，item_list数量: {len(item_list)}")
                
                if item_list:
                    first_item = item_list[0]
                    logger.debug(f"[轮询] 第一个item的keys: {list(first_item.keys())}")
                    
                    # 打印 video 字段信息
                    if 'video' in first_item:
                        video = first_item['video']
                        logger.debug(f"[轮询] video字段keys: {list(video.keys())}")
                        
                        # 如果有 origin_video 或 transcoded_video，打印详细信息
                        if 'origin_video' in video:
                            origin_video = video['origin_video']
                            if isinstance(origin_video, dict):
                                logger.debug(f"[轮询] origin_video清晰度: {list(origin_video.keys())}")
                        
                        if 'transcoded_video' in video:
                            transcoded_video = video['transcoded_video']
                            if isinstance(transcoded_video, dict):
                                logger.debug(f"[轮询] transcoded_video清晰度: {list(transcoded_video.keys())}")
                    
                    # 打印 common_attr.item_urls
                    if 'common_attr' in first_item:
                        item_urls = first_item['common_attr'].get('item_urls', [])
                        logger.debug(f"[轮询] common_attr.item_urls: {item_urls}")
            
            return history_data
            
        except Exception as e:
            logger.warning(f"[轮询] 轮询任务状态失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _download_video(self, video_url, output_dir: str, history_record_id: str) -> Optional[str]:
        """
        下载视频到本地
        
        Args:
            video_url: 视频 URL（可以是字符串或字典）
            output_dir: 输出目录
            history_record_id: 历史记录 ID
            
        Returns:
            本地视频路径
        """
        try:
            import requests
            
            # 如果video_url是字典（多清晰度），选择最高清晰度
            if isinstance(video_url, dict):
                logger.info(f"检测到多清晰度视频URL，选择最高清晰度")
                final_url = None
                selected_quality = None
                
                for quality in ['origin', '720p', '480p', '360p']:
                    if quality in video_url:
                        video_info = video_url[quality]
                        if isinstance(video_info, dict) and video_info.get('video_url'):
                            final_url = video_info['video_url']
                            selected_quality = quality
                            logger.info(f"  选择清晰度: {quality}")
                            break
                
                if not final_url:
                    logger.error("无法从多清晰度字典中提取视频URL")
                    return None
                
                video_url = final_url
            
            logger.info(f"开始下载视频...")
            
            # 生成文件名
            timestamp = int(time.time())
            filename = f"jimeng_video_{history_record_id}_{timestamp}.mp4"
            filepath = os.path.join(output_dir, filename)
            
            # 流式下载视频
            response = requests.get(video_url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示进度（每10%显示一次）
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            if int(progress) % 10 == 0 and downloaded_size < total_size:
                                logger.info(f"  下载进度: {progress:.1f}% ({downloaded_size}/{total_size} bytes)")
            
            logger.info(f"✅ 视频下载成功: {filepath}")
            logger.info(f"  文件大小: {downloaded_size / 1024 / 1024:.2f} MB")
            print(f"\n{'='*60}")
            print(f"🎉 视频已保存: {filepath}")
            print(f"{'='*60}\n")
            
            return filepath
            
        except Exception as e:
            logger.error(f"下载视频失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _poll_task_status(self, history_record_id: str) -> Optional[Dict]:
        """
        轮询任务状态（调用 get_history_by_ids 接口）
        
        Args:
            history_record_id: 历史记录 ID
            
        Returns:
            任务状态信息
        """
        try:
            # 构造请求
            url = f"{self.base_url}/mweb/v1/get_history_by_ids"
            
            # 使用 page.evaluate 发送请求（复用浏览器的 cookie）
            result = self.page.evaluate("""
                async (historyId) => {
                    const response = await fetch('/mweb/v1/get_history_by_ids?aid=513695&device_platform=web&region=cn', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            history_ids: [historyId],
                            image_info: {
                                width: 2048,
                                height: 2048,
                                format: 'webp',
                                image_scene_list: [
                                    {scene: 'normal', width: 2400, height: 2400, uniq_key: '2400', format: 'webp'},
                                    {scene: 'loss', width: 1080, height: 1080, uniq_key: '1080', format: 'webp'}
                                ]
                            }
                        })
                    });
                    return await response.json();
                }
            """, history_record_id)
            
            if not result or result.get('ret') != '0':
                logger.debug(f"轮询接口返回错误: {result}")
                return None
            
            # 提取任务数据
            history_data = result.get('data', {}).get(history_record_id, {})
            if not history_data:
                return None
            
            return history_data
            
        except Exception as e:
            logger.debug(f"轮询任务状态异常: {e}")
            return None
    
    def _extract_video_url_from_history(self, history_data: Dict) -> Optional[str]:
        """
        从历史数据中提取视频 URL
        
        Args:
            history_data: 任务历史数据
            
        Returns:
            视频 URL（优先返回最高清晰度）
        """
        try:
            # 尝试从多个路径提取视频 URL
            
            # 1. 从 resources 提取
            resources = history_data.get('resources', [])
            for resource in resources:
                if resource.get('type') == 'video':
                    video_info = resource.get('video_info', {})
                    video_url = video_info.get('video_url')
                    if video_url:
                        logger.info("✓ 从 resources 提取视频URL")
                        return video_url
            
            # 2. 从 item_list 提取（主要来源）
            item_list = history_data.get('item_list', [])
            for item in item_list:
                video = item.get('video', {})
                if video:
                    # 尝试 origin_video（原始视频）
                    if video.get('origin_video'):
                        origin_video = video['origin_video']
                        # 如果是字典（多清晰度），选择最高清晰度
                        if isinstance(origin_video, dict):
                            for quality in ['origin', '720p', '480p', '360p']:
                                if quality in origin_video:
                                    video_url = origin_video[quality].get('video_url')
                                    if video_url:
                                        logger.info(f"✓ 从 video.origin_video[{quality}] 提取视频URL")
                                        return video_url
                        else:
                            # 如果是字符串，直接返回
                            logger.info("✓ 从 video.origin_video 提取视频URL")
                            return origin_video
                    
                    # 尝试 transcoded_video（转码后的视频）
                    if video.get('transcoded_video'):
                        transcoded_video = video['transcoded_video']
                        # 如果是字典（多清晰度），选择最高清晰度
                        if isinstance(transcoded_video, dict):
                            for quality in ['origin', '720p', '480p', '360p']:
                                if quality in transcoded_video:
                                    video_url = transcoded_video[quality].get('video_url')
                                    if video_url:
                                        logger.info(f"✓ 从 video.transcoded_video[{quality}] 提取视频URL")
                                        return video_url
                        else:
                            # 如果是字符串，直接返回
                            logger.info("✓ 从 video.transcoded_video 提取视频URL")
                            return transcoded_video
                    
                    # 尝试 play_addr（常见的视频URL字段）
                    if video.get('play_addr'):
                        play_addr = video['play_addr']
                        if isinstance(play_addr, dict) and play_addr.get('url_list'):
                            video_url = play_addr['url_list'][0]
                            if video_url:
                                logger.info("✓ 从 video.play_addr.url_list 提取视频URL")
                                return video_url
                    
                    # 尝试 video_url 字段
                    if video.get('video_url'):
                        video_url = video['video_url']
                        if video_url:
                            logger.info("✓ 从 video.video_url 提取视频URL")
                            return video_url
            
            # 3. 从 common_attr.item_urls 提取
            item_list = history_data.get('item_list', [])
            for item in item_list:
                common_attr = item.get('common_attr', {})
                item_urls = common_attr.get('item_urls', [])
                if item_urls and item_urls[0]:
                    logger.info("✓ 从 common_attr.item_urls 提取视频URL")
                    return item_urls[0]
            
            # 4. 从 aigo_data 提取
            aigo_data = history_data.get('aigo_data', {})
            if aigo_data:
                video_url = aigo_data.get('video_url')
                if video_url:
                    logger.info("✓ 从 aigo_data.video_url 提取视频URL")
                    return video_url
            
            logger.warning("未从历史数据中找到视频 URL")
            logger.debug(f"history_data keys: {list(history_data.keys())}")
            if history_data.get('item_list'):
                first_item = history_data['item_list'][0]
                logger.debug(f"第一个item的keys: {list(first_item.keys())}")
                if first_item.get('video'):
                    logger.debug(f"video字段的keys: {list(first_item['video'].keys())}")
            return None
            
        except Exception as e:
            logger.error(f"提取视频 URL 失败: {e}")
            import traceback
            traceback.print_exc()
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
