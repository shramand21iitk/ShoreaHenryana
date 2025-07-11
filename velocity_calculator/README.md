# Velocity Calculator

This project provides a modular Python class `SeedVelocityAnalyzer` for processing image sequences of falling seeds to compute vertical velocity and drift. It includes thresholding, frame differencing, velocity extraction, outlier filtering, and polynomial curve fitting — all in one reusable package. This was done as a part of a larger research on autorotating seeds. 

---

# 📄 License & Intellectual Property

This code is the intellectual property of **Shraman Das** and his supervisor **Professor Debopam Das**, Unsteady Aerodynamics Lab, **IIT Kanpur**.

Unauthorized commercial use, reproduction, or redistribution of this code or any part of it is strictly prohibited without explicit written permission from the authors.

You are free to modify and use the code for **non-commercial academic purposes**, provided that proper credit is given.


---

## 📁 Folder Structure

your_project/
├── main.py # Contains SeedVelocityAnalyzer class
├── example.py # Example usage script
├── Vert_vel/ # Raw grayscale image sequence
├── thresholded_seeds/ # Auto-generated thresholded images
├── subtracted/ # Auto-generated frame difference images
├── velocity.xlsx # Output Excel file with velocity & drift
├── plots/ # Auto-generated plots (velocity, drift, filtered fits)
└── README.md # You're here

---

## 🔧 Requirements

- Python 3.7+
- OpenCV (`opencv-python`)
- NumPy
- pandas
- matplotlib
- openpyxl

Install dependencies:
```bash
pip install opencv-python numpy pandas matplotlib openpyxl
```

# 🚀 Example Usage
```
from main import SeedVelocityAnalyzer as vert

analyzer = vert("velocity_calculator/Vert_vel")
analyzer.threshold_images(thresh_val=28)
analyzer.subtract_images()
analyzer.compute_velocity(scale_factor=0.5)
analyzer.plot_fits() 
analyzer.plot_filtered_fits(threshold=3, factor=1.5)
```
Apply the threshold value by manually checking the seed images
The scaling factor has to be applied based on the size the object is scaled by in the image

## Run the script
```
python example.py
```

# 🧠 Features
### threshold_images(thresh_val=28)
Applies binary thresholding to each grayscale image and saves the results to thresholded_seeds.

### subtract_images()
Performs sequential image subtraction using the first frame as reference and saves results to subtracted. Deletes the first subtraction result.

### compute_velocity(scale_factor=0.5)
Extracts vertical velocity and horizontal drift from the white trail in the subtracted images. Saves to velocity.xlsx.

### plot_fits()
Generates and saves plots of vertical velocity and drift vs. time with polynomial fits (1st–4th degree).

### plot_filtered_fits(threshold=3, factor=1.5)
Filters velocity data using Z-score and IQR methods, then fits and saves polynomial curves (1st–5th degree) for comparison.


# 📊 Output
All plots are saved under the plots/ directory:
1. velocity_fit.png
2. drift_fit.png
3. filtered_fits.png

Excel data is saved in velocity.xlsx.


# 📬 Contact
Created by Shraman Das (IIT Kanpur)
For questions or contributions, feel free to reach out or submit a pull request.