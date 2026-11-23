# Nguyễn Tâm Bình - 2324801030003
# Thử máy chủ AI: thông tin GPU, tốc độ nhân ma trận (có khởi động trước), huấn luyện CNN trên MNIST bằng GPU so với CPU
# Dùng trong máy chủ AI: /opt/ai/bin/python thu_gpu.py
import time

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def matmul(device, dtype, n, lap):
    a = torch.randn(n, n, device=device, dtype=dtype)
    b = torch.randn(n, n, device=device, dtype=dtype)
    for _ in range(3):
        a @ b
    if device == 'cuda':
        torch.cuda.synchronize()
    t = time.perf_counter()
    for _ in range(lap):
        a @ b
    if device == 'cuda':
        torch.cuda.synchronize()
    dt = time.perf_counter() - t
    return lap * 2 * n ** 3 / dt / 1e12


def model():
    return nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10))


def train(device, train_set, test_set, gioi_han=None):
    torch.manual_seed(0)
    net = model().to(device)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    loader = DataLoader(train_set, batch_size=256, shuffle=True, num_workers=2)
    t = time.perf_counter()
    net.train()
    for i, (x, y) in enumerate(loader):
        if gioi_han and i >= gioi_han:
            break
        x, y = x.to(device), y.to(device)
        opt.zero_grad()
        loss_fn(net(x), y).backward()
        opt.step()
    if device == 'cuda':
        torch.cuda.synchronize()
    thoi_gian = time.perf_counter() - t
    net.eval()
    dung = tong = 0
    with torch.no_grad():
        for x, y in DataLoader(test_set, batch_size=1024):
            dung += (net(x.to(device)).argmax(1).cpu() == y).sum().item()
            tong += len(y)
    return thoi_gian, dung / tong


def main():
    print('PyTorch', torch.__version__, '| CUDA', torch.version.cuda, '| có GPU:', torch.cuda.is_available())
    if not torch.cuda.is_available():
        raise SystemExit('Không thấy GPU. Kiểm bằng lệnh nvidia-smi.')
    p = torch.cuda.get_device_properties(0)
    print(f'GPU: {p.name}, {p.total_memory / 1024 ** 3:.1f} GB VRAM, {p.multi_processor_count} SM')

    print('\nNhân ma trận 4096 x 4096 (đã chạy khởi động trước khi đo):')
    print(f'  GPU fp16: {matmul("cuda", torch.float16, 4096, 50):6.1f} TFLOPS')
    print(f'  GPU fp32: {matmul("cuda", torch.float32, 4096, 20):6.1f} TFLOPS')
    print(f'  CPU fp32: {matmul("cpu", torch.float32, 2048, 3):6.2f} TFLOPS')

    print('\nTải MNIST (60.000 ảnh chữ số viết tay)...')
    tf = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    train_set = datasets.MNIST('./du_lieu', train=True, download=True, transform=tf)
    test_set = datasets.MNIST('./du_lieu', train=False, download=True, transform=tf)

    gpu_s, gpu_acc = train('cuda', train_set, test_set)
    print(f'\nHuấn luyện CNN 1 epoch trên GPU: {gpu_s:.1f} s, độ chính xác tập kiểm tra {gpu_acc * 100:.2f}%')
    cpu_s, _ = train('cpu', train_set, test_set, gioi_han=40)
    cpu_epoch = cpu_s / 40 * len(DataLoader(train_set, batch_size=256))
    print(f'Cùng mô hình trên CPU (40 batch, ước cho 1 epoch): {cpu_epoch:.1f} s, GPU nhanh hơn khoảng {cpu_epoch / gpu_s:.0f} lần')
    print(f'VRAM dùng nhiều nhất: {torch.cuda.max_memory_allocated() / 1024 ** 2:.0f} MB')


if __name__ == '__main__':
    main()
