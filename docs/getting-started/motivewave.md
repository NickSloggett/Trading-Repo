# Getting Started with MotiveWave Indicators

## Overview

MotiveWave allows custom studies and strategies in Java.

## Setup

1. Download [MotiveWave](https://www.motivewave.com) and install.
2. Get SDK from installation or website.
3. Set up Java IDE (IntelliJ/Eclipse) with SDK jars in classpath.

## Using Repo Files

- Go to `motivewave-indicators/studies/`.
- Compile `TemplateStudy.java` (e.g., `javac -cp sdk.jar TemplateStudy.java`).
- Copy `.class` to MotiveWave's custom studies folder (Settings > Studies > Custom Studies Path).
- Restart MotiveWave.
- In chart: Studies > Add Study > Custom > Template Study.

## Creating Your Own

Extend `Study` class, use `@StudyHeader`.

See template for SMA example.

## Testing

- Add to chart.
- Use Study Tester for performance.
- Debug with IDE.

## Next Steps

- Add settings and multiple outputs.
- Learn more: [MotiveWave SDK Docs](https://www.motivewave.com/support/SDK.htm)
