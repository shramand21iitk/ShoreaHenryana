%the code runs though all the sheets of the given excel file, to plot all
%the variables in the columns and saves them
%%
filename = "D:\College\IITK\Seed37Cut3_diff.xlsx";   
sheetsToPlot = [];  

[~, allSheets] = xlsfinfo(filename);
if isempty(sheetsToPlot)
    sheetsToPlot = allSheets;
end

[~, baseName, ~] = fileparts(filename);
cutTag = regexprep(baseName, '.*_(cut\d+)$', '$1');
if isempty(cutTag)
    cutTag = 'uncategorized';
end

rootOutput = fullfile(pwd, 'Plots_AllCuts_ShramanSeeds');

for s = 1:numel(sheetsToPlot)
    sheetName = sheetsToPlot{s};

    try
       
        T = readtable(filename, 'Sheet', sheetName);
        data = T{:, 3:end};
        varNames = T.Properties.VariableNames(3:end);
        time = 1:size(data, 1);

        outputFolder = fullfile(rootOutput, cutTag, char(sheetName));
        if ~exist(outputFolder, 'dir')
            mkdir(outputFolder);
        end

        for j = 1:size(data, 2)
            fig = figure('Visible', 'off');
            plot(time, data(:, j), 'LineWidth', 1.8);
            title([sheetName ' - ' varNames{j}], 'Interpreter', 'none');
            xlabel('Time');
            ylabel(varNames{j});
            grid on;

            fileName = regexprep(varNames{j}, '\W', '_');
            saveas(fig, fullfile(outputFolder, [fileName '.png']));
            close(fig);
        end

        fprintf('Plots for "%s" saved in: %s\n', sheetName, outputFolder);

    catch ME
        fprintf('Skipped sheet "%s" (Error: %s)\n', sheetName, ME.message);
    end
end

disp('All selected sheets processed successfully!');

%%

% FINAL FILE
% For single-variable plots of forces.
%The data structure followed is for a given cut, one excel is made, and for
%each speed there are different sheets in same file. 

%filename = "D:\College\IITK\Data\Seed18Cut0_diff.xlsx";
%sheetName = "2mps";

%[~, baseName, ~] = fileparts(filename);
%cutTag = regexprep(baseName, '.*_(cut\d+)$', '$1');  
%if isempty(cutTag)
 %   cutTag = 'uncategorized'; 
%end


%T = readtable(filename, 'Sheet', sheetName);
%data = T{:, 3:end};
%varNames = T.Properties.VariableNames(3:end);


%time = 1:size(data, 1);


%rootOutput = fullfile(pwd, 'Plots_AllCuts_ShramanSeeds');
%outputFolder = fullfile(rootOutput, cutTag, char(sheetName));
%if exist(char(outputFolder), 'dir') == 0
   % mkdir(char(outputFolder));
%end

%% Plot and save each column
%for j = 1:size(data, 2)
   % fig = figure('Visible', 'off');
   % plot(time, data(:, j), 'LineWidth', 1.8)
   % title([sheetName ' - ' varNames{j}], 'Interpreter', 'none')
   % xlabel('Time')
   % ylabel(varNames{j})
   % grid on
    
   % fileName = regexprep(varNames{j}, '\W', '_'); 
   % saveas(fig, fullfile(outputFolder, [fileName '.png']));
    %close(fig)
%end

%disp(['Plots for ' sheetName ' saved in: ' outputFolder])

