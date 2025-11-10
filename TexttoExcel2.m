%for converting the text file obtained from load cell data, to excel sheet
%for processing 

inputFolder = "D:\College\IITK\Data\seed37\cut3";   
outputFile = "D:\College\IITK\Data\seed37_cut3.xlsx";  


txtFiles = dir(fullfile(inputFolder, '*.txt')); 
fprintf('Found %d text files in %s\n', numel(txtFiles), inputFolder);

if isempty(txtFiles)
    error('No .txt files found in the specified folder.');
end



for i = 1:numel(txtFiles)
   
    filePath = fullfile(inputFolder, txtFiles(i).name);

    opts = detectImportOptions(filePath);
    data = readtable(filePath, opts);

   
    [~, sheetName, ~] = fileparts(txtFiles(i).name);
    sheetName = matlab.lang.makeValidName(sheetName);

    
    writetable(data, outputFile, 'Sheet', sheetName);

    fprintf('Added %s as sheet "%s"\n', txtFiles(i).name, sheetName);
end

fprintf('\n All text files successfully combined into %s\n', outputFile);
