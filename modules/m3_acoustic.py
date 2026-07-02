import torch
import torch.nn as nn
import librosa
import numpy as np

class AudioCNN(nn.Module):
    def __init__(self):
        super(AudioCNN, self).__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 16 * 16, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 5)
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.fc_layers(x)
        return x

CATEGORIES = ["gunshot", "explosion", "helicopter", "siren", "ambient"]

model = AudioCNN()
model.load_state_dict(torch.load("models/m3_acoustic/m3_acoustic_cnn.pt", map_location="cpu"))
model.eval()

def predict_audio(file_path):
    y, sr = librosa.load(file_path, duration=5)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)

    if mel_db.shape[1] < 128:
        mel_db = np.pad(mel_db, ((0,0),(0, 128 - mel_db.shape[1])))
    else:
        mel_db = mel_db[:, :128]

    X = torch.FloatTensor(mel_db).unsqueeze(0).unsqueeze(0)

    with torch.no_grad():
        output = model(X)
        probs = torch.softmax(output, dim=1)
        confidence, predicted = torch.max(probs, 1)

    return {
        "predicted_class": CATEGORIES[predicted.item()],
        "confidence": round(confidence.item() * 100, 2),
        "all_scores": {
            CATEGORIES[i]: round(probs[0][i].item() * 100, 2)
            for i in range(len(CATEGORIES))
        }
    }