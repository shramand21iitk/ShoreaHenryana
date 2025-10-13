classdef DataPlotter
    properties
        Filename       
        SheetName       
        OutputFolder    
        ColumnRange     
        YLabels        
        XLabel = 'Time' 
        Format = 'png'  
        XData           
        YData           
    end

    methods
        function obj = DataPlotter(params)
            if nargin == 0
                return; % empty object; user will set inputs via setInputs
            end
            obj = obj.setInputs(params);
        end
%%
        function obj = setInputs(obj, params)
            if isstruct(params)
                fn = fieldnames(params);
                for k = 1:numel(fn)
                    name = fn{k};
                    if isprop(obj, name)
                        obj.(name) = params.(name);
                    end
                end
            elseif iscell(params)
                for k = 1:2:numel(params)
                    name = params{k};
                    val  = params{k+1};
                    if isprop(obj, name)
                        obj.(name) = val;
                    end
                end
            else
                error('params must be a struct or name-value cell array.');
            end

          
            if isempty(obj.Filename)
                error('Filename must be provided (full path or relative).');
            end
            if isempty(obj.SheetName)
                error('SheetName must be provided.');
            end
            if isempty(obj.OutputFolder)
                error('OutputFolder must be provided.');
            end
            if isempty(obj.ColumnRange)
                error('ColumnRange must be provided, e.g., 29:34.');
            end
            if isempty(obj.YLabels)
                error('YLabels must be provided as a cell array of labels.');
            end
            if ~exist(obj.OutputFolder, 'dir')
                mkdir(obj.OutputFolder);
            end
        end

        %% 
        function obj = readData(obj)
            try
                opts = detectImportOptions(obj.Filename, 'Sheet', obj.SheetName);
                T = readtable(obj.Filename, opts, 'Sheet', obj.SheetName);
            catch ME
                error('Error reading file/sheet: %s', ME.message);
            end

            try
                obj.YData = T{:, obj.ColumnRange};
            catch
                error('Unable to extract the specified ColumnRange from the sheet. Check indices.');
            end 
            if ~isnumeric(obj.YData)
               
                if iscell(obj.YData)
                    obj.YData = cellfun(@(c) double(c), obj.YData);
                else
                    error('YData is not numeric. Check your sheet cells.');
                end
            end

           
            nrows = size(obj.YData, 1);
            obj.XData = (1:nrows)';

            if numel(obj.YLabels) ~= size(obj.YData, 2)
                error('Number of YLabels (%d) does not match number of data columns (%d).', ...
                      numel(obj.YLabels), size(obj.YData, 2));
            end
        end

        %% 
        function plotAll(obj)
            if isempty(obj.YData)
                obj = obj.readData();
            end

          
            ncols = size(obj.YData, 2);
            for i = 1:ncols
                f = figure('Visible', 'off');
                plot(obj.XData, obj.YData(:, i), 'LineWidth', 1.8);
                grid on;
                xlabel(obj.XLabel, 'FontSize', 12, 'FontWeight', 'bold');
                ylabel(obj.YLabels{i}, 'FontSize', 12, 'FontWeight', 'bold');
                title(sprintf('%s - %s vs %s', obj.SheetName, obj.YLabels{i}, obj.XLabel), ...
                      'FontSize', 14, 'FontWeight', 'bold');

                % build filename safe string for sheet
                safeSheet = matlab.lang.makeValidName(obj.SheetName);
                saveName = fullfile(obj.OutputFolder, sprintf('%s_Col%d.%s', safeSheet, i, obj.Format));
                try
                    saveas(f, saveName);
                catch ME
                    warning('Failed to save %s: %s', saveName, ME.message);
                end
                close(f);
            end

            fprintf('Saved %d plots to: %s\n', ncols, obj.OutputFolder);
        end

        %% 
        function run(obj)
            obj = obj.readData();
            obj.plotAll();
        end
    end
end
