from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset
import torch

# 1. Load tokenizer + model
clf_name = "xlm-roberta-base"
clf_tok = AutoTokenizer.from_pretrained(clf_name, use_fast=False)
try:
    # Try to load fine‑tuned model
    clf_model = AutoModelForSequenceClassification.from_pretrained("./department_classifier")
    print("Loaded fine‑tuned department classifier.")
except Exception as e:
    # Fall back to base model if not found
    print("Fine‑tuned model not found, loading base model instead.")
    clf_model = AutoModelForSequenceClassification.from_pretrained(clf_name, num_labels=4)
print("Model and tokenizer loaded.")

# 2. Freeze backbone layers (transfer learning)
for param in clf_model.roberta.parameters():
    param.requires_grad = False
print("Backbone layers frozen.")

# 3. Load dataset (train.csv and test.csv must exist in your project folder)
dataset = load_dataset('csv', data_files={'train': 'train.csv', 'test': 'test.csv'})
print("Dataset loaded.")

# 4. Tokenize function
def tokenize(batch):
    return clf_tok(batch['text'], padding="max_length", truncation=True, max_length=128)
print("Tokenization function defined.")
train_dataset = dataset['train'].map(tokenize, batched=True)
test_dataset = dataset['test'].map(tokenize, batched=True)
print("Datasets tokenized.")

# 5. Ensure we have a proper "labels" column for Hugging Face Trainer
def clean_labels(example):
    # Force labels to int, replace NaN with 0
    try:
        return {"labels": int(example.get("label", example.get("labels", 0)))}
    except:
        return {"labels": 0}

# Apply cleaning
train_dataset = train_dataset.map(clean_labels)
test_dataset = test_dataset.map(clean_labels)
# If "label" still exists, rename it to "labels"
if "label" in train_dataset.column_names and "labels" not in train_dataset.column_names:
    train_dataset = train_dataset.rename_column("label", "labels")
if "label" in test_dataset.column_names and "labels" not in test_dataset.column_names:
    test_dataset = test_dataset.rename_column("label", "labels")
# Cast labels to int again to be safe
train_dataset = train_dataset.map(lambda x: {"labels": int(x["labels"])})
test_dataset = test_dataset.map(lambda x: {"labels": int(x["labels"])})
# print(train_dataset[0])
print("Label column cleaned and ready.")


# 6. Set format for PyTorch
train_dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
test_dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
print("Datasets formatted for PyTorch.")

# 7. Training arguments
# print(f"train dataset:/n {train_dataset[0]}")

# training_args = TrainingArguments(
#     output_dir="./results",
#     evaluation_strategy="epoch",
#     save_strategy="epoch",
#     learning_rate=2e-5,
#     per_device_train_batch_size=8,
#     num_train_epochs=3,
#     weight_decay=0.01,
#     logging_dir="./logs",
#     logging_steps=10,
# )

training_args = TrainingArguments(
    output_dir="./results",
    do_eval=True,                # instead of evaluation_strategy
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
)
print("Training arguments set.")

# 8. Trainer setup
trainer = Trainer(
    model=clf_model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# 9. Train the model
trainer.train()
print("Model training complete.")

# 10. Save the fine‑tuned model
trainer.save_model("./department_classifier")
clf_tok.save_pretrained("./department_classifier")
# clf_tok.save_pretrained("./department_classifier", safe_serialization=False)
print("Model and tokenizer saved.")