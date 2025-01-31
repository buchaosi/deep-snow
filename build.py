import PyInstaller.__main__
import os
import shutil
import sys
from PIL import Image

def create_ico_from_png():
    """从PNG创建ICO文件"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        png_path = os.path.join(current_dir, '001.png')
        ico_path = os.path.join(current_dir, 'temp_icon.ico')
        
        if os.path.exists(png_path):
            # 打开PNG图片
            img = Image.open(png_path)
            # 保存为ICO
            img.save(ico_path, format='ICO')
            return ico_path
    except Exception as e:
        print(f"创建图标失败: {str(e)}")
    return None

def clean_previous_build():
    """清理之前的构建文件"""
    dirs_to_clean = ['dist', 'build', 'release']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"已清理 {dir_name} 目录")
            except Exception as e:
                print(f"清理 {dir_name} 失败: {str(e)}")

def create_release():
    """创建发布包"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        source_dir = os.path.join(current_dir, '001')
        
        if not os.path.exists(os.path.join(source_dir, '001.py')):
            print(f"错误: 找不到源文件 {os.path.join(source_dir, '001.py')}")
            return False
        
        # 清理之前的构建
        clean_previous_build()
        
        # 创建临时图标
        ico_path = create_ico_from_png()
        
        # 构建命令
        build_args = [
            os.path.join(source_dir, '001.py'),
            '--name=深雪酱',
            '--windowed',
            '--onefile',
            '--clean',
            '--noconfirm',
            f'--distpath={os.path.join(current_dir, "dist")}',
            f'--workpath={os.path.join(current_dir, "build")}',
            '--noupx',
            '--strip',
            '--noconsole',
        ]
        
        # 如果成功创建了图标，添加图标参数
        if ico_path:
            build_args.append(f'--icon={ico_path}')
        
        # 执行打包
        PyInstaller.__main__.run(build_args)
        
        # 创建发布目录
        release_dir = os.path.join(current_dir, "release")
        if not os.path.exists(release_dir):
            os.makedirs(release_dir)
        
        # 复制可执行文件
        exe_name = "深雪酱.exe"
        exe_path = os.path.join(current_dir, "dist", exe_name)
        if not os.path.exists(exe_path):
            print(f"错误: 找不到生成的exe文件: {exe_path}")
            return False
            
        shutil.copy2(exe_path, os.path.join(release_dir, exe_name))
        
        # 创建配置文件
        empty_json = "{}"
        for json_file in ["key.json", "chat_history.json"]:
            with open(os.path.join(release_dir, json_file), 'w', encoding='utf-8') as f:
                f.write(empty_json)
        
        # 清理临时文件
        if ico_path and os.path.exists(ico_path):
            os.remove(ico_path)
        
        print("打包成功！发布文件在 release 文件夹中。")
        return True
        
    except Exception as e:
        print(f"打包过程出错: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        if create_release():
            print("程序打包完成！")
        else:
            print("程序打包失败！")
            sys.exit(1)
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
        sys.exit(1) 