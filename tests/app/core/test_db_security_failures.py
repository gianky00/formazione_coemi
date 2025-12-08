import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
import time
from pathlib import Path
from cryptography.fernet import InvalidToken
import sqlite3
import pytest

# Import the module explicitly for robust patching
import app.core.db_security as db_security_module
from app.core.db_security import DBSecurityManager

class TestDBSecurityFailures(unittest.TestCase):
    
    def setUp(self):
        # Patch configuration using patch.object for reliability
        self.settings_patcher = patch.object(db_security_module, 'settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.DATABASE_PATH = None
        
        self.user_data_patcher = patch.object(db_security_module, 'get_user_data_dir')
        self.mock_get_user_data = self.user_data_patcher.start()
        self.mock_get_user_data.return_value = Path('/tmp/mock_data')
        
        # Patch LockManager
        self.lock_mgr_patcher = patch.object(db_security_module, 'LockManager')
        self.mock_lock_mgr_cls = self.lock_mgr_patcher.start()
        self.mock_lock_mgr = self.mock_lock_mgr_cls.return_value
        
        # Patch Path.exists on the class globally as it's used by Path instances
        self.path_exists_patcher = patch('pathlib.Path.exists')
        self.mock_exists = self.path_exists_patcher.start()
        self.mock_exists.return_value = False # Default to no DB existing
        
    def tearDown(self):
        self.settings_patcher.stop()
        self.user_data_patcher.stop()
        self.lock_mgr_patcher.stop()
        self.path_exists_patcher.stop()

    def test_stale_lock_recovery_corrupt_json(self):
        """Test that a corrupt lock file is removed."""
        # Force existence check to return True
        self.mock_exists.return_value = True
        
        # Mock opening the lock file with corrupt JSON
        with patch('builtins.open', mock_open(read_data=b'L{invalid_json')):
            # Patch os.remove on the module to ensure we catch the call
            with patch.object(db_security_module.os, 'remove') as m_remove:
                # Initialize manager (triggering the check)
                mgr = DBSecurityManager()
                
                # Verify removal was attempted
                m_remove.assert_called()

    def test_stale_lock_recovery_dead_pid(self):
        """Test that lock is removed if PID is dead."""
        self.mock_exists.return_value = True
        lock_data = json.dumps({"pid": 99999}).encode('utf-8')
        mock_file_content = b'L' + lock_data
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch.object(db_security_module.psutil, 'pid_exists', return_value=False):
                with patch.object(db_security_module.os, 'remove') as m_remove:
                    mgr = DBSecurityManager()
                    m_remove.assert_called()

    def test_stale_lock_recovery_unrelated_process(self):
        """Test that lock is removed if PID exists but is not our app."""
        self.mock_exists.return_value = True
        lock_data = json.dumps({"pid": 1234}).encode('utf-8')
        mock_file_content = b'L' + lock_data
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch.object(db_security_module.psutil, 'pid_exists', return_value=True):
                with patch.object(db_security_module.psutil, 'Process') as m_proc:
                    m_proc.return_value.name.return_value = "chrome.exe"
                    with patch.object(db_security_module.os, 'remove') as m_remove:
                        mgr = DBSecurityManager()
                        m_remove.assert_called()

    def test_stale_lock_recovery_valid_process(self):
        """Test that lock is preserved if process is valid."""
        lock_data = json.dumps({"pid": 1234}).encode('utf-8')
        mock_file_content = b'L' + lock_data
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch.object(db_security_module.psutil, 'pid_exists', return_value=True):
                with patch.object(db_security_module.psutil, 'Process') as m_proc:
                    m_proc.return_value.name.return_value = "python.exe"
                    with patch.object(db_security_module.os, 'remove') as m_remove:
                        mgr = DBSecurityManager()
                        m_remove.assert_not_called()

    def test_heartbeat_failure_triggers_readonly(self):
        """Test that 3 heartbeat failures force read-only mode."""
        mgr = DBSecurityManager()
        # Explicitly ensure lock_manager is a mock to prevent AttributeError
        mgr.lock_manager = MagicMock()
        mgr.is_read_only = False
        mgr.lock_manager.update_heartbeat.return_value = False
        
        with patch('threading.Timer') as m_timer:
            mgr._start_heartbeat()
            # The first call is immediate. Fail 1
            self.assertEqual(mgr._heartbeat_failures, 1)
            
            # Simulate timer callback
            args = m_timer.call_args[0]
            callback = args[1]
            
            callback() # Fail 2
            self.assertEqual(mgr._heartbeat_failures, 2)
            
            callback() # Fail 3 -> Should trigger ReadOnly
            self.assertEqual(mgr._heartbeat_failures, 3)
            self.assertTrue(mgr.is_read_only)
            self.assertIsNone(mgr._heartbeat_timer)

    def test_load_memory_db_permission_error(self):
        """Test handling of permission error when reading DB."""
        mgr = DBSecurityManager()
        mgr.db_path = MagicMock(exists=lambda: True)
        
        with patch('builtins.open', side_effect=PermissionError("Access Denied")):
            with self.assertRaises(RuntimeError):
                mgr.load_memory_db()

    def test_load_memory_db_decryption_failure(self):
        """Test handling of invalid decryption."""
        mgr = DBSecurityManager()
        mgr.db_path = MagicMock(exists=lambda: True)
        
        # Mock file with header
        encrypted_content = mgr._HEADER + b'some_junk_bytes'
        
        with patch('builtins.open', mock_open(read_data=encrypted_content)):
            # Mock fernet to raise error
            mgr.fernet.decrypt = MagicMock(side_effect=InvalidToken)
            with self.assertRaises(ValueError):
                mgr.load_memory_db()

    def test_save_to_disk_read_only(self):
        """Test that save is blocked in read-only mode."""
        mgr = DBSecurityManager()
        mgr.is_read_only = True
        mgr.active_connection = MagicMock()
        
        result = mgr.save_to_disk()
        self.assertFalse(result)
        mgr.active_connection.serialize.assert_not_called()

    def test_save_to_disk_retry_on_permission_error(self):
        """Test that _safe_write retries on PermissionError."""
        mgr = DBSecurityManager()
        mgr.is_read_only = False
        mgr.active_connection = MagicMock()
        mgr.active_connection.serialize.return_value = b'db_data'
        mgr.db_path = Path('/tmp/mock_data/db.db')
        
        with patch('builtins.open', mock_open()) as m_open:
            with patch.object(db_security_module.os, 'replace') as m_replace:
                # First 2 calls fail, 3rd succeeds
                m_replace.side_effect = [PermissionError, PermissionError, None]
                
                mgr.save_to_disk()
                
                # Should have been called 3 times due to retry
                self.assertEqual(m_replace.call_count, 3)

    def test_verify_integrity_corrupt_sqlite(self):
        """Test integrity check fails on corrupt internal data."""
        mgr = DBSecurityManager()
        
        with patch('builtins.open', mock_open(read_data=b'NOT_A_DB_HEADER')):
            with patch('sqlite3.connect') as m_connect:
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                m_connect.return_value = mock_conn
                
                # integrity_check returns "malformed" or similar
                mock_cursor.fetchone.return_value = ("malformed",)
                
                result = mgr.verify_integrity(Path("dummy"))
                self.assertFalse(result)

    def test_backup_rotation_failure(self):
        """Test graceful handling of backup rotation errors."""
        mgr = DBSecurityManager()
        backup_dir = Path('/tmp/backups')
        
        # Mock glob returning files
        file1 = MagicMock()
        file1.stat.return_value.st_mtime = 100
        file2 = MagicMock()
        file2.stat.return_value.st_mtime = 200 # Newer
        
        with patch.object(Path, 'glob', return_value=[file2, file1]):
             # unlink raises Exception
             file1.unlink.side_effect = PermissionError("Cannot delete")
             
             # Should not crash
             mgr.rotate_backups(backup_dir, keep=1)
             
             file1.unlink.assert_called_once()

    def test_move_database_success(self):
        """Test successful DB move."""
        mgr = DBSecurityManager()
        mgr.is_read_only = False
        old_path = Path('/old/path/db.db')
        mgr.db_path = old_path
        mgr.save_to_disk = MagicMock(return_value=True)
        
        target = Path('/new/path')
        
        with patch('shutil.move') as m_move:
            with patch('pathlib.Path.mkdir'):
                # Call the method
                mgr.move_database(target)
                
                # Verify shutil.move
                m_move.assert_called_with(str(old_path), str(target / 'db.db'))
                # Verify settings were saved via the module reference we patched
                self.mock_settings.save_mutable_settings.assert_called()

    def test_move_database_failure_readonly(self):
        """Test move blocked in read-only."""
        mgr = DBSecurityManager()
        mgr.is_read_only = True
        with self.assertRaises(PermissionError):
            mgr.move_database(Path('/new'))
