"""
Command Line Interface for Trading Development Platform
"""

import click
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def cli(verbose: bool, config: Optional[str]):
    """Trading Development Platform CLI"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if config:
        logger.info(f"Using configuration file: {config}")


@cli.command()
@click.argument('symbol')
@click.option('--start-date', '-s', default='2020-01-01', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e', help='End date (YYYY-MM-DD)')
@click.option('--interval', '-i', default='1d', help='Data interval')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def download(symbol: str, start_date: str, end_date: str, interval: str, output: Optional[str]):
    """Download historical data for a symbol"""
    try:
        from python_algorithms.utils.fetch_data import fetch_and_save

        data = fetch_and_save(symbol, start_date, end_date, interval=interval)

        if data is not None:
            if output:
                output_path = Path(output)
                data.to_csv(output_path)
                click.echo(f"Data saved to {output_path}")
            else:
                click.echo(f"Downloaded {len(data)} records for {symbol}")
        else:
            click.echo(f"Failed to download data for {symbol}", err=True)
            raise click.Abort()

    except ImportError:
        click.echo("Data fetching utilities not available. Install dependencies first.", err=True)
        raise click.Abort()


@cli.command()
@click.argument('symbol')
@click.option('--start-date', '-s', default='2020-01-01', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e', help='End date (YYYY-MM-DD)')
def analyze(symbol: str, start_date: str, end_date: str):
    """Run basic analysis on a symbol"""
    try:
        from trading_tools.analysis.simple_analysis import analyze_symbol

        result = analyze_symbol(symbol, start_date, end_date)

        if 'error' in result:
            click.echo(f"Analysis failed: {result['error']}", err=True)
            raise click.Abort()

        metrics = result['metrics']
        click.echo(f"\nAnalysis for {symbol}:")
        click.echo("=" * 50)
        for key, value in metrics.items():
            if isinstance(value, float):
                click.echo("20")
            else:
                click.echo(f"{key}: {value}")

    except ImportError:
        click.echo("Analysis tools not available. Install dependencies first.", err=True)
        raise click.Abort()


@cli.command()
@click.argument('backtest_file', type=click.Path(exists=True))
@click.option('--symbol', '-s', default='AAPL', help='Symbol to backtest')
@click.option('--start-date', default='2020-01-01', help='Start date')
@click.option('--end-date', help='End date')
def backtest(backtest_file: str, symbol: str, start_date: str, end_date: str):
    """Run a backtest from a Python file"""
    try:
        # Import the backtest module
        import importlib.util
        spec = importlib.util.spec_from_file_location("backtest_module", backtest_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for run_backtest function
        if hasattr(module, 'run_backtest_sync'):
            result = module.run_backtest_sync(symbol, start_date, end_date)
            click.echo("Backtest Results:")
            click.echo("=" * 50)
            click.echo(str(result))
        else:
            click.echo("No run_backtest_sync function found in the file", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"Backtest failed: {e}", err=True)
        raise click.Abort()


@cli.command()
def status():
    """Show system status and health checks"""
    click.echo("Trading Development Platform Status")
    click.echo("=" * 50)

    # Check Python version
    import sys
    click.echo(f"Python Version: {sys.version}")

    # Check key dependencies
    dependencies = ['pandas', 'numpy', 'yfinance', 'plotly']
    for dep in dependencies:
        try:
            __import__(dep)
            click.echo(f"✓ {dep}")
        except ImportError:
            click.echo(f"✗ {dep} - Not installed")

    # Check database connection (if configured)
    try:
        import os
        if 'DATABASE_URL' in os.environ:
            click.echo("✓ Database URL configured")
        else:
            click.echo("! Database URL not configured")
    except:
        pass

    click.echo("\nPlatform ready for development!")


if __name__ == '__main__':
    cli()
