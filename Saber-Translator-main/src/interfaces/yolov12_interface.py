import sys
import os
import logging

# 让本地 yolov12-main 目录优先
yolov12_main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../yolov12-main'))
if yolov12_main_path not in sys.path:
    sys.path.insert(0, yolov12_main_path)

from ultralytics import YOLO

logger = logging.getLogger("YOLOv12Interface")

# --- 全局变量存储加载的模型 ---
_yolov12_model = None
_model_conf = 0.5  # 默认置信度阈值


def load_yolov12_model(weights_name='best.pt', conf_threshold=0.6):
    """
    加载 YOLOv12 模型。如果模型已加载，则直接返回。

    Args:
        weights_name (str): 权重文件名 (例如 'best.pt').
        conf_threshold (float): 置信度阈值。

    Returns:
        ultralytics.YOLO: 加载的模型或 None (如果失败).
    """
    global _yolov12_model, _model_conf

    if _yolov12_model is not None:
        # ultralytics YOLOv12 的置信度阈值在 predict 时传递，不在模型对象上设置
        return _yolov12_model

    try:
        # 你原有的 resource_path 逻辑不变
        from src.shared.path_helpers import resource_path
        weights_path = resource_path(os.path.join('weights', weights_name))
        if not os.path.exists(weights_path):
            logger.error(f"YOLOv12 权重文件未找到: {weights_path}")
            return None
        logger.info(f"开始加载 YOLOv12 本地模型: {weights_path}")
        _yolov12_model = YOLO(weights_path)
        logger.info(f"YOLOv12 本地模型加载成功")
        return _yolov12_model
    except Exception as e:
        logger.error(f"加载 YOLOv12 本地模型失败: {e}", exc_info=True)
        _yolov12_model = None
        return None


def detect_bubbles_v12(image_cv, conf_threshold=0.6):
    """
    使用加载的 YOLOv12 模型检测图像中的气泡。

    Args:
        image_cv (numpy.ndarray): OpenCV BGR 格式的图像。
        conf_threshold (float): 本次检测使用的置信度阈值。

    Returns:
        tuple: 包含 boxes, scores, class_ids 的元组，如果失败则返回 ([], [], [])。
               boxes: numpy 数组，形状 (N, 4)，每个框为 [x1, y1, x2, y2]。
               scores: numpy 数组，形状 (N,)。
               class_ids: numpy 数组，形状 (N,)。
    """
    import numpy as np
    model = load_yolov12_model(conf_threshold=conf_threshold)
    if model is None:
        return np.array([]), np.array([]), np.array([])

    try:
        results = model.predict(source=image_cv, conf=conf_threshold, verbose=False)
        boxes, scores, class_ids = [], [], []
        for r in results:
            if hasattr(r, 'boxes') and r.boxes is not None:
                b = r.boxes.xyxy.cpu().numpy() if hasattr(r.boxes, 'xyxy') else np.array([])
                s = r.boxes.conf.cpu().numpy() if hasattr(r.boxes, 'conf') else np.array([])
                c = r.boxes.cls.cpu().numpy() if hasattr(r.boxes, 'cls') else np.array([])
                boxes.append(b)
                scores.append(s)
                class_ids.append(c)
        if boxes:
            boxes = np.concatenate(boxes, axis=0)
            scores = np.concatenate(scores, axis=0)
            class_ids = np.concatenate(class_ids, axis=0)
        else:
            boxes = np.array([])
            scores = np.array([])
            class_ids = np.array([])
        logger.info(f"YOLOv12 检测到 {len(boxes)} 个候选框 (阈值: {conf_threshold})")
        return boxes, scores, class_ids
    except Exception as e:
        logger.error(f"YOLOv12 推理失败: {e}", exc_info=True)
        return np.array([]), np.array([]), np.array([])

# --- 测试代码 ---
if __name__ == '__main__':
    print("--- 测试 YOLOv12 本地接口 ---")
    from src.shared.path_helpers import resource_path
    test_image_path = resource_path('pic/before1.png')
    if os.path.exists(test_image_path):
        import cv2
        print(f"加载测试图片: {test_image_path}")
        img = cv2.imread(test_image_path)
        if img is not None:
            print("开始检测...")
            detected_boxes, detected_scores, detected_classes = detect_bubbles_v12(img, conf_threshold=0.5)
            print(f"检测完成，找到 {len(detected_boxes)} 个气泡。")
            # 可视化结果
            try:
                model = load_yolov12_model()
                results = model.predict(source=img, conf=0.5, verbose=False)
                results[0].show()
            except Exception as e:
                print(f"可视化失败: {e}")
        else:
            print(f"错误：无法加载测试图片 {test_image_path}")
    else:
        print(f"错误：测试图片未找到 {test_image_path}")

    print("\n再次调用检测 (应复用模型)...")
    detect_bubbles_v12(img, conf_threshold=0.7)
    print("再次调用检测 (应复用模型)...")
    detect_bubbles_v12(img, conf_threshold=0.7) 