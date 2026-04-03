import os
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split

def train():
    # 1. 환경 확인
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 학습 장치 감지됨: {device.upper()}")

    # 2. 데이터 로드 (경로를 컨테이너 기준으로 수정)
    data_path = "/app/data/air_quality_texts.csv"
    if not os.path.exists(data_path):
        print(f"❌ 데이터 파일이 없습니다. 경로 확인: {data_path}")
        return

    df = pd.read_csv(data_path)
    
    # 3. 모델 및 토크나이저 준비
    model_name = "klue/bert-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3).to(device)

    # 4. 데이터셋 클래스 정의
    class AirDataset(torch.utils.data.Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels
        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item
        def __len__(self):
            return len(self.labels)

    # 5. 데이터 분할 및 토큰화
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['text'].tolist(), df['label'].tolist(), test_size=0.2, random_state=42
    )
    
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=64)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=64)

    train_dataset = AirDataset(train_encodings, train_labels)
    val_dataset = AirDataset(val_encodings, val_labels)

    # 6. 학습 설정 (에러 수정: evaluation_strategy -> eval_strategy)
    training_args = TrainingArguments(
        output_dir='/app/results',
        num_train_epochs=5,
        per_device_train_batch_size=16,
        logging_dir='/app/logs',
        logging_steps=10,
        eval_strategy="epoch",      # <-- 수정됨
        save_strategy="epoch",
        load_best_model_at_end=True,
        fp16=(device == "cuda"),    # GPU일 때만 fp16 사용
    )

    # 7. 트레이너 실행
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    print("🔥 Fine-tuning 시작...")
    trainer.train()

    # 8. 모델 저장
    save_path = "/app/app/models/fine_tuned_bert"
    os.makedirs(save_path, exist_ok=True)
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    print(f"✅ 학습 완료! 모델이 {save_path}에 저장되었습니다.")

if __name__ == "__main__":
    train()