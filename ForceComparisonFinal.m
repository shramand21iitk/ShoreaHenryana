%final code for force comparisons 
%After specifying the input file and coumns to be plotted, code saves the
%plots to the output folder (given by user) 

%% 
%to be specified by user 
excelFile = "D:\College\IITK\Seed37Cut3_diff.xlsx";          
columnsToPlot = {'ForceX', 'ForceY', 'ForceZ', 'TorqueX', 'TorqueY', 'TorqueZ'};         
outputFolder = 'Plots_AllCuts_ShramanSeeds';                       
seedTag = '_Seed37_Cut3';                          

%%

if ~exist(outputFolder, 'dir')
    mkdir(outputFolder);
end

sheetNames = sheetnames(excelFile);


for c = 1:length(columnsToPlot)
    columnName = columnsToPlot{c};
    figure;
    hold on;

    
    for i = 1:length(sheetNames)
        data = readtable(excelFile, 'Sheet', sheetNames{i});

        % Check if the desired column exists
        if ismember(columnName, data.Properties.VariableNames)
            y = data.(columnName);
            x = 1:length(y);

           
            plot(x, y, 'LineWidth', 1.5, 'DisplayName', sheetNames{i});
        else
            warning('Column "%s" not found in sheet "%s"', columnName, sheetNames{i});
        end
    end

    xlabel('Time');
    ylabel(columnName);
    title(['' columnName ' Across All Speeds']);
    grid on;
    axis tight;
    set(gca, 'FontSize', 12);
    legend('show', 'Location', 'eastoutside', 'FontSize', 10);

    outputFilename = fullfile(outputFolder, [columnName seedTag]);
    %saveas(gcf, [outputFilename '.png']);
    savefig([outputFilename '.fig']);
  
    %exportgraphics(gcf, [outputFilename '.pdf'], 'ContentType', 'vector');

    disp([' Saved: ' outputFilename ' .fig']);
end
