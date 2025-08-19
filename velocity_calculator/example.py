from main import SeedVelocityAnalyzer as vert

analyzer = vert("ShoreaHenryana/velocity_calculator/Vert_vel")
analyzer.threshold_images(thresh_val=28)
analyzer.subtract_images()
analyzer.compute_velocity(scale_factor=0.00075, lower_limit=920, left_limit=640, right_limit=760)
analyzer.five_point_moving_avg()
analyzer.plot_fits() 
analyzer.plot_filtered_fits(threshold=3, factor=1.5)
analyzer.frame_mv_avg(n_frame=5)
analyzer.calc_drag(mass = 0.0008, p_area = 0.0005)