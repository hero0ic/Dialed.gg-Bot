# Dialed.gg Bot

> A Python bot that can consistently achieve near-perfect scores on dialed.gg by capturing the target color from the screen and recreating it using automated slider controls.

---

![Demo](https://github.com/user-attachments/assets/5057ba60-f760-4b4f-99cc-216cc3ef7e47)

---

## ⚙️ How it works

1. **Calibration**
   - User selects screen positions (color preview + sliders)

2. **Capture**
   - App reads pixel color during preview phase

3. **Convert**
   - RGB → HSV using `colorsys`

4. **Detect transition**
   - Monitors pixel change to detect when preview phase ends

5. **Apply**
   - Maps HSV values to slider positions and adjusts them automatically

---

## 🖥️ Calibration Guide
To set up the bot, complete the calibration process by hovering over each required position and pressing **Enter**. For optimal accuracy, closely follow the positions shown in the calibration guide below.


**Step 1.** Hover over the CENTER of the color swatch

<img width="500" height="500" alt="Calibration_1" src="https://github.com/user-attachments/assets/e7f5b04d-415f-43de-ac20-0e3df80ab989" />

**Step 2.** Hover over the TOP of the hue slider

<img width="500" height="500" alt="Calibration_2" src="https://github.com/user-attachments/assets/8ee6a4b1-d0a4-4ec9-8329-76a70b190866" />

**Step 3.** Hover over the BOTTOM of the hue slider

<img width="500" height="500" alt="Calibration_3" src="https://github.com/user-attachments/assets/6426f2bf-3153-4c00-aba3-a7669fe7ec7d" />

**Step 4.** Hover ANYWHERE over the saturation slider

<img width="500" height="500" alt="Calibration_4" src="https://github.com/user-attachments/assets/0a365d44-cd96-4ea0-8365-89ef1ab224a0" />

**Step 5.** Hover ANYWHERE over the brightness slider

<img width="500" height="500" alt="Calibration_5" src="https://github.com/user-attachments/assets/ef3b8f28-ee80-4470-8520-9824d25b5033" />

---

## 🚀 Usage
*See the demo for help if needed*
1. Launch `dialed-bot.exe`
2. Complete the calibration
3. Start a game and wait for the preview phase
4. When the preview phase begins, run the bot with the game window open
5. Repeat steps 3 and 4 each round
