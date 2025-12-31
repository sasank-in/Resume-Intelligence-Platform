"""
Session management and utility functions
"""
import time
from typing import Dict, Optional


class SessionManager:
    """Manage user sessions and session data"""
    
    def __init__(self, timeout: int = 60):
        """
        Initialize session manager
        
        Args:
            timeout: Session timeout in seconds
        """
        self.sessions: Dict = {}
        self.timestamps: Dict = {}
        self.timeout = timeout
    
    def create_session(self, session_id: str, data: Dict) -> None:
        """
        Create a new session
        
        Args:
            session_id: Unique session identifier
            data: Session data dictionary
        """
        self.sessions[session_id] = data
        self.timestamps[session_id] = time.time()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve session data
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data or None if not found
        """
        if session_id in self.sessions:
            self.timestamps[session_id] = time.time()  # Update timestamp
            return self.sessions[session_id]
        return None
    
    def update_session(self, session_id: str, data: Dict) -> None:
        """
        Update session data
        
        Args:
            session_id: Unique session identifier
            data: Updated data dictionary
        """
        if session_id in self.sessions:
            self.sessions[session_id].update(data)
            self.timestamps[session_id] = time.time()
    
    def cleanup_old_sessions(self) -> None:
        """Remove sessions older than timeout"""
        current_time = time.time()
        expired_sessions = [
            sid for sid, timestamp in self.timestamps.items()
            if current_time - timestamp > self.timeout
        ]
        for sid in expired_sessions:
            if sid in self.sessions:
                del self.sessions[sid]
            del self.timestamps[sid]
            print(f"[INFO] Cleaned up expired session: {sid}")
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        return session_id in self.sessions


def validate_file_upload(filename: str, allowed_types: list) -> bool:
    """
    Validate uploaded file
    
    Args:
        filename: Name of uploaded file
        allowed_types: List of allowed file extensions
        
    Returns:
        True if file is valid, False otherwise
    """
    return any(filename.endswith(ext) for ext in allowed_types)
