from main import SeedVelocityAnalyzer as vert

analyzer = vert("velocity_calculator/Vert_vel")
analyzer.threshold_images(thresh_val=28)
analyzer.subtract_images()
analyzer.compute_velocity(scale_factor=0.00075)
analyzer.plot_fits() 
analyzer.plot_filtered_fits(threshold=3, factor=1.5)
