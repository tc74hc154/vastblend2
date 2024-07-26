import bpy
import sys

blend_filepath = sys.argv[-4]
start = int(sys.argv[-3])
end = int(sys.argv[-2])
select_dev = int(sys.argv[-1])
# 出力ファイルの保存パスを設定します
output_path = "/blender/output/"

print(f"From {start} To {end} useing GPU {select_dev}")

# CUDAを使用するように設定
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = "OPTIX"

cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
cycles_prefs.refresh_devices()

# 利用するデバイスをすべてOFFに初期設定
for device in cycles_prefs.devices:
    device.use = False

i = 0
for device in cycles_prefs.devices:
    if device.type == 'OPTIX':
        if i == select_dev:
            device.use = True
        i = i+1

bpy.ops.wm.open_mainfile(filepath=blend_filepath)
# レンダリング設定を変更します
bpy.context.scene.cycles.device = "GPU"             #   <-ここをファイル開いてからにすると成功
bpy.context.scene.render.engine = 'CYCLES'          #   <-ここをファイル開いてからにすると成功

bpy.context.scene.render.image_settings.file_format = 'PNG'  # 画像フォーマットを設定（PNG、JPEG、等）
bpy.context.scene.render.filepath = output_path + "img"  # ファイル名を設定
# フレーム範囲を設定
bpy.context.scene.frame_start = start
bpy.context.scene.frame_end = end
# レンダリングを実行
bpy.ops.render.render(animation=True)
print("-----------------")
for device in cycles_prefs.devices:        
    print("useDevice:", device.name, device.type, "use",device.use)

# Blenderを終了
bpy.ops.wm.quit_blender()