# Nguyễn Tâm Bình - 2324801030003
# Chạy mô hình ngôn ngữ nhỏ trên GPU: Qwen2.5-0.5B-Instruct (khoảng 1 GB, tải từ Hugging Face lần đầu)
# Dùng trong máy chủ AI: /opt/ai/bin/python thu_llm.py "Câu hỏi của bạn"
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.stdout.reconfigure(encoding='utf-8')

MO_HINH = 'Qwen/Qwen2.5-0.5B-Instruct'


def main():
    cau_hoi = ' '.join(sys.argv[1:]) or 'Giải thích ngắn gọn điện toán đám mây là gì, cho ví dụ đời thường.'
    t = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(MO_HINH)
    model = AutoModelForCausalLM.from_pretrained(MO_HINH, torch_dtype=torch.float16).to('cuda')
    print(f'Nạp mô hình lên {torch.cuda.get_device_name(0)}: {time.perf_counter() - t:.1f} s')
    tin = tok.apply_chat_template([{'role': 'user', 'content': cau_hoi}], add_generation_prompt=True, return_tensors='pt').to('cuda')
    t = time.perf_counter()
    ra = model.generate(tin, max_new_tokens=256, do_sample=False)
    dt = time.perf_counter() - t
    moi = ra[0][tin.shape[1]:]
    print(f'\nHỏi: {cau_hoi}\n\nĐáp: {tok.decode(moi, skip_special_tokens=True)}')
    print(f'\n{len(moi)} token trong {dt:.1f} s ({len(moi) / dt:.0f} token/s)')


if __name__ == '__main__':
    main()
