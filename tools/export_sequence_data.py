import json
import subprocess
import shutil
from pathlib import Path

import numpy as np
import torch
import trimesh
from PIL import Image
from scipy.spatial.transform import Rotation as SciRot
from smplx import MANO


ROOT = Path("/CT/WildHOI/work/GraG_website")
ASSETS = ROOT / "assets"
MANO_MODEL_DIR = Path("/CT/WildHOI/work/third_party/hold/code/body_models")
P3D_TO_GL = np.array(
    [[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]],
    dtype=np.float32,
)
GL_TO_CV = np.array(
    [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]],
    dtype=np.float32,
)
CV_TO_GL = GL_TO_CV.copy()

VIEWER_SEQUENCES = [
    {
        "key": "hot3d_h010",
        "label": "H010P001560573a3bleft",
        "dataset": "HOT3D",
        "type": "hot3d_cache",
        "viewer_cache": Path("/CT/WildHOI/work/third_party/hold/code/hot3d_results/viewer_cache/H010P001560573a3bleft.npz"),
        "thumbnail": Path("/CT/WildHOI/work/demo_data/H010P001560573a3bleft/rgb/000000.png"),
    },
    {
        "key": "ho3d_sm2",
        "label": "hold_SM2_ho3d",
        "dataset": "HO3D",
        "type": "ho3d_demo",
        "demo_dir": Path("/CT/WildHOI/work/demo_data/hold_SM2_ho3d"),
        "thumbnail": Path("/CT/WildHOI/work/demo_data/hold_SM2_ho3d/rgb/000000.png"),
        "mesh_cache_dir": Path("/scratch/inf0/user/aaytekin/0_GRAG_FIGS/hold_SM2_ho3d"),
    },
]

COMPARISON_SEQUENCES = [
    {
        "key": "hot3d_h010",
        "label": "H010P001560573a3bleft",
        "dataset": "HOT3D",
        "title": "Results",
        "camera_subtitle": "H010P001560573a3bleft · camera view",
        "side_subtitle": "H010P001560573a3bleft · side view",
        "camera": {
            "HOLD": {"path": Path("/CT/WildHOI/work/ECCV_videos/hold/hot3d_H010P001560573a3bleft_stage1/camera_view/video_0.mp4"), "start": 0.0, "end": 7.7},
            "BIGS": {"path": Path("/CT/WildHOI/work/ECCV_videos/bigs/H010P001560573a3bleft/camera_view/video_0.mp4"), "start": 0.0, "end": 7.7},
            "MagicHOI": {"path": None, "start": 0.0, "end": 7.7},
            "Ours": {"path": Path("/CT/WildHOI/work/ECCV_videos/ours/H010P001560573a3bleft/camera_view/video_0.mp4"), "start": 0.0, "end": 7.7},
            "GT": {
                "path": Path("/CT/WildHOI/work/ECCV_videos/hot3d_gt/H010P001560573a3bleft/camera_view/video_0.mp4"),
                "start": 0.0,
                "end": 7.7,
                "source_fps_override": 10.0,
            },
        },
        "side": {
            "HOLD": {"path": Path("/CT/WildHOI/work/ECCV_videos/hold/hot3d_H010P001560573a3bleft_stage1/side_view/video_0.mp4"), "start": 0.0, "end": 7.7},
            "BIGS": {"path": Path("/CT/WildHOI/work/ECCV_videos/bigs/H010P001560573a3bleft/side_view/video_0.mp4"), "start": 0.0, "end": 7.7},
            "MagicHOI": {"path": None, "start": 0.0, "end": 7.7},
            "Ours": {"path": Path("/CT/WildHOI/work/ECCV_videos/ours/H010P001560573a3bleft/side_view/video_0.mp4"), "start": 0.0, "end": 7.7},
            "GT": {"path": Path("/CT/WildHOI/work/ECCV_videos/hot3d_gt/H010P001560573a3bleft/side_view/video_0.mp4"), "start": 0.0, "end": 7.7},
        },
        "thumbnail": Path("/CT/WildHOI/work/demo_data/H010P001560573a3bleft/rgb/000000.png"),
    },
    {
        "key": "hot3d_h003",
        "label": "H003P001244c5f677right",
        "dataset": "HOT3D",
        "title": "Results",
        "camera_subtitle": "H003P001244c5f677right · camera view",
        "side_subtitle": "H003P001244c5f677right · side view",
        "camera": {
            "HOLD": {"path": Path("/CT/WildHOI/work/ECCV_videos/hold/hot3d_H003P001244c5f677right_stage1/camera_view/video_0.mp4"), "start": 1.6, "end": 3.7},
            "BIGS": {"path": Path("/CT/WildHOI/work/ECCV_videos/bigs/H003P001244c5f677right/camera_view/video_0.mp4"), "start": 1.6, "end": 3.7},
            "MagicHOI": {"path": Path("/CT/WildHOI/work/ECCV_videos/magichoi/H003P001244c5f677right/camera_view/video_0.mp4"), "start": 1.6, "end": 3.7},
            "Ours": {"path": Path("/CT/WildHOI/work/ECCV_videos/ours/H003P001244c5f677right/camera_view/video_0.mp4"), "start": 1.6, "end": 3.7},
            "GT": {
                "path": Path("/CT/WildHOI/work/ECCV_videos/hot3d_gt/H003P001244c5f677right/camera_view/video_0.mp4"),
                "start": 1.6,
                "end": 3.7,
                "source_fps_override": 10.0,
            },
        },
        "side": {
            "HOLD": {"path": Path("/CT/WildHOI/work/ECCV_videos/hold/hot3d_H003P001244c5f677right_stage1/side_view/video_0.mp4"), "start": 1.6, "end": 3.7},
            "BIGS": {"path": Path("/CT/WildHOI/work/ECCV_videos/bigs/H003P001244c5f677right/side_view/video_0.mp4"), "start": 1.6, "end": 3.7},
            "MagicHOI": {"path": Path("/CT/WildHOI/work/ECCV_videos/magichoi/H003P001244c5f677right/side_view/video_0.mp4"), "start": 1.6, "end": 3.7},
            "Ours": {"path": Path("/CT/WildHOI/work/ECCV_videos/ours/H003P001244c5f677right/side_view/video_0.mp4"), "start": 1.6, "end": 3.7},
            "GT": {"path": Path("/CT/WildHOI/work/ECCV_videos/hot3d_gt/H003P001244c5f677right/side_view/video_0.mp4"), "start": 1.6, "end": 3.7},
        },
        "thumbnail": Path("/CT/WildHOI/work/demo_data/H003P001244c5f677right/rgb/000000.png"),
    },
    {
        "key": "ho3d_mc1",
        "label": "hold_MC1_ho3d",
        "dataset": "HO3D",
        "title": "Results",
        "camera_subtitle": "hold_MC1_ho3d · camera view",
        "side_subtitle": "hold_MC1_ho3d · side view",
        "camera": {
            "HOLD": {"path": Path("/CT/WildHOI/work/ECCV_videos/hold/hold_MC1_ho3d/camera_view/video_0.mp4"), "start": 3.0, "end": 6.9},
            "BIGS": {"path": Path("/CT/WildHOI/work/ECCV_videos/bigs/hold_MC1_ho3d/camera_view/video_1.mp4"), "start": 3.0, "end": 6.9},
            "MagicHOI": {"path": Path("/CT/WildHOI/work/ECCV_videos/magichoi/hold_MC1_ho3d/camera_view/video_0.mp4"), "start": 3.0, "end": 6.9},
            "Ours": {"path": Path("/scratch/inf0/user/aaytekin/GraG/DEBUG_DATA/hold_MC1_ho3d/hold_MC1_ho3d_20260309-114148/videos/camera_view/video_0.mp4"), "start": 3.0, "end": 6.9},
            "GT": {"path": Path("/CT/WildHOI/work/ECCV_videos/ho3d_gt/hold_MC1_ho3d/camera_view/video_0.mp4"), "start": 3.0, "end": 6.9},
        },
        "side": {
            "HOLD": {"path": Path("/CT/WildHOI/work/ECCV_videos/hold/hold_MC1_ho3d/side_view/video_1.mp4"), "start": 3.0, "end": 6.9},
            "BIGS": {"path": Path("/CT/WildHOI/work/ECCV_videos/bigs/hold_MC1_ho3d/side_view/video_1.mp4"), "start": 3.0, "end": 6.9},
            "MagicHOI": {"path": Path("/CT/WildHOI/work/ECCV_videos/magichoi/hold_MC1_ho3d/side_view/video_0.mp4"), "start": 3.0, "end": 6.9},
            "Ours": {"path": Path("/scratch/inf0/user/aaytekin/GraG/DEBUG_DATA/hold_MC1_ho3d/hold_MC1_ho3d_20260309-114148/videos/side_view/video_0.mp4"), "start": 3.0, "end": 6.9},
            "GT": {"path": Path("/CT/WildHOI/work/ECCV_videos/ho3d_gt/hold_MC1_ho3d/side_view/video_0.mp4"), "start": 3.0, "end": 6.9},
        },
        "thumbnail": Path("/CT/WildHOI/work/demo_data/hold_MC1_ho3d/rgb/000000.png"),
    },
    {
        "key": "ho3d_sm2",
        "label": "hold_SM2_ho3d",
        "dataset": "HO3D",
        "title": "Results",
        "camera_subtitle": "hold_SM2_ho3d · camera view",
        "side_subtitle": "hold_SM2_ho3d · side view",
        "camera": {
            "HOLD": {"path": Path("/CT/WildHOI/work/ECCV_videos/hold/hold_SM2_ho3d/camera_view/video_0.mp4"), "start": 5.8, "end": 14.3},
            "BIGS": {"path": Path("/CT/WildHOI/work/ECCV_videos/bigs/hold_SM2_ho3d/camera_view/video_0.mp4"), "start": 5.8, "end": 14.3},
            "MagicHOI": {"path": Path("/CT/WildHOI/work/ECCV_videos/magichoi/hold_SM2_ho3d/camera_view/video_0.mp4"), "start": 5.8, "end": 14.3},
            "Ours": {"path": Path("/scratch/inf0/user/aaytekin/GraG/DEBUG_DATA/hold_SM2_ho3d/hold_SM2_ho3d_20260311-044641/videos/camera_view/video_0.mp4"), "start": 5.8, "end": 14.3},
            "GT": {"path": Path("/CT/WildHOI/work/ECCV_videos/ho3d_gt/hold_SM2_ho3d/camera_view/video_0.mp4"), "start": 5.8, "end": 14.3},
        },
        "side": {
            "HOLD": {"path": Path("/CT/WildHOI/work/ECCV_videos/hold/hold_SM2_ho3d/side_view/video_1.mp4"), "start": 5.8, "end": 14.3},
            "BIGS": {"path": Path("/CT/WildHOI/work/ECCV_videos/bigs/hold_SM2_ho3d/side_view/video_0.mp4"), "start": 5.8, "end": 14.3},
            "MagicHOI": {"path": Path("/CT/WildHOI/work/ECCV_videos/magichoi/hold_SM2_ho3d/side_view/video_0.mp4"), "start": 5.8, "end": 14.3},
            "Ours": {"path": Path("/scratch/inf0/user/aaytekin/GraG/DEBUG_DATA/hold_SM2_ho3d/hold_SM2_ho3d_20260311-044641/videos/side_view/video_0.mp4"), "start": 5.8, "end": 14.3},
            "GT": {"path": Path("/CT/WildHOI/work/ECCV_videos/ho3d_gt/hold_SM2_ho3d/side_view/video_0.mp4"), "start": 5.8, "end": 14.3},
        },
        "thumbnail": Path("/CT/WildHOI/work/demo_data/hold_SM2_ho3d/rgb/000000.png"),
    },
]


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)


def get_video_fps(path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=avg_frame_rate",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    value = result.stdout.strip()
    if "/" in value:
        num, den = value.split("/", 1)
        den_f = float(den)
        return float(num) / den_f if den_f else 0.0
    return float(value)


def convert_effective_seconds(path: Path, start_sec: float, end_sec: float, source_fps_override: float | None) -> tuple[float, float]:
    if not source_fps_override:
        return start_sec, end_sec
    raw_fps = get_video_fps(path)
    if raw_fps <= 0:
        return start_sec, end_sec
    scale = source_fps_override / raw_fps
    return start_sec * scale, end_sec * scale


def compute_effective_playback_rate(path: Path, source_fps_override: float | None, base_rate: float = 1.0) -> float:
    if not source_fps_override:
        return base_rate
    raw_fps = get_video_fps(path)
    if raw_fps <= 0:
        return base_rate
    return base_rate * (source_fps_override / raw_fps)


def load_mano(is_right: bool) -> MANO:
    return MANO(
        str(MANO_MODEL_DIR),
        use_pca=False,
        flat_hand_mean=False,
        is_rhand=is_right,
    )


def save_glb(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)


def to_pose_matrix(R: np.ndarray, t: np.ndarray, scale: np.ndarray | None = None) -> np.ndarray:
    M = np.eye(4, dtype=np.float32)
    if scale is None:
        M[:3, :3] = R.astype(np.float32)
    else:
        M[:3, :3] = (R @ np.diag(scale)).astype(np.float32)
    M[:3, 3] = t.astype(np.float32)
    return M


def estimate_rigid_transform(source: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    src_mean = source.mean(axis=0)
    tgt_mean = target.mean(axis=0)
    src_centered = source - src_mean
    tgt_centered = target - tgt_mean
    H = src_centered.T @ tgt_centered
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    t = tgt_mean - R @ src_mean
    return R.astype(np.float32), t.astype(np.float32)


def write_metadata(dst_dir: Path, num_frames: int, width: int, height: int) -> None:
    write_json(
        dst_dir / "metadata.json",
        {
            "glb_path": "object_mesh_scaled.glb",
            "num_frames": int(num_frames),
            "image_width": int(width),
            "image_height": int(height),
        },
    )


def export_hot3d_viewer_sequence(sequence: dict, dst_dir: Path) -> dict:
    data = np.load(sequence["viewer_cache"], allow_pickle=True)
    rgb_dir = dst_dir / "rgb_images"
    hand_dir = dst_dir / "hand_meshes"
    rgb_dir.mkdir(parents=True, exist_ok=True)
    hand_dir.mkdir(parents=True, exist_ok=True)

    frame_paths = [Path(x) for x in data["fnames"].tolist()]
    first_image = Image.open(frame_paths[0])
    width, height = first_image.size
    first_image.close()

    hand_faces = data["faces_h"].astype(np.int64)
    object_faces = data["faces_o"].astype(np.int64)
    hand_vertices_cv = data["v3d_h"].astype(np.float32)
    object_vertices_cv = data["v3d_o"].astype(np.float32)
    hand_vertices_gl = hand_vertices_cv @ CV_TO_GL.T
    object_vertices_gl = object_vertices_cv @ CV_TO_GL.T

    canonical_object = object_vertices_gl[0]
    save_glb(dst_dir / "object_mesh_scaled.glb", canonical_object, object_faces)

    object_poses = []
    for frame_idx, src_path in enumerate(frame_paths):
        copy_file(src_path, rgb_dir / f"frame_{frame_idx:04d}.png")
        save_glb(hand_dir / f"hand_{frame_idx:04d}.glb", hand_vertices_gl[frame_idx], hand_faces)
        R, t = estimate_rigid_transform(canonical_object, object_vertices_gl[frame_idx])
        object_poses.append(to_pose_matrix(R, t).tolist())

    write_metadata(dst_dir, len(frame_paths), width, height)
    write_json(dst_dir / "object_poses.json", {"object_poses": object_poses})
    write_json(dst_dir / "cam_K.json", {"intrinsic_matrix": data["K"].astype(np.float32).tolist()})
    copy_file(sequence["thumbnail"], dst_dir / "thumbnail.png")

    return {
        "key": sequence["key"],
        "label": sequence["label"],
        "dataset": sequence["dataset"],
        "thumbnail": f"assets/agile_results/{sequence['key']}/thumbnail.png",
        "metadataPath": f"assets/agile_results/{sequence['key']}/metadata.json",
    }


def pose_object_rotation_gl(pose: dict) -> np.ndarray:
    quat_wxyz = pose["rotation"][0].detach().cpu().numpy()
    rot_p3d = SciRot.from_quat([quat_wxyz[1], quat_wxyz[2], quat_wxyz[3], quat_wxyz[0]]).as_matrix()
    return (rot_p3d @ P3D_TO_GL).astype(np.float32)


def export_ho3d_viewer_sequence(sequence: dict, dst_dir: Path) -> dict:
    demo_dir = sequence["demo_dir"]
    seq_name = demo_dir.name
    intrinsics = np.load(demo_dir / "results" / "exports" / "npz" / "results.npz")["intrinsics"].astype(np.float32)
    rgb_src_dir = demo_dir / "rgb"
    rgb_dir = dst_dir / "rgb_images"
    hand_dir = dst_dir / "hand_meshes"
    rgb_dir.mkdir(parents=True, exist_ok=True)
    hand_dir.mkdir(parents=True, exist_ok=True)

    rgb_paths = sorted(rgb_src_dir.glob("*.png"))
    if not rgb_paths:
        raise FileNotFoundError(f"No RGB frames found in {rgb_src_dir}")
    first_image = Image.open(rgb_paths[0])
    width, height = first_image.size
    first_image.close()

    mesh_cache_dir = sequence.get("mesh_cache_dir")
    if mesh_cache_dir is not None and Path(mesh_cache_dir).exists():
        cache_dir = Path(mesh_cache_dir)
        object_vertices_cv = np.load(cache_dir / "pred_v3d_c_object.npy").astype(np.float32)
        hand_vertices_cv = np.load(cache_dir / "pred_v3d_c_right.npy").astype(np.float32)
        object_faces = np.load(cache_dir / "pred_faces_object.npy").astype(np.int64)
        hand_faces = np.load(cache_dir / "pred_faces_right.npy").astype(np.int64)
        camera_forward_offset = float(sequence.get("camera_forward_offset", 0.0))
        if camera_forward_offset != 0.0:
            object_vertices_cv = object_vertices_cv.copy()
            hand_vertices_cv = hand_vertices_cv.copy()
            object_vertices_cv[..., 2] += camera_forward_offset
            hand_vertices_cv[..., 2] += camera_forward_offset

        object_vertices_gl = object_vertices_cv @ CV_TO_GL.T
        hand_vertices_gl = hand_vertices_cv @ CV_TO_GL.T
        canonical_object = object_vertices_gl[0]
        save_glb(dst_dir / "object_mesh_scaled.glb", canonical_object, object_faces)

        object_poses = []
        num_frames = min(len(rgb_paths), object_vertices_gl.shape[0], hand_vertices_gl.shape[0])
        for frame_idx in range(num_frames):
            copy_file(rgb_paths[frame_idx], rgb_dir / f"frame_{frame_idx:04d}.png")
            save_glb(hand_dir / f"hand_{frame_idx:04d}.glb", hand_vertices_gl[frame_idx], hand_faces)
            R, t = estimate_rigid_transform(canonical_object, object_vertices_gl[frame_idx])
            object_poses.append(to_pose_matrix(R, t).tolist())
    else:
        poses = torch.load(demo_dir / "sam3d" / "sam3d_poses" / "poses_dict.pt", map_location="cpu")
        object_mesh = trimesh.load(demo_dir / "sam3d" / "result.glb", force="mesh")
        object_mesh.export(dst_dir / "object_mesh_scaled.glb")

        mano_json_dir = demo_dir / "dynhamr" / "track_preds" / seq_name / "001"
        mano_json_paths = sorted(mano_json_dir.glob("*_mano.json"))
        if not mano_json_paths:
            raise FileNotFoundError(f"No MANO json files found in {mano_json_dir}")

        with mano_json_paths[0].open("r", encoding="utf-8") as f:
            first_frame = json.load(f)
        mano = load_mano(bool(first_frame["is_right"]))
        hand_faces = mano.faces.astype(np.int64)

        object_poses = []
        for frame_idx, mano_path in enumerate(mano_json_paths):
            copy_file(rgb_paths[frame_idx], rgb_dir / f"frame_{frame_idx:04d}.png")
            with mano_path.open("r", encoding="utf-8") as f:
                mano_data = json.load(f)

            out = mano(
                betas=torch.tensor(mano_data["betas"], dtype=torch.float32)[None],
                global_orient=torch.tensor(mano_data["global_orient"], dtype=torch.float32)[None],
                hand_pose=torch.tensor(mano_data["body_pose"], dtype=torch.float32).reshape(1, -1),
                transl=torch.tensor(mano_data["cam_trans"], dtype=torch.float32)[None],
            )
            hand_vertices_cv = out.vertices[0].detach().cpu().numpy().astype(np.float32)
            hand_vertices_gl = hand_vertices_cv @ CV_TO_GL.T
            save_glb(hand_dir / f"hand_{frame_idx:04d}.glb", hand_vertices_gl, hand_faces)

            pose = poses[str(frame_idx)]
            rotation_gl = pose_object_rotation_gl(pose)
            translation_gl = (pose["translation"][0].detach().cpu().numpy() @ P3D_TO_GL).astype(np.float32)
            object_poses.append(to_pose_matrix(rotation_gl, translation_gl).tolist())

    write_metadata(dst_dir, len(object_poses), width, height)
    write_json(dst_dir / "object_poses.json", {"object_poses": object_poses})
    intrinsic_matrix = intrinsics[0] if intrinsics.ndim == 3 else intrinsics
    write_json(dst_dir / "cam_K.json", {"intrinsic_matrix": intrinsic_matrix.tolist()})
    copy_file(sequence["thumbnail"], dst_dir / "thumbnail.png")

    return {
        "key": sequence["key"],
        "label": sequence["label"],
        "dataset": sequence["dataset"],
        "thumbnail": f"assets/agile_results/{sequence['key']}/thumbnail.png",
        "metadataPath": f"assets/agile_results/{sequence['key']}/metadata.json",
    }


def export_viewer_assets() -> list[dict]:
    viewer_root = ASSETS / "agile_results"
    ensure_clean_dir(viewer_root)
    manifest = []

    for sequence in VIEWER_SEQUENCES:
        dst_dir = viewer_root / sequence["key"]
        dst_dir.mkdir(parents=True, exist_ok=True)
        if sequence["type"] == "hot3d_cache":
            entry = export_hot3d_viewer_sequence(sequence, dst_dir)
        else:
            entry = export_ho3d_viewer_sequence(sequence, dst_dir)
        manifest.append(entry)

    return manifest


def export_comparison_assets() -> list[dict]:
    comparison_root = ASSETS / "comparison_sequences"
    ensure_clean_dir(comparison_root)
    manifest = []

    for sequence in COMPARISON_SEQUENCES:
        seq_dir = comparison_root / sequence["key"]
        copy_file(sequence["thumbnail"], seq_dir / "thumbnail.png")
        entry = {
            "key": sequence["key"],
            "label": sequence["label"],
            "dataset": sequence["dataset"],
            "title": sequence["title"],
            "camera_subtitle": sequence["camera_subtitle"],
            "side_subtitle": sequence["side_subtitle"],
            "thumbnail": f"assets/comparison_sequences/{sequence['key']}/thumbnail.png",
            "camera": {},
            "side": {},
        }
        for view_name in ("camera", "side"):
            for method_name, src_meta in sequence[view_name].items():
                if src_meta["path"] is None:
                    entry[view_name][method_name] = {
                        "src": None,
                        "start": src_meta["start"],
                        "end": src_meta["end"],
                        "playback_rate": 1.0,
                        "na": True,
                    }
                    continue
                filename = f"{method_name.lower()}.mp4"
                dst = seq_dir / view_name / filename
                copy_file(src_meta["path"], dst)
                start_sec, end_sec = convert_effective_seconds(
                    src_meta["path"],
                    src_meta["start"],
                    src_meta["end"],
                    src_meta.get("source_fps_override"),
                )
                playback_rate = compute_effective_playback_rate(
                    src_meta["path"],
                    src_meta.get("source_fps_override"),
                    src_meta.get("playback_rate", 1.0),
                )
                entry[view_name][method_name] = {
                    "src": f"assets/comparison_sequences/{sequence['key']}/{view_name}/{filename}",
                    "start": start_sec,
                    "end": end_sec,
                    "playback_rate": playback_rate,
                }
        manifest.append(entry)

    return manifest


def write_manifest(viewer_manifest: list[dict], comparison_manifest: list[dict]) -> None:
    write_json(
        ASSETS / "site_data.json",
        {
            "viewerSequences": viewer_manifest,
            "comparisonSequences": comparison_manifest,
        },
    )


def main() -> None:
    viewer_manifest = export_viewer_assets()
    comparison_manifest = export_comparison_assets()
    write_manifest(viewer_manifest, comparison_manifest)
    print("Exported AGILE viewer assets and comparison assets.")


if __name__ == "__main__":
    main()
