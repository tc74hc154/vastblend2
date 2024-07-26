import os
import shutil
import sys
import subprocess
import pandas as pd
import gradio as gr
import zipfile


# スクリプト自身のパスを取得
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
# カレントディレクトリをスクリプトのディレクトリに変更
os.chdir(script_dir)

# 設定
output_folder = 'output'
blender_executable = './blender'  # Blender実行ファイルのパスを設定
render_script = 'render.py'
i = 0
sleep_time = 1  # 秒



def process_blend_files(file_path, start, end):
    # コマンドの構築
    command = [
        blender_executable,
        "-b",
        "-noaudio",
        "-P",
        render_script,
        "--",
        file_path,  # input フォルダ内のファイルのフルパス
        str(start),
        str(end),
        str(i)
    ]
    
    # コマンドの実行
    subprocess.run(command)

def process_file(file, start, end):
    # Blenderファイルの処理を呼び出し
    process_blend_files(file.name, start, end)

def clear_output_folder(output_folder):
    # 出力フォルダを空にする
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))

def zip_output_folder(output_folder):
    zip_filename = 'output.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_folder))
    return zip_filename

# Gradioのインターフェースを作成
with gr.Blocks() as demo:
    gr.Markdown("## ファイルアップロード UI")

    # UIコンポーネント
    file_input = gr.File(label="ファイルをアップロード")
    start_input = gr.Number(label="開始フレーム", value=0)
    end_input = gr.Number(label="終了フレーム", value=1)
    submit_button = gr.Button("Submit")
    zip_output = gr.File(label="出力ファイルのダウンロード")

    # 処理関数
    def handle_file(file, start, end):
        # 出力フォルダを空にする
        clear_output_folder(output_folder)
        
        # Blenderファイルの処理
        process_file(file, start, end)
        
        # ZIPファイルを作成
        zip_path = zip_output_folder(output_folder)
        return zip_path

    # ボタンのアクションを定義
    submit_button.click(fn=handle_file, inputs=[file_input, start_input, end_input], outputs=zip_output)

# アプリケーションを起動
if __name__ == "__main__":
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    demo.launch(show_api=False, server_name="0.0.0.0")
