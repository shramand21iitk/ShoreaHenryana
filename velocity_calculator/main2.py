import os
import cv2
import numpy as np
import openpyxl
import pandas as pd
import matplotlib.pyplot as plt

class FrontCamReadings:
    def __init__(self, thresh_val, input_path, bottom_limit, left_limit, right_limit, scale_factor, projected_area, mass, n_frame, n_frame_mv_av, fps):
        self.thresh_val = thresh_val
        self.bottom_limit = bottom_limit
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.scale_factor = scale_factor
        self.projected_area = projected_area
        self.mass = mass
        self.n_frame = n_frame
        self.n_frame_mv_av = n_frame_mv_av
        self.fps = fps
        self.input_path = input_path
        self.base_path = os.path.dirname(input_path)
        self.cropped_path = os.path.join(self.base_path, 'cropped')
        os.makedirs(self.cropped_path, exist_ok=True)
        self.threshold_path = os.path.join(self.base_path, 'threshold')
        os.makedirs(self.threshold_path, exist_ok=True)
        self.subtract_path = os.path.join(self.base_path, 'subtract')
        os.makedirs(self.subtract_path, exist_ok=True)
        self.data_path = os.path.join(self.base_path, 'data')
        os.makedirs(self.data_path, exist_ok=True)
        self.excel_path = os.path.join(self.data_path, 'DATA.xlsx')
        self.filt_excel_path = os.path.join(self.data_path, 'filtered_data.xlsx')
        self.mv_av_excel_path = os.path.join(self.data_path, 'mv_av_data.xlsx')
        self.plots_path = os.path.join(self.base_path, 'graphs')
        os.makedirs(self.plots_path, exist_ok=True)
        self.plot1 = os.path.join(self.plots_path, 'vert_vel_vs_time.png')
        self.plot2 = os.path.join(self.plots_path, 'drift_vs_time.png')
        self.plot3 = os.path.join(self.plots_path, 'drift_vel_vs_time.png')
        self.plot4 = os.path.join(self.plots_path, 'vert_vel_polyfits.png')
        self.plot5 = os.path.join(self.plots_path, 'drift_vel_polyfits.png')
        self.plot6 = os.path.join(self.plots_path, 'acc_vstime.png')
        self.plot7 = os.path.join(self.plots_path, 'acc_vs_vel.png')
        self.plot8 = os.path.join(self.plots_path, 'drag_vs_time.png')
        self.plot9 = os.path.join(self.plots_path, 'drag_vs_vel.png')
        self.plot10 = os.path.join(self.plots_path, 'cd_vs_time.png')
        self.plot11 = os.path.join(self.plots_path, 'cd_vs_vel.png')
        self.file1 = os.path.join(self.plots_path, 'vert_vel_poly_coeffs.txt')

    def crop_img(self):
        x1, y1 = self.left_limit, 0
        x2, y2 = self.right_limit, self.bottom_limit
        for filename in os.listdir(self.input_path):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
                continue
            input_path = os.path.join(self.input_path, filename)
            output_path = os.path.join(self.cropped_path, filename)
            img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                print(f"Could not open {filename}")
                continue
            if not (0 <= x1 < x2 <= img.shape[1] and 0 <= y1 < y2 <= img.shape[0]):
                continue
            cropped = img[y1:y2, x1:x2]
            cv2.imwrite(output_path, cropped)

    def thresh_img(self):
        for filename in os.listdir(self.cropped_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
                file_path = os.path.join(self.cropped_path, filename)
                img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                _, thresh = cv2.threshold(img, self.thresh_val, 255, cv2.THRESH_BINARY)
                normalized = cv2.normalize(thresh, None, 0, 255, cv2.NORM_MINMAX)
                cv2.imwrite(os.path.join(self.threshold_path, filename), normalized)
    
    def subtract_images(self):
        image_files = sorted([
            f for f in os.listdir(self.threshold_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif'))
        ])
        if not image_files:
            print("No images found for subtraction.")
            return
        ref_image_path = os.path.join(self.threshold_path, image_files[0])
        i1 = cv2.imread(ref_image_path)
        for filename in image_files:
            i2 = cv2.imread(os.path.join(self.threshold_path, filename))
            if i2 is None or i1 is None:
                continue
            i3 = cv2.subtract(i1, i2)
            cv2.imwrite(os.path.join(self.subtract_path, filename), i3)
            i1 = i2
        first_output_path = os.path.join(self.subtract_path, image_files[0])
        if os.path.exists(first_output_path):
            os.remove(first_output_path)

    def collect_data(self):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Sheet1'
        worksheet['A1'] = 'time(s)'
        worksheet['B1'] = 'vert_vel(m/s)'
        worksheet['C1'] = 'bottom_x(m)'
        worksheet['D1'] = 'bottom_y(m)'
        worksheet['E1'] = 'drift_x(m)'
        worksheet['F1'] = 'drift_velocity(m/s)'
        worksheet['G1'] = 'vertical_acceleration(m/s2)'
        worksheet['H1'] = 'drag(N)'
        worksheet['I1'] = 'Cd'
        index = 2
        for filename in sorted(os.listdir(self.subtract_path)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
                path = os.path.join(self.subtract_path, filename)
                im = cv2.imread(path)
                lower = None
                for i in range(self.bottom_limit-1, 0, -1):
                    for j in range(0, self.right_limit-self.left_limit):
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
                worksheet[f"B{index}"] = (lower[0] - upper[0]) * self.scale_factor * self.fps
                worksheet[f"C{index}"] = lower[1] * self.scale_factor
                worksheet[f"D{index}"] = lower[0] * self.scale_factor
                index += 1
        e2 = worksheet["C2"].value
        for i in range(2, index):
            ei = worksheet[f"C{i}"].value
            worksheet[f"E{i}"] = e2 - ei
            if i < index - 1:
                ei_1 = worksheet[f"C{i+1}"].value
                worksheet[f"F{i}"] = (ei_1 - ei) * self.fps 
        for i in range(3, index):
            val1 = worksheet[f"B{i}"].value
            val2 = worksheet[f"B{i-1}"].value
            worksheet[f"G{i}"] = (val1 - val2) / self.fps
        worksheet[f"G{2}"] = worksheet[f"G{3}"].value
        for i in range(2, index):
            worksheet[f"H{i}"] = self.mass*(9.81 - worksheet[f"G{i}"].value)
            worksheet[f"I{i}"] = (worksheet[f"H{i}"].value)/(0.5*1.225*((worksheet[f"B{i}"].value)**2))
        workbook.save(self.excel_path)
    

    def frame_mv_avg(self):
        veldf = pd.read_excel(self.excel_path, sheet_name='Sheet1')
        velocity = veldf['vert_vel(m/s)'].to_numpy()
        drift_velocity = veldf['drift_velocity(m/s)'].to_numpy()
        drift = veldf['drift_x(m)'].to_numpy()
        acc = veldf['vertical_acceleration(m/s2)'].to_numpy()
        drag = veldf['drag(N)'].to_numpy()
        cd = veldf['Cd'].to_numpy()
        s = np.size(velocity)
        avg_vel = np.zeros(s-(self.n_frame_mv_av-1))
        avg_drift_vel = np.zeros(s-(self.n_frame_mv_av-1))
        avg_drift = np.zeros(s-(self.n_frame_mv_av-1))
        time = np.zeros(s-(self.n_frame_mv_av-1))
        avg_acc = np.zeros(s-(self.n_frame_mv_av-1))
        avg_drag = np.zeros(s-(self.n_frame_mv_av-1))
        avg_cd = np.zeros(s-(self.n_frame_mv_av-1))
        for i in range(0, s-(self.n_frame_mv_av-1)):
            time[i] = ((i) + (self.n_frame_mv_av//2))/self.fps
            avg_vel[i] = np.mean(velocity[i:i+self.n_frame_mv_av])
            avg_drift_vel[i] = np.mean(drift_velocity[i:i+self.n_frame_mv_av])
            avg_drift[i] = np.mean(drift[i:i+self.n_frame_mv_av])
            avg_acc[i] = np.mean(acc[i:i+self.n_frame_mv_av])
            avg_drag[i] = np.mean(drag[i:i+self.n_frame_mv_av])
            avg_cd[i] = np.mean(cd[i:i+self.n_frame_mv_av])
        result_df = pd.DataFrame({
            'time_av(s)': time,
            'vert_vel_av(m/s)': avg_vel,
            'drift_vel_av(m/s)':avg_drift_vel,
            'drift_av(m)': avg_drift,
            'vertical_acceleration(m/s2)': avg_acc,
            'drag(N)': avg_drag,
            'Cd': avg_cd
            })
        result_df.to_excel(self.mv_av_excel_path, index=False)

    def plot(self, df, plot1, plot2, plot3, plot4, plot5, plot6, plot7, plot8, plot9, plot10, plot11, file1):
        time = df['time_av(s)'].to_numpy()
        vert_vel = df['vert_vel_av(m/s)'].to_numpy()
        drift = df['drift_av(m)'].to_numpy()
        drift_vel = df['drift_vel_av(m/s)'].to_numpy()
        acc = df['vertical_acceleration(m/s2)'].to_numpy()
        drag = df['drag(N)'].to_numpy()
        cd = df['Cd'].to_numpy()
        # 1) vert_vel vs time
        plt.figure()
        plt.plot(time, vert_vel, markersize=10, c='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Vertical Velocity (m/s)')
        plt.title('Vertical Velocity vs Time')
        plt.grid(True)
        plt.savefig(plot1, dpi=300)
        plt.close()
        # 2) drift vs time
        plt.figure()
        plt.plot(time, drift, markersize=10, c='green')
        plt.xlabel('Time (s)')
        plt.ylabel('Drift X (m)')
        plt.title('Drift vs Time')
        plt.grid(True)
        plt.savefig(plot2, dpi=300)
        plt.close()
        # 3) drift_vel vs time
        plt.figure()
        plt.plot(time, drift_vel, markersize=10, c='red')
        plt.xlabel('Time (s)')
        plt.ylabel('Drift Velocity (m/s)')
        plt.title('Drift Velocity vs Time')
        plt.grid(True)
        plt.savefig(plot3, dpi=300)
        plt.close()
        # 4) Polynomial fitting for vert_vel vs time
        coeffs_vert = {}
        plt.figure()
        plt.scatter(time, vert_vel, s=10, c='blue', label='Data')
        for deg in range(1, 5):
            coeffs = np.polyfit(time, vert_vel, deg)
            coeffs_vert[deg] = coeffs
            poly = np.poly1d(coeffs)
            plt.plot(time, poly(time), label=f'Degree {deg}')
            # Compute R^2
            y_pred = poly(time)
            ss_res = np.sum((vert_vel - y_pred) ** 2)
            ss_tot = np.sum((vert_vel - np.mean(vert_vel)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            # Build equation string
            eqn = " + ".join([
                f"{coef:.3g}x^{i}" if i != 0 else f"{coef:.3g}"
                for coef, i in zip(coeffs, range(deg, -1, -1))])
            # Annotate in top-left corner, shifting down for each degree
            plt.text(
                0, 1 - 0.04 * (deg - 1),
                f'Deg {deg}: {eqn}  (R²={r2:.4f})',
                transform=plt.gca().transAxes,
                fontsize=8,
                verticalalignment='top')
        plt.xlabel('Time (s)')
        plt.ylabel('Vertical Velocity (m/s)')
        plt.title('Vertical Velocity Polynomial Fits')
        plt.legend()
        plt.grid(True)
        plt.savefig(plot4, dpi=300)
        plt.close()
        # Save vertical velocity polynomial coefficients
        with open(file1, "w") as f:
            for deg, coeffs in coeffs_vert.items():
                f.write(f"Degree {deg}: {coeffs.tolist()}\n")
        # 5) Polynomial fitting for drift_vel vs time
        coeffs_drift_vel = {}
        plt.figure()
        plt.plot(time, drift_vel, markersize=30, c='red', label='Data')
        plt.xlabel('Time (s)')
        plt.ylabel('Drift Velocity (m/s)')
        plt.title('Drift Velocity Polynomial Fits')
        plt.legend()
        plt.grid(True)
        plt.savefig(plot5, dpi=300)
        plt.close()
        # 6) vert_acc vs time
        plt.figure()
        plt.plot(time, acc, markersize=10, c='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Vertical Acceleration (m2/s)')
        plt.title('Vertical Acceleration vs Time')
        plt.grid(True)
        plt.savefig(plot6, dpi=300)
        plt.close()
        # 7) vert_acc vs velocity
        plt.figure()
        plt.scatter(vert_vel, acc, s=30, c='blue', label='Data')
        coeffs_drift_vel = {}
        for deg in range(1, 5):
            coeffs = np.polyfit(vert_vel, acc, deg)
            coeffs_drift_vel[deg] = coeffs
            poly = np.poly1d(coeffs)
            plt.plot(vert_vel, poly(vert_vel), label=f'Degree {deg}')
            # Compute R^2
            y_pred = poly(vert_vel)
            ss_res = np.sum((acc - y_pred) ** 2)
            ss_tot = np.sum((acc - np.mean(acc)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            # Build equation string
            eqn = " + ".join([
                f"{coef:.3g}x^{i}" if i != 0 else f"{coef:.3g}"
                for coef, i in zip(coeffs, range(deg, -1, -1))])
            # Annotate in top-left corner, shifting down for each degree
            plt.text(
                0, 1 - 0.04 * (deg - 1),
                f'Deg {deg}: {eqn}  (R²={r2:.4f})',
                transform=plt.gca().transAxes,
                fontsize=8,
                verticalalignment='top')
        plt.xlabel('Vertical Velocity (m/s)')
        plt.ylabel('Vertical Acceleration (m2/s)')
        plt.title('Vertical Acceleration vs Vertical Velocity')
        plt.legend()
        plt.grid(True)
        plt.savefig(plot7, dpi=300)
        plt.close()
        # 8) drag vs time
        plt.figure()
        plt.plot(time, drag, markersize=10, c='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Drag (N)')
        plt.title('Drag vs Time')
        plt.grid(True)
        plt.savefig(plot8, dpi=300)
        plt.close()
        # 9) drag vs velocity
        plt.figure()
        plt.scatter(vert_vel, drag, s=30, c='blue', label='Data')
        coeffs_drift_vel = {}
        for deg in range(1, 5):
            coeffs = np.polyfit(vert_vel, drag, deg)
            coeffs_drift_vel[deg] = coeffs
            poly = np.poly1d(coeffs)
            plt.plot(vert_vel, poly(vert_vel), label=f'Degree {deg}')
            # Compute R^2
            y_pred = poly(vert_vel)
            ss_res = np.sum((drag - y_pred) ** 2)
            ss_tot = np.sum((drag - np.mean(drag)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            # Build equation string
            eqn = " + ".join([
                f"{coef:.3g}x^{i}" if i != 0 else f"{coef:.3g}"
                for coef, i in zip(coeffs, range(deg, -1, -1))])
            # Annotate in top-left corner, shifting down for each degree
            plt.text(
                0, 1 - 0.04 * (deg - 1),
                f'Deg {deg}: {eqn}  (R²={r2:.4f})',
                transform=plt.gca().transAxes,
                fontsize=8,
                verticalalignment='top')
        plt.xlabel('Vertical Velocity (m/s)')
        plt.ylabel('Drag (N)')
        plt.title('Drag vs Vertical Velocity')
        plt.legend()
        plt.grid(True)
        plt.savefig(plot9, dpi=300)
        plt.close()
        # 10) Cd vs time
        plt.figure()
        plt.plot(time, cd, markersize=10, c='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Drag Coefficient (Cd)')
        plt.title('Drag coefficient vs Time')
        plt.grid(True)
        plt.savefig(plot10, dpi=300)
        plt.close()
        # 11) Cd vs velocity
        plt.figure()
        plt.scatter(vert_vel, cd, s=10, c='blue', label='Data')
        coeffs_drift_vel = {}
        for deg in range(1, 5):
            coeffs = np.polyfit(vert_vel, cd, deg)
            coeffs_drift_vel[deg] = coeffs
            poly = np.poly1d(coeffs)
            plt.plot(vert_vel, poly(vert_vel), label=f'Degree {deg}')
            # Compute R^2
            y_pred = poly(vert_vel)
            ss_res = np.sum((cd - y_pred) ** 2)
            ss_tot = np.sum((cd - np.mean(cd)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            # Build equation string
            eqn = " + ".join([
                f"{coef:.3g}x^{i}" if i != 0 else f"{coef:.3g}"
                for coef, i in zip(coeffs, range(deg, -1, -1))])
            # Annotate in top-left corner, shifting down for each degree
            plt.text(
                0, 1 - 0.04 * (deg - 1),
                f'Deg {deg}: {eqn}  (R²={r2:.4f})',
                transform=plt.gca().transAxes,
                fontsize=8,
                verticalalignment='top')
        plt.xlabel('TVertical Velocity (m/s)')
        plt.ylabel('Drag Coefficient (Cd)')
        plt.title('Drag coefficient vs Vertical Velocity')
        plt.legend()
        plt.grid(True)
        plt.savefig(plot11, dpi=300)
        plt.close()

    def execute(self):
        self.crop_img()
        self.thresh_img()
        self.subtract_images()
        self.collect_data()
        self.frame_mv_avg()
        df = pd.read_excel(self.mv_av_excel_path)
        self.plot(df, 
                  self.plot1, 
                  self.plot2, 
                  self.plot3, 
                  self.plot4, 
                  self.plot5, 
                  self.plot6, 
                  self.plot7, 
                  self.plot8, 
                  self.plot9, 
                  self.plot10, 
                  self.plot11, 
                  self.file1)