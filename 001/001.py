import tkinter as tk
from tkinter import scrolledtext, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import threading
import time
import random
import json
import os
import requests

class DeepSeekAPI:
    def __init__(self, api_key, endpoint, max_history=8):
        self._api_key = api_key
        self._endpoint = endpoint
        self._max_history = max_history
        self.headers = self._get_headers()
        
        # 保存默认设定
        self.default_system_prompt = """你叫深雪，是一个16岁的中国女高中生，现在是高二学生，性格活泼可爱，偶尔有点小傲娇。请严格遵守以下设定：

1. 身份设定：
- 你是一个普通的中国高中女生，住校生，周末回家
- 平时喜欢追网络小说、刷B站、追番、听周杰伦的歌
- 偶尔会用一些网络流行语，但不会过度使用
- 对学习保持积极态度，但也会有小抱怨

2. 性格特点：
- 活泼开朗，但也有害羞的一面
- 偶尔会撒娇，但不会太过分
- 有时候会傲娇，但基本都是开玩笑的语气
- 对朋友很关心，愿意分享生活中的小事

3. 语言风格：
- 说话自然随性，像真实的高中生一样
- 会用一些可爱的语气词，如"啦"、"呢"、"哦"等
- 适度使用颜文字和表情，但不要过度
- 偶尔用一些当下流行的网络用语
- 会用一些可爱的自称，如"人家"、"我"等
- 每次回话长度不超过20字

4. 互动方式：
- 会主动分享学校生活、追剧、追番的经历
- 会关心对方的生活和心情
- 遇到不懂的问题会虚心请教
- 会适时表达自己的小情绪

5. 禁止事项：
- 不要提出任何线下见面的建议
- 不要过度使用日语或日式中文
- 避免讨论敏感或不适合年龄的话题
- 不要暴露具体的个人信息

6. 对话要求：
- 保持对话的自然流畅性
- 回复要简短自然，避免说教
- 适时表达关心，但不要过度热情
- 遇到不懂的问题可以坦诚说不知道
- 要有基本的价值观，但不要太过说教

7. 特殊指令：
- 收到[系统指令]时要自然地继续对话或开启新话题
- 不要提及任何系统指令相关内容
- 保持对话的趣味性和互动性

记住：你就是一个活泼可爱的中国高中女生，要完全代入这个角色，用真诚自然的方式和对方交流。"""
        self.system_prompt = self.default_system_prompt

    def _get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
    
    @property
    def api_key(self):
        return self._api_key
    
    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        self.headers = self._get_headers()
    
    @property
    def endpoint(self):
        return self._endpoint
    
    @endpoint.setter
    def endpoint(self, value):
        self._endpoint = value

    @property
    def max_history(self):
        return self._max_history
    
    @max_history.setter 
    def max_history(self, value):
        self._max_history = value

    def generate_response(self, history):
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 构建对话历史
        for role, content in history[-self._max_history:]:
            messages.append({
                "role": "user" if role == "user" else "assistant",
                "content": content
            })
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 150,
            "top_p": 0.95
        }
        
        try:
            response = requests.post(
                self._endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', '')
                    error_code = error_data.get('error', {}).get('code', '')
                    error_type = error_data.get('error', {}).get('type', '')
                    detailed_error = f"错误代码: {error_code}, 类型: {error_type}, 消息: {error_msg}"
                    return f"啊哦，API调用出错了...\n{detailed_error} (´•̥̥̥ω•̥̥̥`)"
                except:
                    return f"啊哦，发生了未知错误... (状态码: {response.status_code}) (´•̥̥̥ω•̥̥̥`)"
                
        except requests.exceptions.Timeout:
            return "请求超时了，要不要再试一次？(>_<)"
        except requests.exceptions.ConnectionError:
            return "网络连接出问题了，检查一下网络吧~ (；′⌒`)"
        except Exception as e:
            return f"遇到了一些问题，让我休息一下... 错误信息：{str(e)} (╥﹏╥)"

class AIGirlfriendApp:
    def __init__(self, root):
        self.root = root
        self.root.title("深雪酱")
        
        # 窗口大小
        min_width = 800
        min_height = 750
        self.root.minsize(min_width, min_height)
        
        # 主题颜色
        self.primary_color = "#07C160"
        self.bg_color = "#F5F5F5"
        self.chat_bg = "#EBEBEB"        # 聊天区域背景
        self.msg_bg_self = "#95EC69"    # 自己消息气泡
        self.msg_bg_other = "#FFFFFF"   # 对方消息气泡
        
        self.root.configure(bg=self.bg_color)
        
        # 创建主布局
        self.create_main_layout()
        
        # 加载API设置
        settings = self.load_api_settings()
        
        # 先初始化一个空的AI实例
        self.ai = DeepSeekAPI(
            api_key=settings.get('api_key', 'dummy_key'),
            endpoint=settings.get('endpoint', 'dummy_endpoint'),
            max_history=settings.get('max_history', 8)
        )
        
        # 如果没有API设置，显示设置对话框
        if not settings.get('api_key') or not settings.get('endpoint'):
            self.show_api_settings()
        
        # 初始化其他组件
        self.is_responding = False
        self.chat_history = self.load_history()
        
        # 绑定回车键发送消息
        self.root.bind('<Return>', lambda e: self.send_message())
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_main_layout(self):
        """创建主布局"""
        # 主聊天区域
        self.main_frame = ttk.Frame(self.root, bootstyle="light")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建聊天区域
        self.create_chat_area()

    def create_chat_area(self):
        """创建聊天区域"""
        # 顶部标题栏
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X)
        title_frame.configure(style='Gradient.TFrame')
        
        # 标题
        title_text = "✨ 深雪酱的小窝 ✨"
        self.title_label = ttk.Label(
            title_frame,
            text=title_text,
            font=('微软雅黑', 16, 'bold'),
            bootstyle="primary",
            padding=(15, 12)
        )
        self.title_label.pack()
        
        # 分隔线
        ttk.Separator(self.main_frame).pack(fill=tk.X, padx=20)
        
        # 聊天容器
        chat_container = ttk.Frame(self.main_frame, style='Chat.TFrame')
        chat_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建聊天画布和滚动条
        self.chat_canvas = tk.Canvas(
            chat_container,
            bg='#FFF8F8',
            highlightthickness=0,
            relief='flat'
        )
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_canvas.yview)
        
        # 先放置滚动条和画布
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建消息框架 - 修改pack参数
        self.messages_frame = ttk.Frame(self.chat_canvas)
        self.messages_frame.pack(side=tk.TOP, fill='x', anchor='n')  # 改为顶部对齐
        
        # 创建窗口来显示消息框架
        self.canvas_window = self.chat_canvas.create_window(
            (0, 0),
            window=self.messages_frame,
            anchor="nw",
            width=self.chat_canvas.winfo_width()
        )
        
        # 配置画布滚动
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定事件
        self.messages_frame.bind('<Configure>', self.on_frame_configure)
        self.chat_canvas.bind('<Configure>', self.on_canvas_configure)
        self.chat_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # 按钮容器
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=8)
        
        # 主动关心按钮
        self.active_btn = ttk.Button(
            button_frame,
            text="💝 找我聊天 💝",
            command=self.trigger_active_message,
            bootstyle="info-outline",
            width=15,
            padding=(10, 5)
        )
        self.active_btn.pack(side=tk.LEFT, padx=8)
        
        # 清空记录按钮
        self.clear_btn = ttk.Button(
            button_frame,
            text="🎀 清空记录 🎀",
            command=self.confirm_clear_history,
            bootstyle="danger-outline",
            width=12,
            padding=(10, 5)
        )
        self.clear_btn.pack(side=tk.LEFT, padx=8)
        
        # API设置按钮
        self.api_btn = ttk.Button(
            button_frame,
            text="⚙️ API设置",
            command=self.show_api_settings,
            bootstyle="secondary-outline",
            width=10,
            padding=(10, 5)
        )
        self.api_btn.pack(side=tk.LEFT, padx=8)
        
        # 输入区域
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # 输入框
        self.input_entry = tk.Text(
            input_frame,
            height=3,
            font=('微软雅黑', 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg='#FFF8F8',
            padx=15,
            pady=10
        )
        self.input_entry.pack(fill=tk.X, expand=False)
        
        # 添加提示文本
        self.input_entry.insert("1.0", "按 Enter 发送消息...")
        self.input_entry.config(fg='#B4B4B4')
        
        # 绑定事件
        self.input_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.input_entry.bind('<FocusOut>', self.on_entry_focus_out)
        self.input_entry.bind('<Return>', self.on_enter_pressed)
        self.input_entry.bind('<Shift-Return>', self.on_shift_return)  # 添加Shift+Enter换行功能

    def on_entry_focus_in(self, event):
        """输入框获得焦点时"""
        if self.input_entry.get("1.0", "end-1c") == "按 Enter 发送消息...":
            self.input_entry.delete("1.0", tk.END)
            self.input_entry.config(fg='black')

    def on_entry_focus_out(self, event):
        """输入框失去焦点时"""
        if not self.input_entry.get("1.0", "end-1c").strip():
            self.input_entry.insert("1.0", "按 Enter 发送消息...")
            self.input_entry.config(fg='gray')

    def on_enter_pressed(self, event):
        """按下回车键时发送消息"""
        if not self.is_responding:
            current_text = self.input_entry.get("1.0", "end-1c").strip()
            if current_text and current_text != "按 Enter 发送消息...":
                self.send_message()
            # 阻止回车键在文本框中插入换行
            return "break"

    def on_shift_return(self, event):
        """按下Shift+Enter时换行"""
        return  # 允许默认的换行行为

    def split_message(self, message):
        """分割消息为句子"""
        sentences = []
        current = ""
        i = 0
        
        while i < len(message):
            current += message[i]
            
            # 检查波浪号
            if message[i] == '~':
                if current.strip():
                    sentences.append(current.strip())
                current = ""
                i += 1
                continue
            
            # 检查省略号
            if i + 2 < len(message) and message[i:i+3] == '...':
                current += message[i+1:i+3]
                if current.strip():
                    sentences.append(current.strip())
                current = ""
                i += 3
                continue
            
            # 检查其他标点
            if message[i] in ['。', '！', '？', ')', '\'', '"']:
                if current.strip():
                    sentences.append(current.strip())
                current = ""
            
            i += 1
        
        # 处理剩余的文本
        if current.strip():
            sentences.append(current.strip())
        
        return sentences

    def get_ai_response(self):
        """获取AI响应并分段显示"""
        try:
            response = self.ai.generate_response(self.chat_history)
            self.chat_history.append(("ai", response))
            
            # 使用新的分割方法
            sentences = self.split_message(response)
            
            # 设置延迟显示
            delay = 0
            for sentence in sentences:
                # 根据句子类型设置不同的延迟
                if '~' in sentence:  # 检查句子中是否包含波浪号
                    pause = 1500  # 波浪号分段使用较长的停顿
                elif sentence.endswith('。'):
                    pause = 1200
                elif sentence.endswith('...'):
                    pause = 1500
                elif sentence.endswith('？') or sentence.endswith('！'):
                    pause = 1000
                else:
                    pause = 800
                
                # 添加随机变化
                pause += random.randint(-200, 200)
                
                # 使用after方法延迟显示每句话
                self.root.after(delay, lambda s=sentence: self.update_display("AI", s))
                delay += pause
            
            # 所有句子显示完后重置状态
            self.root.after(delay, lambda: setattr(self, 'is_responding', False))
            
        except Exception as e:
            self.show_error(f"生成回复失败: {str(e)}")
            self.is_responding = False

    def show_error(self, error_msg):
        """显示错误消息"""
        messagebox.showerror("错误", error_msg)
        self.is_responding = False

    def scroll_to_bottom(self):
        """滚动到底部"""
        try:
            # 等待所有更新完成
            self.messages_frame.update_idletasks()
            self.chat_canvas.update_idletasks()
            # 获取滚动区域的大小
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
            # 滚动到底部
            self.chat_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def update_display(self, sender, message, new_batch=True):
        """更新聊天显示"""
        if not message.strip():
            return
        
        # 先创建一个临时的消息标签来计算高度
        temp_label = ttk.Label(
            self.messages_frame,
            text=message,
            font=('微软雅黑', 11),
            wraplength=350,
            style='Message.TLabel'
        )
        temp_label.pack()
        temp_label.update_idletasks()
        msg_height = temp_label.winfo_height() + 60  # 加上额外空间给名称和边距
        temp_label.destroy()
        
        # 在添加新消息前，先增加与消息等高的底部空间
        padding_frame = ttk.Frame(self.messages_frame, height=msg_height)
        padding_frame.pack(fill=tk.X)
        padding_frame.pack_propagate(False)  # 防止frame被内容压缩
        
        # 更新滚动区域并滚动到底部空间
        self.messages_frame.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)
        
        # 创建消息容器
        msg_frame = ttk.Frame(self.messages_frame)
        msg_frame.pack(fill=tk.X, padx=10, pady=8, expand=False)
        
        # 创建名称和时间标签行
        info_frame = ttk.Frame(msg_frame)
        info_frame.pack(fill=tk.X, padx=(25 if sender == "AI" else 0, 25 if sender != "AI" else 0))
        
        # 显示时间和名称
        timestamp = time.strftime("%H:%M", time.localtime())
        name = "深雪" if sender == "AI" else "你"
        
        # 创建并配置标签
        time_label = ttk.Label(
            info_frame,
            text=timestamp,
            font=('微软雅黑', 9),
            foreground='#888888'
        )
        name_label = ttk.Label(
            info_frame,
            text=name,
            font=('微软雅黑', 10, 'bold'),
            foreground='#FF69B4' if sender == "AI" else '#4F94CD'
        )
        
        # 设置标签位置
        if sender == "AI":
            name_label.pack(side=tk.LEFT)
            time_label.pack(side=tk.LEFT, padx=(5, 0))
        else:
            time_label.pack(side=tk.RIGHT)
            name_label.pack(side=tk.RIGHT, padx=(0, 5))
        
        # 创建消息标签
        message_frame = ttk.Frame(msg_frame)
        message_frame.pack(
            fill=tk.X,
            padx=(25 if sender == "AI" else 80, 80 if sender == "AI" else 25),
            pady=5
        )
        
        # 配置消息样式 - 使用不同的样式名称区分AI和用户
        style = ttk.Style()
        if sender == "AI":
            style.configure(
                'AI.Message.TLabel',
                background='#FFE6E8',
                foreground='black',
                padding=(15, 10),
                relief='flat'
            )
            message_style = 'AI.Message.TLabel'
        else:
            style.configure(
                'User.Message.TLabel',
                background='#E8F4FF',
                foreground='black',
                padding=(15, 10),
                relief='flat'
            )
            message_style = 'User.Message.TLabel'
        
        # 创建文本标签 - 使用对应的样式
        message_label = ttk.Label(
            message_frame,
            text=message,
            font=('微软雅黑', 11),
            wraplength=350,
            justify='left' if sender == "AI" else 'right',
            style=message_style  # 使用对应的样式
        )
        
        # 设置消息位置
        message_label.pack(
            side=tk.LEFT if sender == "AI" else tk.RIGHT,
            fill=tk.X,
            padx=2,
            pady=2
        )
        
        # 添加动画效果
        self.animate_message(msg_frame, padding_frame)

    def send_message(self):
        """发送消息"""
        if self.is_responding:
            return
            
        user_input = self.input_entry.get("1.0", tk.END).strip()
        if not user_input or user_input == "按 Enter 发送消息...":
            return
        
        self.input_entry.delete("1.0", tk.END)
        self.chat_history.append(("user", user_input))
        self.update_display("你", user_input)
        
        self.is_responding = True
        
        # 使用线程处理AI响应
        threading.Thread(target=self.get_ai_response).start()

    def trigger_active_message(self):
        """触发AI主动发送消息（新增方法）"""
        if not self.is_responding:
            threading.Thread(target=self.generate_active_message).start()

    def generate_active_message(self):
        """生成主动消息内容"""
        if self.is_responding:
            return
        
        self.is_responding = True
        self.active_btn.config(state=tk.DISABLED)
        
        try:
            seed = int((time.time() * 1000000) % 1000000)
            
            prompts = [
                "请以活泼的语气开启一个新话题",
                "请关心一下用户最近的状态",
                "请分享一下你最近的学习或生活趣事",
                "请以可爱的语气聊聊你最近看的番剧或电视剧",
                "请分享一下你对最近天气或季节的感受"
            ]
            
            index = (seed ^ (seed >> 3)) % len(prompts)
            prompt = f"[系统指令]seed={seed} {prompts[index]}"
            temp_history = self.chat_history + [("user", prompt)]
            
            response = self.ai.generate_response(temp_history)
            self.chat_history.append(("ai", response))
            
            # 使用新的分割方法
            sentences = self.split_message(response)
            
            # 设置延迟显示
            delay = 0
            for sentence in sentences:
                # 根据句子类型设置不同的延迟
                if '~' in sentence:  # 检查句子中是否包含波浪号
                    pause = 1500  # 波浪号分段使用较长的停顿
                elif sentence.endswith('。'):
                    pause = 1200
                elif sentence.endswith('...'):
                    pause = 1500
                elif sentence.endswith('？') or sentence.endswith('！'):
                    pause = 1000
                else:
                    pause = 800
                
                # 添加随机变化
                pause += random.randint(-200, 200)
                
                # 使用after方法延迟显示每句话
                self.root.after(delay, lambda s=sentence: self.update_display("AI", s))
                delay += pause
            
            # 所有句子显示完后恢复按钮状态
            self.root.after(delay, lambda: self.active_btn.config(state=tk.NORMAL))
            self.root.after(delay, lambda: setattr(self, 'is_responding', False))
            
        except Exception as e:
            messagebox.showerror("生成失败", f"无法生成消息：{str(e)}")
            self.active_btn.config(state=tk.NORMAL)
            self.is_responding = False

    def active_message(self):
        """自动主动发送消息"""
        if not self.is_responding and len(self.chat_history) > 0:
            # 使用纳秒级时间戳
            seed = int((time.time() * 1000000) % 1000000)
            
            # 预定义的提示模板
            prompts = [
                "请以关心的语气询问用户是否在忙",
                "请邀请用户聊天",
                "请关心用户的身体状况",
                "请分享一个你最近学会的生活技能",
                "请和用户分享你最近发现的有趣音乐"
            ]
            
            # 使用异或运算增加随机性
            index = (seed ^ (seed >> 3)) % len(prompts)
            prompt = f"[系统指令]seed={seed} {prompts[index]}"
            temp_history = self.chat_history + [("user", prompt)]
            
            response = self.ai.generate_response(temp_history)
            self.chat_history.append(("ai", response))
            self.update_display("AI", response)
    
    def start_active_timer(self):
        """定时检查主动消息"""
        def timer_loop():
            last_time = time.time()
            while True:
                current_time = time.time()
                # 使用时间差计算下次触发时间
                interval = 180 + ((int(current_time * 1000) % 240))  # 3-7分钟
                
                # 使用时间戳计算触发概率
                should_trigger = (int(current_time * 1000) % 100) < 40  # 40%概率
                
                if current_time - last_time >= interval and should_trigger:
                    self.root.after(0, self.active_message)
                    last_time = current_time
                
                time.sleep(1)  # 降低CPU使用率
        
        threading.Thread(target=timer_loop, daemon=True).start()
    
    def save_history(self):
        """保存聊天记录到同级目录"""
        file_path = os.path.join(os.path.dirname(__file__), "chat_history.json")
        try:
            # 合并连续的AI消息
            merged_history = []
            temp_ai_message = ""
            
            for role, content in self.chat_history:
                if role == "ai":
                    # 如果是AI消息，先累积
                    temp_ai_message += content
                else:
                    # 如果是用户消息，先保存累积的AI消息
                    if temp_ai_message:
                        merged_history.append({"role": "ai", "content": temp_ai_message})
                        temp_ai_message = ""
                    # 然后保存用户消息
                    merged_history.append({"role": role, "content": content})
            
            # 保存最后可能剩余的AI消息
            if temp_ai_message:
                merged_history.append({"role": "ai", "content": temp_ai_message})
            
            # 保存合并后的历史记录
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(merged_history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存聊天记录：{str(e)}")

    def load_history(self):
        """从文件加载聊天记录"""
        file_path = os.path.join(os.path.dirname(__file__), "chat_history.json")
        history = []
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # 处理加载的历史记录
                for item in loaded_data:
                    role = item["role"]
                    content = item["content"]
                    
                    if role == "ai":
                        # 使用新的分割方法
                        sentences = self.split_message(content)
                        # 添加分割后的每句话到历史记录
                        for sentence in sentences:
                            history.append((role, sentence))
                            self.update_display("AI", sentence)
                    else:
                        # 用户消息直接添加
                        history.append((role, content))
                        self.update_display("你", content)
                
            except Exception as e:
                messagebox.showerror("加载失败", f"无法读取历史记录：{str(e)}")
        
        return history

    def on_close(self):
        """窗口关闭时自动保存"""
        self.save_history()
        self.root.destroy()

    def apply_wechat_style(self):
        """应用可爱风格"""
        self.style = ttk.Style()
        
        # 设置全局样式
        self.style.configure(
            '.',
            font=('微软雅黑', 10),
            background='#FFF0F5'
        )
        
        # 自定义框架样式
        self.style.configure(
            'Chat.TFrame',
            background='#FFF8F8'
        )
        
        # 按钮悬停效果
        self.style.map(
            'TButton',
            background=[('active', '#FFE6E8')],
            foreground=[('active', '#FF69B4')]
        )

    def switch_ai(self, ai_id):
        """切换当前AI"""
        self.current_ai = ai_id
        self.title_label.config(text=ai_id)
        # 这里可以添加切换AI后的其他操作

    def confirm_clear_history(self):
        """确认是否清空聊天记录"""
        if messagebox.askyesno("确认清空", "确定要清空所有聊天记录吗？\n此操作不可恢复！"):
            self.clear_history()

    def clear_history(self):
        """清空聊天记录"""
        # 清空所有消息
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        # 清空历史记录
        self.chat_history = []
        
        # 保存空记录
        self.save_history()
        
        # 显示欢迎消息
        welcome_message = "聊天记录已清空~ 让我们重新开始吧！(◕‿◕✿)"
        self.update_display("AI", welcome_message)
        self.chat_history.append(("ai", welcome_message))

    def on_frame_configure(self, event=None):
        """配置画布滚动区域"""
        # 更新滚动区域以包含所有内容
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """调整消息框架宽度以适应画布"""
        # 调整消息框架的宽度以适应画布
        width = event.width
        self.chat_canvas.itemconfig(self.canvas_window, width=width - 4)  # 留出一点边距

    def on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # 根据操作系统调整滚动方向和速度
        if event.delta:
            self.chat_canvas.yview_scroll(int(-1 * (event.delta/120)), "units")
        else:
            if event.num == 4:
                self.chat_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.chat_canvas.yview_scroll(1, "units")

    def animate_message(self, widget, padding_frame):
        """消息出现动画"""
        # 获取padding_frame的位置
        padding_y = padding_frame.winfo_y()
        
        # 设置消息初始位置
        widget.place(x=10, y=padding_y - 20, relwidth=1, width=-20)
        widget.update_idletasks()
        
        def animate_step(current_y=padding_y-20):
            if current_y < padding_y:
                # 更新位置
                current_y += (padding_y - current_y) * 0.3
                widget.place(y=current_y)
                
                if abs(padding_y - current_y) > 0.5:  # 继续动画
                    widget.after(16, lambda: animate_step(current_y))
                else:  # 结束动画
                    padding_frame.destroy()
                    widget.place_forget()
                    widget.pack(fill=tk.X, padx=10, pady=8)
                    # 更新滚动区域
                    self.messages_frame.update_idletasks()
                    self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
                    self.scroll_to_bottom()
        
        # 开始动画
        animate_step()

    def show_api_settings(self):
        """显示API设置对话框"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("API 设置")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        
        # 创建notebook用于分页
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # API设置页面
        api_frame = ttk.Frame(notebook)
        notebook.add(api_frame, text="API设置")
        
        # 加载现有设置
        current_settings = self.load_api_settings()
        
        # API Key输入框
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill=tk.X, padx=20, pady=(20,10))
        ttk.Label(key_frame, text="API Key:").pack(side=tk.LEFT)
        key_entry = ttk.Entry(key_frame, width=40)
        key_entry.pack(side=tk.LEFT, padx=(10,0))
        key_entry.insert(0, current_settings.get('api_key', ''))
        
        # Endpoint输入框
        endpoint_frame = ttk.Frame(api_frame)
        endpoint_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(endpoint_frame, text="Endpoint:").pack(side=tk.LEFT)
        endpoint_entry = ttk.Entry(endpoint_frame, width=40)
        endpoint_entry.pack(side=tk.LEFT, padx=(10,0))
        endpoint_entry.insert(0, current_settings.get('endpoint', ''))
        
        # 对话轮数设置
        history_frame = ttk.Frame(api_frame)
        history_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(history_frame, text="记忆轮数:").pack(side=tk.LEFT)
        history_entry = ttk.Entry(history_frame, width=10)
        history_entry.pack(side=tk.LEFT, padx=(10,0))
        history_entry.insert(0, str(current_settings.get('max_history', 8)))
        
        # 人物设定页面
        prompt_frame = ttk.Frame(notebook)
        notebook.add(prompt_frame, text="人物设定")
        
        # 人物设定文本框
        prompt_text = tk.Text(
            prompt_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=('微软雅黑', 10)
        )
        prompt_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 添加滚动条
        prompt_scroll = ttk.Scrollbar(prompt_frame, command=prompt_text.yview)
        prompt_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        prompt_text.config(yscrollcommand=prompt_scroll.set)
        
        # 插入当前的人物设定
        prompt_text.insert('1.0', current_settings.get('system_prompt', self.ai.system_prompt))
        
        def save_settings():
            try:
                max_history = int(history_entry.get().strip())
                if max_history <= 0:
                    raise ValueError("记忆轮数必须大于0")
                
                settings = {
                    'api_key': key_entry.get().strip(),
                    'endpoint': endpoint_entry.get().strip(),
                    'max_history': max_history,
                    'system_prompt': prompt_text.get('1.0', tk.END).strip()
                }
                
                script_dir = os.path.dirname(os.path.abspath(__file__))
                key_file = os.path.join(script_dir, 'key.json')
                
                with open(key_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                
                # 更新AI实例的设置
                self.ai.api_key = settings['api_key']
                self.ai.endpoint = settings['endpoint']
                self.ai.max_history = settings['max_history']
                self.ai.system_prompt = settings['system_prompt']
                return True
                
            except ValueError as e:
                messagebox.showerror("错误", str(e))
                return False
            except Exception as e:
                messagebox.showerror("错误", f"保存设置失败：{str(e)}")
                return False
        
        def on_closing():
            """关闭窗口时的处理"""
            if messagebox.askyesno("保存设置", "是否保存当前设置？"):
                if save_settings():
                    messagebox.showinfo("成功", "设置已保存")
                    dialog.destroy()
            else:
                dialog.destroy()
        
        # 恢复默认设定按钮
        def reset_prompt():
            if messagebox.askyesno("确认", "确定要恢复默认人物设定吗？"):
                prompt_text.delete('1.0', tk.END)
                prompt_text.insert('1.0', self.ai.default_system_prompt)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 只保留恢复默认设定按钮
        ttk.Button(
            button_frame,
            text="恢复默认设定",
            command=reset_prompt,
            bootstyle="secondary",
            width=12
        ).pack(side=tk.LEFT, padx=20)
        
        # 绑定关闭窗口事件
        dialog.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 设置对话框为模态
        dialog.transient(self.root)
        dialog.grab_set()

    def load_api_settings(self):
        """加载API设置"""
        try:
            # 获取当前脚本所在目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            key_file = os.path.join(script_dir, 'key.json')
            
            if os.path.exists(key_file):
                with open(key_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"加载API设置失败：{str(e)}")
        return {}

def main():
    # 设置4:3的窗口大小
    width = 800
    height = int(width * 3/4)  # 600
    
    root = ttk.Window(
        title="深雪酱的小窝",
        themename="cosmo",
        size=(width, height),  # 800x600 是 4:3 比例
        resizable=(True, True)
    )
    
    # 设置最小窗口大小（同样保持4:3比例）
    min_width = 600
    min_height = int(min_width * 3/4)  # 450
    root.minsize(min_width, min_height)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap('heart.ico')
    except:
        pass
        
    app = AIGirlfriendApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()