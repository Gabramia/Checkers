# Checkers Game (Python + Pygame)

This is a full-featured Checkers game built in Python using Pygame. You can build and run it on any system using Docker — no local Python setup needed.

---

## 🚀 Quick Start with Docker

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/checkers-game.git
cd checkers-game
```

### 2. Build the Docker image

```bash
docker build -t checkers-game .
```

### 3. Run the game

```bash
docker run --rm -it checkers-game python main.py
```

> 💡 The game will open in a window (if Docker supports GUI on your OS — works on Linux and WSL2 with GUI).

---

## 🛠 Optional: Build an Executable

If you want to package the game into an executable (e.g., for sharing), run this inside the Docker container:

```bash
docker run --rm -it checkers-game pyinstaller --onefile --add-data "assets;assets" --distpath . main.py
```

> The built executable will appear in the container's `/checkers` directory. Use a volume mount to copy it to your host if needed.

---

## 📦 Requirements (for running without Docker)

If you want to run the game directly on your system:

- Python 3.10+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

- Then run:
  ```bash
  python main.py
  ```

---

## 👀 Screenshots

_(add screenshots of your game UI here)_

---

## 🧠 Features

- Local 2-player mode
- Easy and hard AI opponents
- Full GUI with interactive buttons
- Custom board and piece graphics
- Supports move highlighting and capture rules