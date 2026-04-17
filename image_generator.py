import time
import os
import requests
from playwright.async_api import Page
from typing import List, Optional


class ImageGenerator:
    def __init__(self, page: Page):
        self.page = page
        
    async def enter_agent_mode(self) -> bool:
        """进入Agent模式并切换到图片生成"""
        try:
            # 等待页面稳定
            await self.page.wait_for_timeout(2000)
                
            # 先关闭可能出现的弹框
            print("\n检查并关闭弹框...")
            try:
                # 尝试关闭各种可能的弹框
                close_selectors = [
                    # 弹框右上角的 X 按钮
                    "div[class*='modal'] button",
                    ".ant-modal-close",
                    ".modal-close-btn",
                    "button[aria-label='Close']",
                    "button[aria-label='close']",
                    # 通用关闭按钮
                    "button:has-text('关闭')",
                    "button:has-text('知道了')",
                    "button:has-text('暂不')",
                    "div[class*='close']",
                    "button[class*='close']",
                    ".modal-close",
                ]
                    
                for selector in close_selectors:
                    try:
                        close_btn = await self.page.query_selector(selector)
                        if close_btn and await close_btn.is_visible():
                            await close_btn.click()
                            print(f"✓ 已关闭弹框，使用选择器: {selector}")
                            await self.page.wait_for_timeout(1500)
                            break
                    except:
                        continue
                    
                # 如果上面的方法都不行，尝试按 ESC 键
                try:
                    await self.page.keyboard.press('Escape')
                    print("✓ 已按ESC键关闭弹框")
                    await self.page.wait_for_timeout(1000)
                except:
                    pass
                        
            except:
                print("⚠ 未找到需要关闭的弹框")
                
            # 截图确认
            await self.page.screenshot(path='after_close_popup.png')
                
            # 确保在首页，如果没有则导航回去
            current_url = self.page.url
            if "/generate" in current_url or "/ai-tool/home" not in current_url:
                print("\n检测到不在首页，导航回首页...")
                await self.page.goto("https://jimeng.jianying.com/ai-tool/home", wait_until='domcontentloaded', timeout=30000)
                await self.page.wait_for_timeout(3000)
                await self.page.screenshot(path='back_to_home.png')
                
            # 精确点击底部输入框内的"Agent 模式"下拉按钮
            print("\n查找底部输入框内的 Agent 模式下拉按钮...")
                
            # 先找到输入框容器，然后在其中找 Agent 模式按钮
            try:
                # 方案1：先找到输入框，再找其中的 Agent 模式按钮
                input_container = await self.page.query_selector(
                    "div[class*='input'], div[class*='editor'], div[class*='compose'], textarea"
                )
                    
                if input_container:
                    # 在输入框容器内查找 Agent 模式按钮
                    agent_mode_btn = await input_container.query_selector(
                        "text=Agent 模式"
                    )
                        
                    if not agent_mode_btn:
                        # 尝试更宽的选择器
                        agent_mode_btn = await input_container.query_selector(
                        "div:has-text('Agent'), span:has-text('Agent'), button:has-text('Agent')"
                    )
                else:
                    agent_mode_btn = None
                        
                # 方案2：如果上面没找到，直接查找但要求按钮在页面底部
                if not agent_mode_btn:
                    # 查找所有包含 Agent 模式的元素
                    all_agent_btns = await self.page.query_selector_all("text=Agent 模式")
                        
                    # 选择最后一个（通常在底部输入框）
                    if all_agent_btns and len(all_agent_btns) > 0:
                        agent_mode_btn = all_agent_btns[-1]  # 取最后一个
                        print(f"✓ 找到 {len(all_agent_btns)} 个 Agent 模式按钮，选择最后一个")
                    
                if not agent_mode_btn:
                    raise Exception("未找到 Agent 模式按钮")
                    
                # 滚动到元素
                await agent_mode_btn.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(1000)
                    
                # 点击前截图
                await self.page.screenshot(path='before_click_agent.png')
                    
                # 点击
                await agent_mode_btn.click()
                print("✓ 已点击 Agent 模式按钮")
                await self.page.wait_for_timeout(3000)
                    
                # 截图确认
                await self.page.screenshot(path='after_click_agent_mode.png')
                    
            except Exception as e:
                print(f"✗ 查找 Agent 模式按钮失败: {e}")
                await self.page.screenshot(path='cannot_find_agent_mode.png')
                return False
                
            # 在下拉菜单中选择"图片生成"
            print("\n查找图片生成选项...")
            image_selectors = [
                "text=图片生成",
                "div:has-text('图片生成')",
                "li:has-text('图片生成')",
                "span:has-text('图片生成')",
            ]
                
            image_gen_option = None
            for selector in image_selectors:
                try:
                    image_gen_option = await self.page.wait_for_selector(selector, timeout=5000)
                    if image_gen_option and await image_gen_option.is_visible():
                        print(f"✓ 找到图片生成选项，选择器: {selector}")
                        break
                except:
                    continue
                
            if image_gen_option:
                await image_gen_option.click()
                print("✓ 已选择图片生成")
                await self.page.wait_for_timeout(3000)
                await self.page.screenshot(path='image_gen_selected.png')
                return True
            else:
                print("✗ 未找到图片生成选项")
                return False
                    
        except Exception as e:
            print(f"✗ 切换到图片生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def switch_to_image_generation(self) -> bool:
        """此方法已合并到 enter_agent_mode 中"""
        # 由于 enter_agent_mode 已经完成了切换到图片生成
        # 这个方法保留但不再需要调用
        print("✓ 图片生成模式已在 enter_agent_mode 中切换")
        return True
    
    async def select_image_model(self, model_name: str = "") -> bool:
        """选择图片模型"""
        try:
            if model_name:
                model_selector = await self.page.wait_for_selector(
                    f"div:has-text('{model_name}'), option:has-text('{model_name}')",
                    timeout=5000
                )
            else:
                # 选择默认第一个模型
                model_selector = await self.page.wait_for_selector(
                    "div.model-select, select.model, [class*='model']",
                    timeout=5000
                )
            
            await model_selector.click()
            print(f"✓ 已选择模型: {model_name if model_name else '默认模型'}")
            await self.page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"✗ 未找到模型选择器: {e}")
            return False
    
    async def select_aspect_ratio(self, ratio: str = "1:1") -> bool:
        """选择图片比例"""
        try:
            ratio_btn = await self.page.wait_for_selector(
                f"div:has-text('{ratio}'), button:has-text('{ratio}')",
                timeout=5000
            )
            await ratio_btn.click()
            print(f"✓ 已选择比例: {ratio}")
            await self.page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"✗ 未找到比例选项 {ratio}: {e}")
            return False
    
    async def enter_prompt(self, prompt_text: str) -> bool:
        """输入提示词"""
        try:
            # 查找文本输入框
            prompt_input = await self.page.wait_for_selector(
                "textarea, input[type='text'][placeholder*='提示'], div[contenteditable='true']",
                timeout=10000
            )
            
            # 清空并输入提示词
            await prompt_input.click()
            await prompt_input.fill(prompt_text)
            print(f"✓ 已输入提示词: {prompt_text[:50]}...")
            await self.page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"✗ 未找到提示词输入框: {e}")
            return False
    
    async def upload_images(self, image_paths: List[str]) -> bool:
        """上传图片"""
        try:
            if not isinstance(image_paths, list):
                image_paths = [image_paths]
            
            # 查找文件输入元素
            file_input = await self.page.query_selector("input[type='file']")
            
            if file_input:
                # 直接使用setInputFiles上传
                absolute_paths = [os.path.abspath(path) for path in image_paths]
                await file_input.set_input_files(absolute_paths)
                print(f"✓ 已上传图片: {', '.join(image_paths)}")
                await self.page.wait_for_timeout(2000)
                return True
            else:
                # 尝试点击上传按钮
                upload_btn = await self.page.wait_for_selector(
                    "button:has-text('上传'), div:has-text('选择图片'), div:has-text('上传图片')",
                    timeout=5000
                )
                
                # 监听文件选择对话框
                async with self.page.expect_file_chooser() as fc_info:
                    await upload_btn.click()
                
                file_chooser = await fc_info.value
                absolute_paths = [os.path.abspath(path) for path in image_paths]
                await file_chooser.set_files(absolute_paths)
                print(f"✓ 已上传图片: {', '.join(image_paths)}")
                await self.page.wait_for_timeout(2000)
                return True
                
        except Exception as e:
            print(f"✗ 上传图片失败: {e}")
            return False
    
    async def add_image_reference(self, image_names: List[str]) -> bool:
        """在提示词中添加图片引用 @图片名"""
        try:
            # 查找文本输入框
            prompt_input = await self.page.query_selector(
                "textarea, input[type='text'], div[contenteditable='true']"
            )
            
            if not prompt_input:
                return False
            
            # 将光标移动到末尾
            await prompt_input.click()
            
            # 添加图片引用
            if isinstance(image_names, str):
                image_names = [image_names]
            
            for img_name in image_names:
                # 输入@和图片名
                await prompt_input.press_sequentially(f" @{img_name}")
                await self.page.wait_for_timeout(500)
            
            print(f"✓ 已添加图片引用: {image_names}")
            return True
        except Exception as e:
            print(f"✗ 添加图片引用失败: {e}")
            return False
    
    async def start_generation(self) -> bool:
        """开始生成"""
        try:
            # 查找生成按钮
            generate_btn = await self.page.wait_for_selector(
                "button:has-text('生成'), button:has-text('开始生成'), div:has-text('生成')",
                timeout=10000
            )
            
            await generate_btn.click()
            print("✓ 已开始生成任务")
            await self.page.wait_for_timeout(2000)
            return True
        except Exception as e:
            print(f"✗ 未找到生成按钮: {e}")
            return False
    
    async def wait_for_completion(self, timeout: int = 300) -> bool:
        """等待生成完成"""
        try:
            print("⏳ 等待生成完成...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # 检查是否有生成完成的标识
                completion_indicators = [
                    "div:has-text('生成完成')",
                    "div:has-text('已完成')",
                    "img.result-image",
                    "div.result-image",
                    "div[class*='result'][class*='image']"
                ]
                
                for indicator in completion_indicators:
                    try:
                        element = await self.page.query_selector(indicator)
                        if element and await element.is_visible():
                            print("✓ 生成完成！")
                            return True
                    except Exception:
                        continue
                
                # 检查进度状态
                try:
                    status_element = await self.page.query_selector(
                        "div:has-text('生成中'), div:has-text('处理中')"
                    )
                    if status_element:
                        status_text = await status_element.inner_text()
                        print(f"  当前状态: {status_text}")
                except Exception:
                    pass
                
                await self.page.wait_for_timeout(5000)
            
            print("✗ 生成超时")
            return False
            
        except Exception as e:
            print(f"✗ 等待生成完成时出错: {e}")
            return False
    
    async def save_generated_images(self, save_dir: str = "generated_images") -> bool:
        """保存生成的图片"""
        try:
            # 创建保存目录
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 查找生成的图片
            img_elements = await self.page.query_selector_all("img[src]")
            
            saved_count = 0
            for idx, img_element in enumerate(img_elements):
                try:
                    img_src = await img_element.get_attribute("src")
                    
                    if img_src and ("http" in img_src or "data:" in img_src):
                        # 下载图片
                        if img_src.startswith("data:"):
                            # Base64图片
                            import base64
                            header, encoded = img_src.split(",", 1)
                            image_data = base64.b64decode(encoded)
                            filename = os.path.join(save_dir, f"generated_{idx+1}.png")
                            with open(filename, 'wb') as f:
                                f.write(image_data)
                        else:
                            # URL图片
                            response = requests.get(img_src)
                            if response.status_code == 200:
                                filename = os.path.join(save_dir, f"generated_{idx+1}.jpg")
                                with open(filename, 'wb') as f:
                                    f.write(response.content)
                        print(f"✓ 已保存图片: {filename}")
                        saved_count += 1
                except Exception as e:
                    print(f"✗ 保存图片失败: {e}")
            
            print(f"✓ 共保存 {saved_count} 张图片到 {save_dir}")
            return saved_count > 0
            
        except Exception as e:
            print(f"✗ 保存生成的图片时出错: {e}")
            return False
    
    async def generate_image(self, prompt: str, image_paths: Optional[List[str]] = None, 
                           model_name: str = "", ratio: str = "1:1", 
                           save_dir: str = "generated_images") -> bool:
        """完整的图片生成流程"""
        print("\n=== 开始图片生成流程 ===\n")
        
        # 1. 进入Agent模式
        if not await self.enter_agent_mode():
            return False
        
        # 2. 切换到图片生成
        if not await self.switch_to_image_generation():
            return False
        
        # 3. 选择模型
        if model_name:
            await self.select_image_model(model_name)
        
        # 4. 选择比例
        await self.select_aspect_ratio(ratio)
        
        # 5. 上传图片（如果有）
        if image_paths:
            await self.upload_images(image_paths)
            await self.page.wait_for_timeout(1000)
        
        # 6. 输入提示词
        await self.enter_prompt(prompt)
        
        # 7. 添加图片引用（如果有图片）
        if image_paths:
            image_names = [os.path.basename(path) for path in image_paths]
            await self.add_image_reference(image_names)
        
        # 8. 开始生成
        if not await self.start_generation():
            return False
        
        # 9. 等待生成完成
        if not await self.wait_for_completion():
            return False
        
        # 10. 保存结果
        if not await self.save_generated_images(save_dir):
            return False
        
        print("\n=== 图片生成流程完成 ===\n")
        return True
