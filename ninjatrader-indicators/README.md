# NinjaTrader C# Indicators and Strategies

This directory contains C# code for custom indicators, strategies, and add-ons for NinjaTrader 8.

## Overview

NinjaTrader uses C# for developing custom studies, automated strategies, and platform extensions. This provides a powerful, object-oriented approach to creating sophisticated trading tools.

## Structure

```
ninjatrader-indicators/
├── Indicators/                 # Custom indicators
│   ├── AdvancedVolumeProfile.cs
│   ├── OrderFlowImbalance.cs
│   ├── CustomMACD.cs
│   └── SmartMoneyIndex.cs
├── Strategies/                 # Automated trading strategies
│   ├── MeanReversionStrategy.cs
│   ├── BreakoutStrategy.cs
│   ├── ScalpingStrategy.cs
│   └── TrendFollowing.cs
├── AddOns/                     # Platform add-ons
│   ├── TradeManager.cs         # Advanced order management
│   ├── RiskCalculator.cs       # Position sizing
│   └── Dashboard.cs            # Custom dashboard
├── Templates/                  # Code templates
│   ├── BasicIndicator.cs       # Basic indicator template
│   ├── BasicStrategy.cs        # Basic strategy template
│   └── AddOnTemplate.cs        # Add-on template
├── Shared/                     # Shared utilities
│   ├── Utilities.cs            # Helper functions
│   ├── Statistics.cs           # Statistical functions
│   └── DataStructures.cs       # Custom data structures
├── docs/
│   ├── DEVELOPMENT_GUIDE.md    # Development guide
│   ├── BUILD_DEPLOY.md         # Build and deployment
│   └── API_REFERENCE.md        # NinjaTrader API reference
└── README.md                   # This file
```

## Prerequisites

- **NinjaTrader 8**: Latest version (download from ninjatrader.com)
- **Visual Studio** or **Visual Studio Code** with C# support
- **.NET Framework 4.8** (comes with NinjaTrader)
- Basic knowledge of C# programming

## Quick Start

### 1. Setup Development Environment

```bash
# NinjaTrader installation path (default)
C:\Users\<YourUser>\Documents\NinjaTrader 8\

# Folder structure:
# - bin/Custom/Indicators/     # Compiled indicator DLLs
# - bin/Custom/Strategies/     # Compiled strategy DLLs
# - bin/Custom/AddOns/         # Compiled add-on DLLs
```

### 2. Import into NinjaTrader

**Option A: Copy Source Files**
1. Copy `.cs` files to `Documents\NinjaTrader 8\bin\Custom\Indicators\` (or Strategies/)
2. In NinjaTrader: Tools > Edit NinjaScript > Indicator
3. Select your indicator and click "Compile"

**Option B: Import .zip Archive**
1. Create a .zip with your .cs files
2. In NinjaTrader: Tools > Import > NinjaScript Add-On
3. Select the .zip file and import

### 3. Apply to Chart

1. Right-click on chart > Indicators
2. Find your custom indicator in the list
3. Configure parameters and click OK

## Development Guide

### Basic Indicator Template

```csharp
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;

namespace NinjaTrader.NinjaScript.Indicators
{
    public class MyCustomIndicator : Indicator
    {
        // ===== PRIVATE VARIABLES =====
        private double sum;
        
        // ===== PROPERTIES (User Inputs) =====
        
        [Range(1, int.MaxValue)]
        [NinjaScriptProperty]
        [Display(Name="Length", Description="Number of bars for calculation", Order=1, GroupName="Parameters")]
        public int Length
        { get; set; }
        
        [Range(1, double.MaxValue)]
        [NinjaScriptProperty]
        [Display(Name="Multiplier", Description="Multiplier for bands", Order=2, GroupName="Parameters")]
        public double Multiplier
        { get; set; }
        
        [NinjaScriptProperty]
        [Display(Name="Show Bands", Description="Display upper/lower bands", Order=3, GroupName="Display")]
        public bool ShowBands
        { get; set; }
        
        // ===== INITIALIZATION =====
        
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"My custom indicator description";
                Name = "MyCustomIndicator";
                Calculate = Calculate.OnBarClose;  // or Calculate.OnEachTick
                IsOverlay = false;  // false = separate panel
                DisplayInDataBox = true;
                DrawOnPricePanel = true;
                DrawHorizontalGridLines = true;
                DrawVerticalGridLines = true;
                PaintPriceMarkers = true;
                ScaleJustification = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                IsSuspendedWhileInactive = true;
                
                // Default parameter values
                Length = 14;
                Multiplier = 2.0;
                ShowBands = true;
                
                // Add plot lines (Series)
                AddPlot(Brushes.Green, "MainLine");
                AddPlot(Brushes.Red, "SignalLine");
                AddPlot(Brushes.Gray, "UpperBand");
                AddPlot(Brushes.Gray, "LowerBand");
            }
            else if (State == State.Configure)
            {
                // Configure any additional data series or resources
            }
            else if (State == State.DataLoaded)
            {
                // Initialize after data is loaded
                sum = 0;
            }
        }
        
        // ===== CALCULATION =====
        
        protected override void OnBarUpdate()
        {
            // Ensure we have enough bars
            if (CurrentBar < Length)
                return;
            
            // Example: Simple Moving Average
            double sma = SMA(Length)[0];
            
            // Calculate standard deviation
            double variance = 0;
            for (int i = 0; i < Length; i++)
            {
                double diff = Close[i] - sma;
                variance += diff * diff;
            }
            double stdDev = Math.Sqrt(variance / Length);
            
            // Set plot values
            Values[0][0] = sma;  // MainLine
            Values[1][0] = EMA(Values[0], Length / 2)[0];  // SignalLine
            
            if (ShowBands)
            {
                Values[2][0] = sma + (stdDev * Multiplier);  // UpperBand
                Values[3][0] = sma - (stdDev * Multiplier);  // LowerBand
            }
            
            // ===== OPTIONAL: Background coloring =====
            if (Close[0] > Values[2][0])
            {
                BackBrushes[0] = Brushes.LightGreen;
                BackBrushes[0].Opacity = 0.1;
            }
            else if (Close[0] < Values[3][0])
            {
                BackBrushes[0] = Brushes.LightPink;
                BackBrushes[0].Opacity = 0.1;
            }
            
            // ===== OPTIONAL: Alerts =====
            if (CrossAbove(Close, Values[2], 1))
            {
                Alert("CrossAbove", Priority.High, "Price crossed above upper band", 
                      "Alert.wav", 10, Brushes.Red, Brushes.White);
            }
        }
        
        // ===== PROPERTIES FOR ACCESSING VALUES FROM OTHER SCRIPTS =====
        
        [Browsable(false)]
        [XmlIgnore]
        public Series<double> MainLine
        {
            get { return Values[0]; }
        }
        
        [Browsable(false)]
        [XmlIgnore]
        public Series<double> SignalLine
        {
            get { return Values[1]; }
        }
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private MyCustomIndicator[] cacheMyCustomIndicator;
		public MyCustomIndicator MyCustomIndicator(int length, double multiplier, bool showBands)
		{
			return MyCustomIndicator(Input, length, multiplier, showBands);
		}

		public MyCustomIndicator MyCustomIndicator(ISeries<double> input, int length, double multiplier, bool showBands)
		{
			if (cacheMyCustomIndicator != null)
				for (int idx = 0; idx < cacheMyCustomIndicator.Length; idx++)
					if (cacheMyCustomIndicator[idx] != null && cacheMyCustomIndicator[idx].Length == length && cacheMyCustomIndicator[idx].Multiplier == multiplier && cacheMyCustomIndicator[idx].ShowBands == showBands && cacheMyCustomIndicator[idx].EqualsInput(input))
						return cacheMyCustomIndicator[idx];
			return CacheIndicator<MyCustomIndicator>(new MyCustomIndicator(){ Length = length, Multiplier = multiplier, ShowBands = showBands }, input, ref cacheMyCustomIndicator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.MyCustomIndicator MyCustomIndicator(int length, double multiplier, bool showBands)
		{
			return indicator.MyCustomIndicator(Input, length, multiplier, showBands);
		}

		public Indicators.MyCustomIndicator MyCustomIndicator(ISeries<double> input , int length, double multiplier, bool showBands)
		{
			return indicator.MyCustomIndicator(input, length, multiplier, showBands);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.MyCustomIndicator MyCustomIndicator(int length, double multiplier, bool showBands)
		{
			return indicator.MyCustomIndicator(Input, length, multiplier, showBands);
		}

		public Indicators.MyCustomIndicator MyCustomIndicator(ISeries<double> input , int length, double multiplier, bool showBands)
		{
			return indicator.MyCustomIndicator(input, length, multiplier, showBands);
		}
	}
}

#endregion
```

### Basic Strategy Template

```csharp
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;

namespace NinjaTrader.NinjaScript.Strategies
{
    public class MyStrategy : Strategy
    {
        private SMA fastMA;
        private SMA slowMA;
        
        [Range(1, int.MaxValue)]
        [NinjaScriptProperty]
        [Display(Name="Fast Period", Order=1, GroupName="Parameters")]
        public int FastPeriod
        { get; set; }
        
        [Range(1, int.MaxValue)]
        [NinjaScriptProperty]
        [Display(Name="Slow Period", Order=2, GroupName="Parameters")]
        public int SlowPeriod
        { get; set; }
        
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"Simple MA crossover strategy";
                Name = "MyStrategy";
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                IsFillLimitOnTouch = false;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;
                OrderFillResolution = OrderFillResolution.Standard;
                Slippage = 0;
                StartBehavior = StartBehavior.WaitUntilFlat;
                TimeInForce = TimeInForce.Gtc;
                TraceOrders = false;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;
                StopTargetHandling = StopTargetHandling.PerEntryExecution;
                BarsRequiredToTrade = 20;
                IsInstantiatedOnEachOptimizationIteration = true;
                
                FastPeriod = 10;
                SlowPeriod = 30;
            }
            else if (State == State.Configure)
            {
            }
            else if (State == State.DataLoaded)
            {
                fastMA = SMA(FastPeriod);
                slowMA = SMA(SlowPeriod);
                
                AddChartIndicator(fastMA);
                AddChartIndicator(slowMA);
            }
        }
        
        protected override void OnBarUpdate()
        {
            if (CurrentBar < BarsRequiredToTrade)
                return;
            
            // Entry logic
            if (CrossAbove(fastMA, slowMA, 1))
            {
                EnterLong(1, "Long Entry");
            }
            else if (CrossBelow(fastMA, slowMA, 1))
            {
                EnterShort(1, "Short Entry");
            }
        }
        
        protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, 
                                               int quantity, int filled, double averageFillPrice, 
                                               OrderState orderState, DateTime time, ErrorCode error, string nativeError)
        {
            // Handle order updates
        }
        
        protected override void OnExecutionUpdate(Execution execution, string executionId, 
                                                   double price, int quantity, 
                                                   MarketPosition marketPosition, string orderId, DateTime time)
        {
            // Handle execution updates
        }
    }
}
```

## Advanced Features

### 1. Multi-Timeframe Analysis

```csharp
// Add additional data series
protected override void OnStateChange()
{
    if (State == State.Configure)
    {
        AddDataSeries(BarsPeriodType.Minute, 60);  // Add 60-min bars
    }
}

protected override void OnBarUpdate()
{
    if (BarsInProgress == 0)  // Primary series
    {
        // Your logic for primary timeframe
    }
    else if (BarsInProgress == 1)  // Secondary series (60-min)
    {
        // Higher timeframe logic
        double htfClose = Closes[1][0];
    }
}
```

### 2. Custom Drawing

```csharp
protected override void OnBarUpdate()
{
    // Draw arrow
    Draw.ArrowUp(this, "Arrow" + CurrentBar, true, 0, Low[0] - TickSize * 10, Brushes.Green);
    
    // Draw text
    Draw.Text(this, "Text" + CurrentBar, "Buy Signal", 0, Low[0], Brushes.Blue);
    
    // Draw line
    Draw.Line(this, "Line" + CurrentBar, 10, Close[10], 0, Close[0], Brushes.Yellow);
}
```

### 3. Order Management

```csharp
// Enter position with stop and target
EnterLong(1, "Long Entry");
SetStopLoss("Long Entry", CalculationMode.Ticks, 20, false);
SetProfitTarget("Long Entry", CalculationMode.Ticks, 40);

// Advanced order management
private void ManagePosition()
{
    if (Position.MarketPosition == MarketPosition.Long)
    {
        // Trail stop
        double trailPrice = High[0] - (ATR(14)[0] * 2);
        SetStopLoss(CalculationMode.Price, trailPrice, false);
    }
}
```

## Best Practices

1. **State Management**: Properly initialize in `OnStateChange()`
2. **Bar Validation**: Always check `CurrentBar < BarsRequiredToTrade`
3. **Position Checks**: Verify position state before entries/exits
4. **Error Handling**: Implement `OnOrderUpdate()` for error handling
5. **Testing**: Use Strategy Analyzer for backtesting
6. **Performance**: Minimize calculations, cache results
7. **Documentation**: Comment code thoroughly

## Building and Deployment

### Compile in NinjaTrader

1. Tools > Edit NinjaScript > Indicator (or Strategy)
2. Select your script
3. Click "Compile"
4. Check for errors in output window

### Export for Distribution

1. Tools > Export > NinjaScript Add-On
2. Select your indicators/strategies
3. Create .zip archive
4. Share with others

## Debugging

```csharp
// Print to Output window
Print(String.Format("Close: {0}, SMA: {1}", Close[0], sma[0]));

// Draw debug values on chart
Draw.TextFixed(this, "Debug", 
    String.Format("Fast: {0:F2}\nSlow: {1:F2}", fastMA[0], slowMA[0]), 
    TextPosition.TopRight);

// Use breakpoints in Visual Studio (attach to NinjaTrader.exe)
```

## Resources

- [NinjaTrader 8 Help Guide](https://ninjatrader.com/support/helpGuides/nt8/)
- [NinjaScript API](https://ninjatrader.com/support/helpGuides/nt8/NT%20HelpGuide%20English.html?ninjascript.html)
- [Support Forum](https://ninjatrader.com/support/forum/)
- [Video Tutorials](https://ninjatrader.com/support/helpGuides/nt8/en-us/ninjascript_videos.htm)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

See [LICENSE](../LICENSE) file for details.




