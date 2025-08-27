"""
MLflow logging utilities for the Financial Decision Engine.

This module provides standardized logging for optimization runs, model metrics,
and portfolio performance tracking.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient


class MLflowLogger:
    """MLflow logging utility class"""
    
    def __init__(self, experiment_name: str = "financial_optimizer"):
        """
        Initialize MLflow logger
        
        Args:
            experiment_name: Name of the MLflow experiment
        """
        self.experiment_name = experiment_name
        self.client = MlflowClient()
        
        # Set tracking URI from environment or default
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        mlflow.set_tracking_uri(tracking_uri)
        
        # Create or get experiment
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
            else:
                experiment_id = experiment.experiment_id
            
            mlflow.set_experiment(experiment_name)
            self.experiment_id = experiment_id
            
        except Exception as e:
            print(f"Warning: MLflow setup failed: {e}")
            self.experiment_id = None

    def log_optimization_run(self, metrics: Dict[str, float], 
                           portfolio: Dict[str, float],
                           optimization_type: str,
                           parameters: Optional[Dict[str, Any]] = None,
                           artifacts: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Log a portfolio optimization run
        
        Args:
            metrics: Performance metrics (return, risk, sharpe, etc.)
            portfolio: Asset weights
            optimization_type: Type of optimization (mean_variance, cvar, etc.)
            parameters: Optimization parameters
            artifacts: Additional artifacts to log
            
        Returns:
            Run ID if successful, None otherwise
        """
        if self.experiment_id is None:
            return None
            
        try:
            with mlflow.start_run(experiment_id=self.experiment_id) as run:
                # Log basic info
                mlflow.set_tag("optimization_type", optimization_type)
                mlflow.set_tag("timestamp", datetime.utcnow().isoformat())
                
                # Log metrics
                for metric_name, metric_value in metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
                
                # Log parameters
                if parameters:
                    for param_name, param_value in parameters.items():
                        mlflow.log_param(param_name, param_value)
                
                # Log portfolio composition
                portfolio_json = json.dumps(portfolio, indent=2)
                mlflow.log_text(portfolio_json, "portfolio_weights.json")
                
                # Log portfolio statistics
                num_positions = len([w for w in portfolio.values() if w > 0.001])
                max_weight = max(portfolio.values()) if portfolio else 0
                hhi = sum(w**2 for w in portfolio.values())
                
                mlflow.log_metric("num_positions", num_positions)
                mlflow.log_metric("max_weight", max_weight)
                mlflow.log_metric("concentration_hhi", hhi)
                
                # Log artifacts
                if artifacts:
                    for artifact_name, artifact_path in artifacts.items():
                        if os.path.exists(artifact_path):
                            mlflow.log_artifact(artifact_path, artifact_name)
                
                return run.info.run_id
                
        except Exception as e:
            print(f"Warning: MLflow logging failed: {e}")
            return None

    def log_backtest_results(self, backtest_metrics: Dict[str, float],
                           strategy_name: str,
                           period: str) -> Optional[str]:
        """
        Log backtest results
        
        Args:
            backtest_metrics: Backtest performance metrics
            strategy_name: Name of the strategy
            period: Backtest period
            
        Returns:
            Run ID if successful, None otherwise
        """
        if self.experiment_id is None:
            return None
            
        try:
            with mlflow.start_run(experiment_id=self.experiment_id) as run:
                mlflow.set_tag("run_type", "backtest")
                mlflow.set_tag("strategy_name", strategy_name)
                mlflow.set_tag("period", period)
                mlflow.set_tag("timestamp", datetime.utcnow().isoformat())
                
                for metric_name, metric_value in backtest_metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
                
                return run.info.run_id
                
        except Exception as e:
            print(f"Warning: MLflow backtest logging failed: {e}")
            return None

    def log_risk_model_metrics(self, model_metrics: Dict[str, float],
                             model_type: str) -> Optional[str]:
        """
        Log risk model validation metrics
        
        Args:
            model_metrics: Risk model performance metrics
            model_type: Type of risk model
            
        Returns:
            Run ID if successful, None otherwise
        """
        if self.experiment_id is None:
            return None
            
        try:
            with mlflow.start_run(experiment_id=self.experiment_id) as run:
                mlflow.set_tag("run_type", "risk_model")
                mlflow.set_tag("model_type", model_type)
                mlflow.set_tag("timestamp", datetime.utcnow().isoformat())
                
                for metric_name, metric_value in model_metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
                
                return run.info.run_id
                
        except Exception as e:
            print(f"Warning: MLflow risk model logging failed: {e}")
            return None


# Global logger instance
_logger_instance = None

def get_logger(experiment_name: str = "financial_optimizer") -> MLflowLogger:
    """Get or create MLflow logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = MLflowLogger(experiment_name)
    return _logger_instance


def log_optimization_run(metrics: Dict[str, float], 
                        portfolio: Dict[str, float],
                        optimization_type: str,
                        parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Convenience function to log optimization run
    
    Args:
        metrics: Performance metrics
        portfolio: Asset weights
        optimization_type: Type of optimization
        parameters: Optimization parameters
        
    Returns:
        Run ID if successful, None otherwise
    """
    logger = get_logger()
    return logger.log_optimization_run(metrics, portfolio, optimization_type, parameters)


def log_backtest_results(backtest_metrics: Dict[str, float],
                        strategy_name: str,
                        period: str) -> Optional[str]:
    """
    Convenience function to log backtest results
    
    Args:
        backtest_metrics: Backtest performance metrics
        strategy_name: Name of the strategy
        period: Backtest period
        
    Returns:
        Run ID if successful, None otherwise
    """
    logger = get_logger()
    return logger.log_backtest_results(backtest_metrics, strategy_name, period)


# Example usage
if __name__ == "__main__":
    # Test logging functionality
    logger = get_logger("test_experiment")
    
    test_metrics = {
        "portfolio_return": 0.12,
        "portfolio_risk": 0.15,
        "sharpe_ratio": 0.8,
        "max_drawdown": -0.05
    }
    
    test_portfolio = {
        "AAPL": 0.15,
        "GOOGL": 0.12,
        "MSFT": 0.18,
        "CASH": 0.55
    }
    
    run_id = logger.log_optimization_run(
        metrics=test_metrics,
        portfolio=test_portfolio,
        optimization_type="mean_variance",
        parameters={"risk_aversion": 3.0, "lookback": 252}
    )
    
    print(f"Logged test run with ID: {run_id}")