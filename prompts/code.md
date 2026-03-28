import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# -----------------------------------
# 1. Hyperparameters & Setup
# -----------------------------------
BATCH_SIZE = 300
LEARNING_RATE = 1
EPOCHS = 3
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# -----------------------------------
# 2. Data Pipeline
# -----------------------------------
# Convert images to PyTorch tensors
transform = transforms.Compose([transforms.ToTensor()])

# Download and load datasets
train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
test_dataset = datasets.MNIST(root='./data', train=False, transform=transform)

# Create iterators for the data
train_loader = DataLoader(dataset=train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# -----------------------------------
# 3. Model Definition
# -----------------------------------
class PrimalCNN(nn.Module):
    def __init__(self):
        super(PrimalCNN, self).__init__()
        # Input: 1 channel (grayscale), Output: 16 channels
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=500, kernel_size=3, stride=1, padding=1)
        
        self.fc = nn.Linear(32 * 7 * 7, 10)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        
        # Flatten the tensor for the fully connected layer
        x = x.view(x.size(0), -1) 
        x = self.fc(x)
        return x

# Initialize model, loss function, and optimizer
model = PrimalCNN().to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# -----------------------------------
# 4. Training Loop
# -----------------------------------
print("Starting training...")
for epoch in range(EPOCHS):
    model.train()
    for batch_idx, (data, targets) in enumerate(train_loader):
        data, targets = data.to(DEVICE), targets.to(DEVICE)

        # Forward pass
        scores = model(data)
        loss = criterion(scores, targets)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Epoch [{epoch+1}/{EPOCHS}] completed. Last Batch Loss: {loss.item():.4f}")

# -----------------------------------
# 5. Testing Loop
# -----------------------------------
print("Evaluating model on test data...")
model.eval()
num_correct = 0
num_samples = 0

# Disable gradient calculation for evaluation
with torch.no_grad():
    for data, targets in test_loader:
        data, targets = data.to(DEVICE), targets.to(DEVICE)
        
        scores = model(data)
        _, predictions = scores.max(1)
        
        num_correct += (predictions == targets).sum().item()
        num_samples += predictions.size(0)

accuracy = float(num_correct) / float(num_samples) * 100
print(f"Test Accuracy: {accuracy:.2f}%")