import gradio as gr
import os
import requests
import tarfile
import subprocess
import shutil
import zipfile

# ディレクトリパス
download_xz_folder = 'download_xz'
download_exe_folder = 'download_exe'
output_folder = 'output'
blender_executable = './blender'
render_script = 'render.py'

# ディレクトリ内のフォルダリストを取得する関数
def get_folder():
    return [d for d in os.listdir(download_exe_folder) if os.path.isdir(os.path.join(download_exe_folder, d))]

def update_folders():
    return gr.Dropdown(choices=get_folder(), interactive=True)

# 選択されたフォルダを使用してBlenderの実行ファイルパスを更新する関数
def update_blender_executable(selected_folder):
    global blender_executable
    blender_executable = os.path.join(download_exe_folder, selected_folder, "blender")
    print(f"Blender executable set to: {blender_executable}")
    return f"Blender executable set to: {blender_executable}"

def process_blend_files(file_path, start, end):
    command = [
        blender_executable,
        "-b",
        "-noaudio",
        "-P",
        render_script,
        "--",
        file_path,
        str(start),
        str(end),
        str(0)
    ]
    subprocess.run(command)

def process_file(file, start, end):
    process_blend_files(file.name, start, end)

def clear_output_folder(folder):
    for root, dirs, files in os.walk(folder):
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

def download_and_extract(url):
    status_message = "Starting download..."
    try:
        filename = url.split("/")[-1]
        download_path = os.path.join(download_xz_folder, filename)
        extract_folder = os.path.join(download_exe_folder, filename.split('.tar.xz')[0])

        # Create directories if they do not exist
        os.makedirs(download_xz_folder, exist_ok=True)
        os.makedirs(download_exe_folder, exist_ok=True)

        # Download the file
        response = requests.get(url, stream=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        status_message = f"Downloaded {filename}. Extracting..."

        # Extract the file
        with tarfile.open(download_path, 'r:xz') as tar:
            # Get the top-level directory name in the tar archive
            top_level_dir = tar.getnames()[0].split('/')[0]
            for member in tar.getmembers():
                # Remove the top-level directory from the member name
                member.name = os.path.relpath(member.name, top_level_dir)
                tar.extract(member, extract_folder)

        status_message = f"Extraction complete. {extract_folder}"

    except Exception as e:
        status_message = f"Error: {e}"

    return status_message

# Create Gradio interface
def create_interface():
    css = """
    <style>
        #update-button {
            margin: 2.5em 0em 0em 0;
            max-width: 2.5em;
            min-width: 2.5em !important;
            height: 2.4em;
        }
    </style>
    """

    with gr.Blocks() as demo:
        gr.HTML(css)  # Add custom CSS

        gr.Markdown("## Blender Rendering Web UI for Vast.ai")

        # Tabbed interface
        with gr.Tabs():
            with gr.TabItem("Rendering"):
                with gr.Row():
                    dropdown = gr.Dropdown(label="Select Version", choices=get_folder(), interactive=True)
                    update_button = gr.Button("🔄", elem_id="update-button")

                file_input = gr.File(label="Upload File")
                start_input = gr.Number(label="Start Frame", value=0)
                end_input = gr.Number(label="End Frame", value=1)
                submit_button = gr.Button("Start Rendering")
                zip_output = gr.File(label="Download Output File")

                def handle_file(file, start, end):
                    clear_output_folder(output_folder)
                    process_file(file, start, end)
                    zip_path = zip_output_folder(output_folder)
                    return zip_path

                submit_button.click(fn=handle_file, inputs=[file_input, start_input, end_input], outputs=zip_output)
                update_button.click(fn=update_folders, outputs=dropdown)
                dropdown.change(fn=update_blender_executable, inputs=dropdown, outputs=None)

            with gr.TabItem("Other Version"):
                url_input = gr.Textbox(label="Enter URL (*-linux-x64.tar.xz)")
                download_button = gr.Button("Download")
                status_message = gr.Textbox(label="Status", value="", lines=3)

                download_button.click(fn=download_and_extract, inputs=url_input, outputs=status_message)

    return demo

# Launch the application
if __name__ == "__main__":
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(download_xz_folder):
        os.makedirs(download_xz_folder)
    if not os.path.exists(download_exe_folder):
        os.makedirs(download_exe_folder)
    demo = create_interface()
    demo.launch(show_api=False, server_name="0.0.0.0")
