function plot_rf_owc_metrics(outputDir)
%PLOT_RF_OWC_METRICS Plot synthetic RF-OWC policy metrics exported by Python.
% Usage:
%   addpath('matlab')
%   plot_rf_owc_metrics('outputs')

if nargin < 1
    outputDir = 'outputs';
end

resultsDir = fullfile(outputDir, 'results');
figuresDir = fullfile(outputDir, 'figures');
if ~exist(figuresDir, 'dir')
    mkdir(figuresDir);
end

comparison = readtable(fullfile(resultsDir, 'synthetic_policy_comparison.csv'));

figure('Name', 'RF-OWC service satisfaction');
bar(categorical(comparison.policy), comparison.mean_service_satisfaction);
ylabel('Mean service satisfaction');
title('Synthetic RF-OWC orchestration policies');
grid on;
saveas(gcf, fullfile(figuresDir, 'matlab_service_satisfaction.png'));

figure('Name', 'RF-OWC utilization');
bar(categorical(comparison.policy), comparison.owc_utilization);
ylabel('OWC utilization share');
title('Synthetic OWC utilization by policy');
grid on;
saveas(gcf, fullfile(figuresDir, 'matlab_owc_utilization.png'));
end
