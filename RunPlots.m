
params = struct();
params.Filename     = 'drag_data.xlsx';         
params.SheetName    = 'cut.2';
params.OutputFolder = fullfile(pwd, 'plots');  %can create folder if doesnt already exists  
params.ColumnRange  = 1:6; %can remove this step if the sheets are saved according to the speeds 
params.YLabels      = {'F(x)', 'F(y)', 'F(z)', 'T(x)', 'T(y)', 'T(z)'};
params.XLabel       = 'Time';
params.Format       = 'png';


dp = DataPlotter(params);
dp.readData();
dp.plotAll();