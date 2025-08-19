from main2 import FrontCamReadings as fcr

analyzer = fcr(thresh_val=28, 
               input_path=r'velocity_calculator/Vert_vel', 
               bottom_limit=920, 
               left_limit=600, 
               right_limit=750, 
               scale_factor=0.00075, 
               projected_area=0.0005, 
               mass=0.0008, 
               n_frame=30,
               n_frame_mv_av=100,
               fps = 500)
analyzer.execute()