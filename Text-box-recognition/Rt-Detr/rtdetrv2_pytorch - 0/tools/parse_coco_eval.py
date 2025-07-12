import torch
import numpy as np
import argparse

# COCO官方指标顺序
COCO_METRICS = [
    'AP', 'AP50', 'AP75', 'APs', 'APm', 'APl',
    'AR1', 'AR10', 'AR100', 'ARs', 'ARm', 'ARl'
]

def parse_eval(eval_path):
    data = torch.load(eval_path)
    # 一般主指标在 stats 里
    stats = data.get('stats', None)
    if stats is not None:
        print('==== COCO主要指标 ====' )
        for name, value in zip(COCO_METRICS, stats):
            print(f'{name:6}: {value:.4f}')
        print('\n全部指标 stats:', stats)
    else:
        print('未找到 stats 字段，原始内容如下:')
        for k, v in data.items():
            if isinstance(v, np.ndarray):
                print(f'{k}: shape={v.shape}')
            else:
                print(f'{k}: {v}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval-path', type=str, required=True, help='latest.pth 路径')
    args = parser.parse_args()
    parse_eval(args.eval_path) 