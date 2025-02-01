## 深雪酱的小窝 - AI聊天应用
![001](https://github.com/user-attachments/assets/38520797-f51e-44e1-89c2-4877d337ba56)
### 简介
深雪酱的小窝是一款基于AI的虚拟聊天应用，模拟了一个活泼可爱的中国高中女生“深雪”。通过与用户自然流畅的对话，深雪可以分享生活趣事、关心用户心情，并提供轻松愉快的互动体验。
(注：本项目由AI制作，本人只进行调试）：前期由deepseek生成主体框架并写出基础功能，后期用Cursor进行细化
### 已知问题

1.构建出的exe无法读写json文件（随缘修复）

### 功能特性
1. **自然对话**  
   深雪能够以活泼可爱的语气与用户进行自然流畅的对话，支持简短回复和情感表达。
   
2. **主动聊天**  
   应用会在适当的时间主动发起聊天，关心用户的状态或分享生活中的小故事。

3. **个性化设定**  
   用户可以通过API设置界面自定义人物设定，调整深雪的性格、语言风格等。

4. **历史记录保存**  
   聊天记录会自动保存，下次启动时可继续之前的对话。

5. **错误处理**  
   当API调用失败或网络异常时，应用会友好地提示用户并尝试恢复。

6. **可爱UI设计**  
   界面采用可爱风格的配色和布局，提供舒适的视觉体验。

### API设置

默认使用deepseek的API (目前也只能用deepseek）

api_key:填写你的key

Endpoint:建议填写https://api.deepseek.com/v1/chat/completions

### 构建方法

#### 构建
- 运行build.py
- 构建结果生成在同目录的release内

#### 依赖
在运行脚本之前，请确保已安装以下Python库：
- `tkinter`（通常内置在Python中）
- `ttkbootstrap`
- `Pillow`
- `requests`
- `PyInstaller`

可以通过以下命令安装所需的第三方库：
```bash
pip install ttkbootstrap Pillow requests PyInstaller

