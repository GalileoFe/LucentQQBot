import os
import glob

def read_txt_files():
    """
    读取指定目录下所有的.txt文件，并返回它们的文件名（去掉扩展名后的名字）和内容。
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(script_dir, 'presets'))  # 切换到指定目录

    txt_files = glob.glob("*.txt")  # 获取所有.txt文件
    result = {}  # 用于存储每个文件的文件名和内容
    for file in txt_files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            result[file[:-4]] = content
    return result

if __name__ == "__main__":
    result = read_txt_files()
    print(result)

