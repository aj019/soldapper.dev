import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
from typing import Dict, Any
import os

class Monitoring:
    def __init__(self):
        self.setup_logging()
        self.analytics_file = "analytics.json"
        self._ensure_analytics_file()

    def setup_logging(self):
        """Setup logging configuration."""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Setup file handler
        file_handler = RotatingFileHandler(
            f"{log_dir}/app.log",
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )

        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        self.logger = logging.getLogger(__name__)

    def _ensure_analytics_file(self):
        """Ensure analytics file exists with proper structure."""
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'w') as f:
                json.dump({
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "daily_stats": {},
                    "endpoint_stats": {}
                }, f)

    def log_request(self, endpoint: str, status: str, duration: float):
        """Log API request details."""
        self.logger.info(f"Request to {endpoint} - Status: {status} - Duration: {duration}s")
        self._update_analytics(endpoint, status)

    def log_error(self, error: Exception, context: str = ""):
        """Log error details."""
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)

    def _update_analytics(self, endpoint: str, status: str):
        """Update analytics data."""
        try:
            with open(self.analytics_file, 'r') as f:
                analytics = json.load(f)

            # Update general stats
            analytics["total_requests"] += 1
            if status == "success":
                analytics["successful_requests"] += 1
            else:
                analytics["failed_requests"] += 1

            # Update daily stats
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in analytics["daily_stats"]:
                analytics["daily_stats"][today] = {
                    "total": 0,
                    "success": 0,
                    "fail": 0
                }
            analytics["daily_stats"][today]["total"] += 1
            if status == "success":
                analytics["daily_stats"][today]["success"] += 1
            else:
                analytics["daily_stats"][today]["fail"] += 1

            # Update endpoint stats
            if endpoint not in analytics["endpoint_stats"]:
                analytics["endpoint_stats"][endpoint] = {
                    "total": 0,
                    "success": 0,
                    "fail": 0
                }
            analytics["endpoint_stats"][endpoint]["total"] += 1
            if status == "success":
                analytics["endpoint_stats"][endpoint]["success"] += 1
            else:
                analytics["endpoint_stats"][endpoint]["fail"] += 1

            with open(self.analytics_file, 'w') as f:
                json.dump(analytics, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error updating analytics: {str(e)}")

    def get_analytics(self) -> Dict[str, Any]:
        """Get current analytics data."""
        try:
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading analytics: {str(e)}")
            return {}

# Initialize monitoring instance
monitoring = Monitoring() 