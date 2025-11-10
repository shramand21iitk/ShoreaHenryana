
fileA = "D:\College\IITK\Data\Cal_data.xlsx";     % Excel file A (to subtract)
fileB = "D:\College\IITK\Data\seed37_cut3.xlsx";     % Excel file B
outputFile = "D:\College\IITK\Seed37Cut3_diff.xlsx"; 
 
[~, sheetsA] = xlsfinfo(fileA);
[~, sheetsB] = xlsfinfo(fileB);

for i = 1:numel(sheetsB)
    sheetName = sheetsB{i};
    fprintf('\nProcessing sheet: %s ...\n', sheetName);

  
    if ~ismember(sheetName, sheetsA)
        fprintf('Sheet "%s" not found in A. Skipping.\n', sheetName);
        continue;
    end

  
    T1 = readtable(fileA, 'Sheet', sheetName);
    T2 = readtable(fileB, 'Sheet', sheetName);

    if ~isequal(T1.Properties.VariableNames, T2.Properties.VariableNames)
        fprintf('Columns differ in "%s". Skipping.\n', sheetName);
        continue;
    end

    Tdiff = T1;

    for j = 1:width(T1)
        colA = T1{:, j};
        colB = T2{:, j};

        if iscell(colA), colA = str2double(colA); end
        if iscell(colB), colB = str2double(colB); end

        if isnumeric(colA) && isnumeric(colB)
            try
                Tdiff{:, j} = colB - colA;
            catch
                fprintf('Skipping column "%s" (non-numeric values).\n', T1.Properties.VariableNames{j});
            end
        else
            fprintf('Skipping column "%s" (not numeric).\n', T1.Properties.VariableNames{j});
        end
    end

    if i == 1
        writetable(Tdiff, outputFile, 'Sheet', sheetName);
    else
        writetable(Tdiff, outputFile, 'Sheet', sheetName, 'WriteMode', 'append');
    end

    fprintf('Sheet "%s" processed successfully.\n', sheetName);
end

disp('All available sheets processed and saved!');
