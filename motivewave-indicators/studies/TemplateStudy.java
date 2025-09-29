package com.motivewave.platform.sdk.study;

import com.motivewave.platform.sdk.common.*;
import com.motivewave.platform.sdk.common.desc.*;
import com.motivewave.platform.sdk.study.*;

@StudyHeader(
    namespace = "com.tradingrepo",
    id = "TEMPLATESTUDY",
    version = 1,
    label = "Template Study",
    desc = "A template for custom MotiveWave studies - Simple Moving Average"
)
public class TemplateStudy extends Study {
    
    @Override
    public void initialize(Defaults defaults) {
        var settings = getSettings();
        settings.addIntegerSetting("length", 14, 1, 999, 1, "Length", "The period for the moving average");
        
        var sd = createStudyDescriptor();
        sd.setMinBars(20);
        sd.setLabelSettings("length");
        var maSetting = settings.getSetting("length");
        var output = sd.getOutputDescriptor(0);
        output.setSetting(maSetting);
        output.setLabel("MA");
        output.setColor(defaults.getLineColor(0));
        output.setLineWidth(2);
    }
    
    @Override
    protected void calculate(int index, DataContext ctx) {
        int length = getSettings().getInteger("length", 14);
        if (index < length - 1) return;
        
        DataSeries series = ctx.getDataSeries();
        double sum = 0.0;
        for (int i = 0; i < length; i++) {
            sum += series.getClose(index - i);
        }
        double ma = sum / length;
        
        series.setDouble(index, 0, ma);
        series.setComplete(index, true);
    }
}

