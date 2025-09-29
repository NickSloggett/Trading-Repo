# Sierra Chart C++ Indicators and Studies

This directory contains C++ code for custom studies, indicators, and trading systems in Sierra Chart.

## Overview

Sierra Chart uses the ACSIL (Advanced Custom Study Interface and Language) framework for developing custom studies in C++. This provides high-performance, compiled indicators with full access to Sierra Chart's powerful features.

## Structure

```
sierra-chart-indicators/
├── studies/                    # Custom indicators and studies
│   ├── advanced_volume.cpp     # Advanced volume analysis
│   ├── order_flow.cpp          # Order flow indicators
│   ├── market_profile.cpp      # Market profile studies
│   └── custom_ma.cpp           # Custom moving averages
├── trading_systems/            # Automated trading systems
│   ├── mean_reversion.cpp      # Mean reversion strategy
│   └── breakout_system.cpp     # Breakout trading system
├── templates/                  # Study templates
│   ├── basic_indicator.cpp     # Basic indicator template
│   ├── trading_system.cpp      # Trading system template
│   └── drawing_study.cpp       # Drawing study template
├── utils/                      # Utility functions
│   ├── statistics.h            # Statistical functions
│   └── helpers.h               # Helper functions
├── docs/
│   ├── ACSIL_GUIDE.md          # ACSIL programming guide
│   ├── BUILD_INSTRUCTIONS.md   # Compilation instructions
│   └── EXAMPLES.md             # Example studies
├── Makefile                    # Build automation
└── README.md                   # This file
```

## Prerequisites

- **Sierra Chart**: Version 2400 or later (download from sierrachart.com)
- **Visual Studio** (Windows): 2019 or later, or
- **GCC/Clang** (Linux/Mac): C++17 compatible compiler
- **ACSIL SDK**: Included with Sierra Chart installation

## Quick Start

### 1. Setup Development Environment

**Windows:**
```cmd
# Install Visual Studio with C++ development tools
# Add Sierra Chart include path to project
set SIERRA_PATH=C:\SierraChart
```

**Linux:**
```bash
# Install GCC
sudo apt-get install build-essential

# Set Sierra Chart path
export SIERRA_PATH=/opt/SierraChart
```

### 2. Compile a Study

**Using Makefile:**
```bash
# Compile single study
make study NAME=advanced_volume

# Compile all studies
make all

# Clean build artifacts
make clean
```

**Manual Compilation (Windows):**
```cmd
cl.exe /LD /MD /O2 /EHsc advanced_volume.cpp ^
  /I"C:\SierraChart" ^
  /link /OUT:advanced_volume.dll
```

**Manual Compilation (Linux):**
```bash
g++ -shared -fPIC -O3 -std=c++17 advanced_volume.cpp \
  -I/opt/SierraChart \
  -o advanced_volume.so
```

### 3. Install in Sierra Chart

1. Copy compiled DLL/SO to Sierra Chart's `Data` folder
2. In Sierra Chart: Analysis > Studies > Add Custom Study
3. Select your study from the list
4. Configure parameters and apply to chart

## Development Guide

### Basic Indicator Template

```cpp
#include "sierrachart.h"

// Study identifier - must be unique
SCDLLName("My Custom Indicator")

/*==========================================================================*/
SCSFExport scsf_MyCustomIndicator(SCStudyInterfaceRef sc)
{
    // Subgraph declarations
    SCSubgraphRef Subgraph_Line = sc.Subgraph[0];
    
    // Input declarations
    SCInputRef Input_Length = sc.Input[0];
    
    // Configuration section
    if (sc.SetDefaults)
    {
        // Study settings
        sc.GraphName = "My Custom Indicator";
        sc.StudyDescription = "Description of what this indicator does";
        sc.AutoLoop = 1;  // Enable auto-looping
        sc.GraphRegion = 0;  // 0 = main chart, 1 = separate panel
        
        // Subgraph configuration
        Subgraph_Line.Name = "Line";
        Subgraph_Line.DrawStyle = DRAWSTYLE_LINE;
        Subgraph_Line.PrimaryColor = RGB(0, 255, 0);
        Subgraph_Line.LineWidth = 2;
        
        // Input configuration
        Input_Length.Name = "Length";
        Input_Length.SetInt(14);
        Input_Length.SetIntLimits(1, 1000);
        
        return;
    }
    
    // Calculation section
    // sc.Index is current bar being processed (auto-loop handles iteration)
    
    int Length = Input_Length.GetInt();
    
    // Example: Simple moving average
    sc.SimpleMovAvg(sc.Close, Subgraph_Line, Length);
    
    // Or manual calculation:
    // float Sum = 0;
    // for (int i = sc.Index - Length + 1; i <= sc.Index; i++)
    // {
    //     if (i >= 0)
    //         Sum += sc.Close[i];
    // }
    // Subgraph_Line[sc.Index] = Sum / Length;
}
```

### Advanced Features

#### 1. Multiple Timeframe Analysis

```cpp
// Get data from higher timeframe
int HigherTimeframeChart = sc.Input[1].GetChartNumber();
SCGraphData HTFData;
sc.GetChartBaseData(HigherTimeframeChart, HTFData);

// Get corresponding higher timeframe index
int HTFIndex = sc.GetNearestMatchForDateTimeIndex(HigherTimeframeChart, sc.Index);

// Use HTF data
float HTFClose = HTFData[SC_CLOSE][HTFIndex];
```

#### 2. Alert Conditions

```cpp
// Generate alert when condition is met
if (sc.Close[sc.Index] > Subgraph_Line[sc.Index] &&
    sc.Close[sc.Index - 1] <= Subgraph_Line[sc.Index - 1])
{
    sc.SetAlert(1, "Price crossed above indicator");
}
```

#### 3. Drawing Objects

```cpp
// Draw horizontal line
s_UseTool Tool;
Tool.Clear();
Tool.ChartNumber = sc.ChartNumber;
Tool.DrawingType = DRAWING_HORIZONTAL_LINE;
Tool.BeginValue = sc.Close[sc.Index];
Tool.Color = RGB(255, 0, 0);
Tool.LineWidth = 2;
sc.UseTool(Tool);
```

#### 4. Order Management (Trading Systems)

```cpp
// Submit buy order
s_SCNewOrder NewOrder;
NewOrder.OrderQuantity = 1;
NewOrder.OrderType = SCT_ORDERTYPE_MARKET;

int Result = sc.BuyEntry(NewOrder);
if (Result > 0)
{
    // Order submitted successfully
}
```

### Performance Optimization

1. **Use AutoLoop**: Enables efficient bar-by-bar processing
2. **Persistent Variables**: Use `sc.GetPersistent*()` for state
3. **Avoid Recalculation**: Check `sc.Index` and only calculate when needed
4. **Use Built-in Functions**: Sierra Chart's built-in functions are optimized
5. **Memory Management**: Use SCFloatArray for large arrays

## Examples

### 1. Advanced Volume Analysis

See `studies/advanced_volume.cpp` - Analyzes volume at price levels with:
- Volume-weighted average price (VWAP)
- Volume profile
- Delta volume (buy vs. sell pressure)

### 2. Order Flow Indicator

See `studies/order_flow.cpp` - Tracks order flow metrics:
- Bid/ask imbalance
- Large order detection
- Cumulative delta

### 3. Market Profile

See `studies/market_profile.cpp` - Generates market profile:
- TPO (Time Price Opportunity) charts
- Value area calculation
- Point of control (POC)

## API Reference

### Common Functions

```cpp
// Price arrays
sc.Open[index]
sc.High[index]
sc.Low[index]
sc.Close[index]
sc.Volume[index]

// Technical indicators (built-in)
sc.SimpleMovAvg(Input, Output, Length)
sc.ExponentialMovAvg(Input, Output, Length)
sc.RSI(Input, Output, RSIOutput, Length, MovAvgType)
sc.MACD(Input, FastMA, SlowMA, MACD, Signal, MovAvgType, FastLen, SlowLen, SignalLen)

// Array operations
sc.ArrayValueAtNthOccurrence(Array, SubgraphOut, StartIndex, OccurrenceIndex, ValueToFind)
sc.Highest(Input, Output, Length)
sc.Lowest(Input, Output, Length)

// Time functions
sc.GetBarHasClosedStatus()
sc.GetTradeDate()
sc.GetCurrentDateTime()

// Order functions (trading systems)
sc.BuyEntry(NewOrder)
sc.SellEntry(NewOrder)
sc.BuyExit(NewOrder)
sc.SellExit(NewOrder)
```

## Best Practices

1. **Testing**: Always test thoroughly on historical and simulated data
2. **Error Handling**: Check return values and handle errors gracefully
3. **Comments**: Document complex logic and formulas
4. **Version Control**: Use git for tracking changes
5. **Performance**: Profile code and optimize hot paths
6. **Modularity**: Break complex studies into reusable functions
7. **Configuration**: Make parameters configurable via inputs

## Debugging

1. **Add logging**: Use `sc.AddMessageToLog()`
2. **Visual debugging**: Draw values on chart using text drawings
3. **Incremental development**: Build and test in small increments
4. **Use replay**: Test with Sierra Chart's bar replay feature

## Resources

- [Official ACSIL Documentation](https://www.sierrachart.com/index.php?page=doc/ACSIL.php)
- [ACSIL Function Reference](https://www.sierrachart.com/index.php?page=doc/ACSILFunctionDoc.php)
- [Sierra Chart Support Forum](https://www.sierrachart.com/supportboard.php)
- [ACSIL Programming Videos](https://www.sierrachart.com/index.php?page=doc/ACSILProgrammingVideos.php)

## Contributing

Contributions are welcome! Please:
1. Follow Sierra Chart's ACSIL coding standards
2. Test thoroughly before submitting
3. Document new features and parameters
4. Add example usage in comments

## License

See [LICENSE](../LICENSE) file for details.
