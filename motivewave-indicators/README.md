# MotiveWave Indicators and Strategies

This directory contains Java code for custom studies (indicators) and strategies in MotiveWave trading platform.

## Structure

- **studies/**: Custom indicators extending `Study` class
- **strategies/**: Automated trading strategies extending `Strategy` class

## Prerequisites

- MotiveWave software (download from motivewave.com)
- Java Development Kit (JDK 8 or later)
- MotiveWave SDK (included with MotiveWave or downloadable)

## Setup

1. **Install MotiveWave**: Download and install MotiveWave.
2. **Set up Development Environment**:
   - Use IDE like IntelliJ IDEA or Eclipse.
   - Add MotiveWave SDK to project classpath (jar files from MotiveWave installation).
3. **Compile**:
   - Compile `.java` files to `.class`.
   - Place compiled classes in MotiveWave's `studies/` or `scripts/` folder (configurable in Settings > Studies > Custom Studies).
4. **Load in MotiveWave**:
   - Restart MotiveWave.
   - In a chart, go to Studies > Add Study > Custom > Select your study.

## Development

### Creating a Custom Study

Extend the `com.motivewave.platform.sdk.study.Study` class.

Template (`studies/TemplateStudy.java`):

```java
package com.motivewave.platform.sdk.study;

import com.motivewave.platform.sdk.common.*;
import com.motivewave.platform.sdk.common.desc.*;
import com.motivewave.platform.sdk.study.*;

@StudyHeader(
    namespace = "com.mycompany",
    id = "TEMPLATESTUDY",
    version = 1,
    label = "Template Study",
    desc = "A template for custom MotiveWave studies"
)
public class TemplateStudy extends Study {
    
    @Override
    public void initialize(Defaults defaults) {
        var settings = getSettings();
        settings.addIntegerSetting("length", 14, 1, 999, 1);
        
        var sd = createStudyDescriptor();
        sd.setMinBars(20); // Minimum bars needed
        sd.setLabelSettings("length");
    }
    
    @Override
    protected void calculate(int index, DataContext ctx) {
        int length = getSettings().getInteger("length");
        if (index < length) return;
        
        double[] close = ctx.getData(0).getCloseValues();
        double sum = 0;
        for (int i = 0; i < length; i++) {
            sum += close[index - i];
        }
        double ma = sum / length;
        
        setValue(index, ma, 0); // Output value
    }
}
```

### Compiling and Installing

- Compile: `javac -cp "MotiveWaveSDK.jar" TemplateStudy.java`
- Copy `TemplateStudy.class` to MotiveWave's custom studies folder.
- For strategies, similar but extend `Strategy` and implement order management.

### Best Practices

- Use `@StudyHeader` annotation for metadata.
- Handle settings with `getSettings()`.
- Use `DataContext` for data access (OHLCV).
- Test in MotiveWave's Study Tester.
- Avoid heavy computations; use efficient loops.

## Examples

- **TemplateStudy**: Simple moving average example.
- Add more: RSI, MACD customizations in `studies/`.

## Resources

- [MotiveWave SDK Documentation](https://www.motivewave.com/support/SDK.htm)
- [Study Development Guide](https://www.motivewave.com/support/study_development.htm)
- JavaDocs in SDK.

Contribute by adding `.java` files and updating examples in README.
