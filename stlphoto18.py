import os
import sys
import math
import numpy as np
import trimesh
import trimesh.transformations as tf
from PIL import Image
import pyrender
import concurrent.futures

def center_and_fit_no_division(mesh):
    bounds = mesh.bounds
    min_corner = bounds[0]
    mesh.apply_translation(-min_corner)

    done = False
    while not done:
        bounds = mesh.bounds
        size = bounds[1] - bounds[0]
        largest_dim = max(size)

        if largest_dim > 2.0:
            mesh.apply_scale(0.5)
        elif largest_dim < 1.0 and largest_dim > 1e-12:
            mesh.apply_scale(2.0)
        else:
            done = True

    bounds = mesh.bounds
    min_corner = bounds[0]
    max_corner = bounds[1]
    cx = (min_corner[0] + max_corner[0]) * 0.5
    cy = (min_corner[1] + max_corner[1]) * 0.5
    cz = (min_corner[2] + max_corner[2]) * 0.5
    mesh.apply_translation((-cx, -cy, -cz))

def fix_inverted_faces_if_needed(mesh):
    if not mesh.is_winding_consistent:
        mesh.fix_normals()

def camera_top_view():
    return tf.translation_matrix([0, 0, 5])

def camera_front_view():
    trans = tf.translation_matrix([0, -5, 0])
    rot_x_90 = tf.rotation_matrix(math.radians(90), [1, 0, 0])
    return trans @ rot_x_90

def render_offscreen_with_pyrender(mesh, camera_transform, out_png):
    pyr_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=False)

    scene = pyrender.Scene(
        bg_color=[40/255.0, 40/255.0, 40/255.0, 1.0],
        ambient_light=[0.3, 0.3, 0.3]
    )
    scene.add(pyr_mesh)

    light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
    light_pose = tf.translation_matrix([2, 2, 5])
    scene.add(light, pose=light_pose)

    camera = pyrender.PerspectiveCamera(
        yfov=math.radians(60.0),
        znear=0.01,
        zfar=100.0
    )
    scene.add(camera, pose=camera_transform)

    try:
        r = pyrender.OffscreenRenderer(viewport_width=800, viewport_height=800)
        color_img, depth_img = r.render(scene)
        r.delete()
    except Exception as e:
        print(f"Warning: Could not render {out_png} => {e}")
        return

    Image.fromarray(color_img).save(out_png)
    enforce_dark_background(out_png, (40, 40, 40))

def enforce_dark_background(image_path, rgb=(40, 40, 40)):
    try:
        img = Image.open(image_path).convert("RGBA")
        px = img.load()
        if px is None:
            return
        w, h = img.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if (r == 255 and g == 255 and b == 255 and a == 255):
                    px[x, y] = (rgb[0], rgb[1], rgb[2], 255)
        img.save(image_path)
    except Exception as e:
        print("Error enforcing dark background:", e)

def render_two_views(mesh, out_prefix):
    top_png = out_prefix + "_top_view.png"
    front_png = out_prefix + "_front_view.png"

    if os.path.exists(top_png) and os.path.exists(front_png):
        print(f"Skipping (images exist): {top_png} & {front_png}")
        return

    if not os.path.exists(top_png):
        top_tf = camera_top_view()
        render_offscreen_with_pyrender(mesh, top_tf, top_png)
        print(f"Rendered top view => {top_png}")
    else:
        print(f"Skipping (exists): {top_png}")

    if not os.path.exists(front_png):
        front_tf = camera_front_view()
        render_offscreen_with_pyrender(mesh, front_tf, front_png)
        print(f"Rendered front view => {front_png}")
    else:
        print(f"Skipping (exists): {front_png}")

def process_one_file_in_subprocess(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    dir_name = os.path.dirname(file_path)
    out_prefix = os.path.join(dir_name, base_name)

    try:
        mesh = trimesh.load(file_path, force='mesh')
    except Exception as e:
        return f"Error loading {file_path}: {e}"

    if mesh.is_empty or len(mesh.vertices) == 0:
        return f"Skipping empty mesh: {file_path}"

    center_and_fit_no_division(mesh)
    mesh.apply_scale(2.5)

    fix_inverted_faces_if_needed(mesh)
    try:
        mesh.visual.vertex_colors = [200, 150, 100, 255]
    except Exception as e:
        print(f"Error assigning color to {file_path}: {e}")

    render_two_views(mesh, out_prefix)
    return f"Rendered top & front for {file_path}"

def process_all_meshes_in_folder(folder_path, max_workers=4):
    all_files_to_process = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(('.stl', '.obj')):
                full_path = os.path.join(root, filename)

                base_name = os.path.splitext(filename)[0]
                top_png = os.path.join(root, base_name + "_top_view.png")
                front_png = os.path.join(root, base_name + "_front_view.png")

                if os.path.exists(top_png) and os.path.exists(front_png):
                    print(f"Skipping (images exist): {top_png} & {front_png}")
                    continue

                all_files_to_process.append(full_path)

    if not all_files_to_process:
        print("No STL/OBJ files need processing.")
        return

    executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
    futures = {
        executor.submit(process_one_file_in_subprocess, f): f
        for f in all_files_to_process
    }

    try:
        for idx, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            file_path = futures[future]
            try:
                result_msg = future.result()
                if result_msg:
                    print(result_msg)
            except Exception as e:
                print(f"Error in subprocess for {file_path}: {e}")
            finally:
                print(f"Completed {idx}/{len(all_files_to_process)} files.")
    except KeyboardInterrupt:
        print("Ctrl-C pressed. Stopping all workers gracefully...")
        executor.shutdown(wait=False, cancel_futures=True)
        sys.exit(1)

    executor.shutdown(wait=True)
    print("Processing complete.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py /path/to/folder [max_workers]")
        sys.exit(1)

    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print("Not a valid directory:", folder_path)
        sys.exit(1)

    max_workers = 4
    if len(sys.argv) >= 3:
        try:
            max_workers = int(sys.argv[2])
        except:
            pass

    process_all_meshes_in_folder(folder_path, max_workers=max_workers)
    print("Done.")

if __name__ == "__main__":
    main()
