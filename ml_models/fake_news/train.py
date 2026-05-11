from transformers import TrainingArguments, Trainer, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
import os

MODEL_NAME = "roberta-base"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved_model")


def train_fake_news_model(train_data: list, eval_data: list, epochs: int = 3):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

    train_dataset = Dataset.from_list(train_data)
    eval_dataset = Dataset.from_list(eval_data)

    train_dataset = train_dataset.map(tokenize_function, batched=True)
    eval_dataset = eval_dataset.map(tokenize_function, batched=True)

    training_args = TrainingArguments(
        output_dir=MODEL_PATH,
        num_train_epochs=epochs,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_dir="./logs",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )

    trainer.train()
    trainer.save_model(MODEL_PATH)
    tokenizer.save_pretrained(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
