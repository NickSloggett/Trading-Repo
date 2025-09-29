#include "sierrachart.h"

/*==========================================================================*/
// Basic Indicator Template for Sierra Chart
// 
// This template provides a starting point for creating custom indicators
// Copy this file and modify for your specific needs
//
// Author: Trading-Repo
// Version: 1.0
/*==========================================================================*/

SCDLLName("Basic Indicator Template")

/*==========================================================================*/
SCSFExport scsf_BasicIndicatorTemplate(SCStudyInterfaceRef sc)
{
    // ===== SUBGRAPH DECLARATIONS =====
    // Subgraphs are the output lines/values displayed on the chart
    SCSubgraphRef Subgraph_Main = sc.Subgraph[0];
    SCSubgraphRef Subgraph_Signal = sc.Subgraph[1];
    SCSubgraphRef Subgraph_Upper = sc.Subgraph[2];
    SCSubgraphRef Subgraph_Lower = sc.Subgraph[3];
    
    // ===== INPUT DECLARATIONS =====
    // Inputs are the parameters users can configure
    SCInputRef Input_Length = sc.Input[0];
    SCInputRef Input_MovAvgType = sc.Input[1];
    SCInputRef Input_Multiplier = sc.Input[2];
    SCInputRef Input_PriceType = sc.Input[3];
    
    // ===== CONFIGURATION SECTION =====
    // This section runs once when the study is first added to a chart
    if (sc.SetDefaults)
    {
        // Study identification
        sc.GraphName = "Basic Indicator Template";
        sc.StudyDescription = "Template for creating custom indicators. Modify this description.";
        
        // Study settings
        sc.AutoLoop = 1;  // Automatic looping through bars
        sc.GraphRegion = 0;  // 0 = main chart, 1 = separate panel below
        sc.CalculationPrecedence = STD_PREC_LEVEL;  // Calculation order
        
        // Subgraph configuration
        Subgraph_Main.Name = "Main Line";
        Subgraph_Main.DrawStyle = DRAWSTYLE_LINE;
        Subgraph_Main.PrimaryColor = RGB(0, 255, 0);  // Green
        Subgraph_Main.LineWidth = 2;
        Subgraph_Main.DrawZeros = false;
        
        Subgraph_Signal.Name = "Signal Line";
        Subgraph_Signal.DrawStyle = DRAWSTYLE_LINE;
        Subgraph_Signal.PrimaryColor = RGB(255, 0, 0);  // Red
        Subgraph_Signal.LineWidth = 1;
        Subgraph_Signal.DrawZeros = false;
        
        Subgraph_Upper.Name = "Upper Band";
        Subgraph_Upper.DrawStyle = DRAWSTYLE_LINE;
        Subgraph_Upper.PrimaryColor = RGB(128, 128, 128);  // Gray
        Subgraph_Upper.LineWidth = 1;
        Subgraph_Upper.LineStyle = LINESTYLE_DOT;
        Subgraph_Upper.DrawZeros = false;
        
        Subgraph_Lower.Name = "Lower Band";
        Subgraph_Lower.DrawStyle = DRAWSTYLE_LINE;
        Subgraph_Lower.PrimaryColor = RGB(128, 128, 128);  // Gray
        Subgraph_Lower.LineWidth = 1;
        Subgraph_Lower.LineStyle = LINESTYLE_DOT;
        Subgraph_Lower.DrawZeros = false;
        
        // Input configuration
        Input_Length.Name = "Length";
        Input_Length.SetInt(14);
        Input_Length.SetIntLimits(1, 1000);
        Input_Length.SetDescription("Number of bars to use in calculation");
        
        Input_MovAvgType.Name = "Moving Average Type";
        Input_MovAvgType.SetMovAvgType(MOVAVGTYPE_SIMPLE);
        Input_MovAvgType.SetDescription("Type of moving average to use");
        
        Input_Multiplier.Name = "Multiplier";
        Input_Multiplier.SetFloat(2.0f);
        Input_Multiplier.SetFloatLimits(0.1f, 10.0f);
        Input_Multiplier.SetDescription("Multiplier for bands calculation");
        
        Input_PriceType.Name = "Price Type";
        Input_PriceType.SetCustomInputStrings("Close;Open;High;Low;HL/2;HLC/3;HLCC/4;OHLC/4");
        Input_PriceType.SetCustomInputIndex(0);
        Input_PriceType.SetDescription("Price data to use");
        
        return;
    }
    
    // ===== CALCULATION SECTION =====
    // This section runs for each bar (when AutoLoop = 1)
    // sc.Index is the current bar being processed
    
    // Get input values
    int Length = Input_Length.GetInt();
    int MovAvgType = Input_MovAvgType.GetMovAvgType();
    float Multiplier = Input_Multiplier.GetFloat();
    int PriceType = Input_PriceType.GetIndex();
    
    // Ensure we have enough data
    if (sc.Index < Length - 1)
        return;
    
    // Get price data based on user selection
    SCFloatArrayRef PriceArray = sc.BaseDataIn[PriceType];
    
    // ===== EXAMPLE CALCULATION: Moving Average with Bands =====
    
    // Calculate moving average
    sc.MovingAverage(PriceArray, Subgraph_Main, MovAvgType, Length);
    
    // Calculate standard deviation for bands
    float Sum = 0;
    float Avg = Subgraph_Main[sc.Index];
    
    for (int i = 0; i < Length; i++)
    {
        int Index = sc.Index - i;
        if (Index >= 0)
        {
            float Diff = PriceArray[Index] - Avg;
            Sum += Diff * Diff;
        }
    }
    
    float StdDev = sqrt(Sum / Length);
    
    // Calculate upper and lower bands
    Subgraph_Upper[sc.Index] = Avg + (StdDev * Multiplier);
    Subgraph_Lower[sc.Index] = Avg - (StdDev * Multiplier);
    
    // Calculate signal line (moving average of main line)
    sc.MovingAverage(Subgraph_Main, Subgraph_Signal, MovAvgType, Length / 2);
    
    // ===== OPTIONAL: Alert Conditions =====
    
    // Example: Alert when price crosses above upper band
    if (sc.Index > 0)
    {
        if (sc.Close[sc.Index] > Subgraph_Upper[sc.Index] &&
            sc.Close[sc.Index - 1] <= Subgraph_Upper[sc.Index - 1])
        {
            sc.SetAlert(1, "Price crossed above upper band");
        }
        
        // Alert when price crosses below lower band
        if (sc.Close[sc.Index] < Subgraph_Lower[sc.Index] &&
            sc.Close[sc.Index - 1] >= Subgraph_Lower[sc.Index - 1])
        {
            sc.SetAlert(2, "Price crossed below lower band");
        }
    }
    
    // ===== OPTIONAL: Background Coloring =====
    
    // Color background when price is above/below bands
    if (sc.Close[sc.Index] > Subgraph_Upper[sc.Index])
    {
        sc.DataStartIndex = sc.Index;  // Required for background colors
        int TransparentLevel = 90;  // 0-100, higher = more transparent
        Subgraph_Main.DataColor[sc.Index] = sc.GetStudyLineColor(0, TransparentLevel);
    }
}

/*==========================================================================*/
// NOTES AND TIPS:
//
// 1. AutoLoop vs Manual Loop:
//    - AutoLoop = 1: Sierra Chart automatically calls this function for each bar
//    - AutoLoop = 0: You must manually loop through bars
//
// 2. Persistent Variables:
//    - Use sc.GetPersistentInt(), sc.GetPersistentFloat() for state between calls
//    - Example: int& MyVar = sc.GetPersistentInt(1);
//
// 3. Built-in Functions:
//    - sc.SimpleMovAvg(), sc.ExponentialMovAvg(), sc.RSI(), sc.MACD()
//    - Use built-in functions when possible - they're optimized
//
// 4. Performance:
//    - Minimize calculations inside loops
//    - Use sc.GetCalculationStartIndexForStudy() to avoid recalculating old bars
//    - Cache frequently accessed values
//
// 5. Debugging:
//    - sc.AddMessageToLog("Debug message", 0);
//    - Use subgraphs to display intermediate values
//
// 6. Multiple Timeframes:
//    - Use sc.GetChartBaseData() to access other chart data
//    - See ACSIL documentation for examples
//
/*==========================================================================*/
