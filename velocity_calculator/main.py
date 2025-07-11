import os
import cv2
import numpy as np
import openpyxl
import pandas as pd
import matplotlib.pyplot as plt


class SeedVelocityAnalyzer:
    def __init__(self, raw_path):
        self.raw_path = raw_path
        self.base_path = os.path.dirname(raw_path)
        self.thresh_path = os.path.join(self.base_path, 'thresholded_seeds')
        self.subtracted_path = os.path.join(self.base_path, 'subtracted')
        self.excel_path = os.path.join(self.base_path, 'velocity.xlsx')
        self.plots_path = os.path.join(self.base_path, 'plots')
        os.makedirs(self.plots_path, exist_ok=True)


    def threshold_images(self, thresh_val=28):
        os.makedirs(self.thresh_path, exist_ok=True)
        for filename in os.listdir(self.raw_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
                file_path = os.path.join(self.raw_path, filename)
                img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                _, thresh = cv2.threshold(img, thresh_val, 255, cv2.THRESH_BINARY)
                normalized = cv2.normalize(thresh, None, 0, 255, cv2.NORM_MINMAX)
                cv2.imwrite(os.path.join(self.thresh_path, filename), normalized)


    def subtract_images(self):
        os.makedirs(self.subtracted_path, exist_ok=True)
        # Sort and get the list of images
        image_files = sorted([
            f for f in os.listdir(self.thresh_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif'))
        ])
        if not image_files:
            print("No images found for subtraction.")
            return
        # Use the first image as the initial reference
        ref_image_path = os.path.join(self.thresh_path, image_files[0])
        i1 = cv2.imread(ref_image_path)
        for filename in image_files:
            i2 = cv2.imread(os.path.join(self.thresh_path, filename))
            if i2 is None or i1 is None:
                continue
            i3 = cv2.subtract(i1, i2)
            cv2.imwrite(os.path.join(self.subtracted_path, filename), i3)
            i1 = i2
        # Remove the first subtracted image
        first_output_path = os.path.join(self.subtracted_path, image_files[0])
        if os.path.exists(first_output_path):
            os.remove(first_output_path)


    def compute_velocity(self, scale_factor=0.5):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Sheet1'
        worksheet['A1'] = 'time(s)'
        worksheet['B1'] = 'vert_vel(m/s)'
        worksheet['C1'] = 'drift(px)'
        index = 2
        for filename in sorted(os.listdir(self.subtracted_path)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
                path = os.path.join(self.subtracted_path, filename)
                im = cv2.imread(path)
                lower = None
                for i in range(920, 0, -1):
                    for j in range(640, 760):
                        if np.array_equal(im[i, j], [255, 255, 255]):
                            lower = [i, j]
                            break
                    if lower:
                        break
                if not lower:
                    continue
                upper = next(([k, lower[1]] for k in range(lower[0], 0, -1)
                              if np.array_equal(im[k, lower[1]], [0, 0, 0])), [0, lower[1]])
                worksheet[f"A{index}"] = index - 1
                worksheet[f"B{index}"] = (lower[0] - upper[0]) * scale_factor
                worksheet[f"C{index}"] = lower[1]
                index += 1
        workbook.save(self.excel_path)


    def plot_fits(self):
        data = pd.read_excel(self.excel_path)
        x = data['time(s)']
        y_vel = data['vert_vel(m/s)']
        y_drift = data['drift(px)']
        def plot_and_save(x, y, ylabel, title, filename):
            plt.figure()
            plt.scatter(x, y, label='Data points')
            colors = ['red', 'green', 'blue', 'purple']
            labels = ['Linear fit', '2nd poly fit', '3rd poly fit', '4th poly fit']
            for degree in range(1, 5):
                coeffs = np.polyfit(x, y, degree)
                poly_fit = np.poly1d(coeffs)
                plt.plot(x, poly_fit(x), color=colors[degree - 1], label=labels[degree - 1])
            plt.xlabel("time(s)")
            plt.ylabel(ylabel)
            plt.title(title)
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(self.plots_path, filename))
            plt.close()
        plot_and_save(x, y_vel, "vert_vel(m/s)", "Vertical Velocity vs Time", "velocity_fit.png")
        plot_and_save(x, y_drift, "drift(px)", "Drift vs Time", "drift_fit.png")



    def plot_filtered_fits(self, threshold=3, factor=1.5):
        data = pd.read_excel(self.excel_path)
        zscore_data = self._remove_outliers_zscore(data, threshold)
        iqr_data = self._remove_outliers_iqr(data, factor)
        time_z, vel_z = zscore_data['time(s)'], zscore_data['vert_vel(m/s)']
        time_iqr, vel_iqr = iqr_data['time(s)'], iqr_data['vert_vel(m/s)']
        plt.figure(figsize=(10, 6))
        plt.scatter(time_z, vel_z, color='black', label='Z-score filtered data')
        plt.scatter(time_iqr, vel_iqr, color='gray', label='IQR filtered data', alpha=0.7)
        colors = ['blue', 'green', 'red', 'purple', 'orange']
        for degree in range(1, 6):
            coeffs_z = np.polyfit(time_z, vel_z, degree)
            coeffs_i = np.polyfit(time_iqr, vel_iqr, degree)
            plt.plot(time_z, np.polyval(coeffs_z, time_z), linestyle='--', color=colors[degree - 1], label=f'Z-score deg {degree}')
            plt.plot(time_iqr, np.polyval(coeffs_i, time_iqr), linestyle='-', color=colors[degree - 1], alpha=0.7, label=f'IQR deg {degree}')
        plt.xlabel("Time(s)")
        plt.ylabel("Velocity(m/s)")
        plt.title("Velocity vs Time with Polynomial Fits (Z-score & IQR)")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(self.plots_path, "filtered_fits.png"))
        plt.close()



    def _remove_outliers_zscore(self, df, threshold=3):
        z_scores = np.abs((df['vert_vel(m/s)'] - df['vert_vel(m/s)'].mean()) / df['vert_vel(m/s)'].std())
        return df[z_scores < threshold].sort_values(by='time(s)')


    def _remove_outliers_iqr(self, df, factor=1.5):
        Q1 = df['vert_vel(m/s)'].quantile(0.25)
        Q3 = df['vert_vel(m/s)'].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - factor * IQR
        upper = Q3 + factor * IQR
        return df[(df['vert_vel(m/s)'] >= lower) & (df['vert_vel(m/s)'] <= upper)].sort_values(by='time(s)')