# 🧠 Smart Brain Link Saver

A minimalist cross-browser extension to quickly categorize and save links. Works on **Chrome** and **Firefox**.

## 🚀 Setup & Installation

Follow these steps to activate the extension in your browser:

### 1. Build the Project
Make sure you have dependencies installed and run the build command:
```bash
cd extension
npm install
npm run build
```

### 2. Load into Chrome
1. Open Google Chrome and go to `chrome://extensions/`.
2. Toggle **Developer mode** (switch in the top right corner) to **ON**.
3. Click the **Load unpacked** button.
4. Select the **`chrome-extension/dist`** folder that was generated in the previous step.

### 2. Load into Firefox
1. Open Firefox and go to `about:debugging#/runtime/this-firefox`.
2. Click **Load Temporary Add-on...**.
3. Navigate to the **`chrome-extension/dist`** folder and select the **`manifest.json`** file.

---

## 🛠️ How It Works

- **Auto Capture**: The extension automatically detects the title and URL of your current tab.
- **Emoji Categories**:
  - 💼 **Work**: For professional or job-related links.
  - 🏠 **Personal**: For personal interests and hobbies.
  - ⏳ **Watch Later**: For articles or videos you want to check out later.
- **Save**: Clicking "Save to Brain" sends a POST request to `http://localhost:5000/api/save` (configurable in `App.jsx`).

## ⚡ Development

If you want to modify the design or functionality:
1. Edit files in `src/`.
2. Run `npm run build` to update the `dist` folder.
3. Go to `chrome://extensions/` and click the **Update** icon (circular arrow) on the extension card.

---
*HackUDC 2026 - Smart Brain*
