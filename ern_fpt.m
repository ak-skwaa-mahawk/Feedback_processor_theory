% ern_fpt.m — Neural FPT
if abs(actual - expected) > threshold
    trigger_ern();  % C190 veto
    theta_burst();  % R-drop
end