# tests/test_collector_job.py
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app import collector_job


class CollectorJobTests(unittest.TestCase):
    @patch("app.collector_job.get_db_connection")
    def test_insert_usage_runs_insert_and_commit(self, mock_get_db_conn):
        # Arrange: fake connection + fake cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_conn.return_value = mock_conn

        ts = datetime(2025, 1, 1, 12, 0, 0)

        # Act
        collector_job.insert_usage(10.0, 20.0, 30.0, ts)

        # Assert: cursor was created
        mock_conn.cursor.assert_called_once()

        # Assert: one INSERT executed with params
        mock_cursor.execute.assert_called_once()

        # Assert: commit + close on connection
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

