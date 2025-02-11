"""Progress tracking for the research process."""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Tracks progress of the research process using files."""
    
    def __init__(self, session_id: str, base_dir: str = "temp"):
        """Initialize the progress tracker.
        
        Args:
            session_id: Session ID for tracking
            base_dir: Base directory for progress files
        """
        logger.info(f"Initialized ProgressTracker for session {session_id}")
        self.session_id = session_id
        self.base_dir = Path(base_dir) / "progress"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.base_dir / f"{session_id}_progress.json"
        
        # Initialize default progress state
        self._current_progress = {
            "session_id": session_id,
            "current_step": 0,
            "total_steps": 0,
            "status": "Initializing",
            "agent": "System",
            "description": "Setting up progress tracking",
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "errors": []
        }
        
        # Try to load existing progress or create new file
        if self.progress_file.exists():
            self._load_progress()
        else:
            # Create initial progress file
            self.save_progress()
            logger.info(f"Created new progress file at {self.progress_file}")
    
    def _load_progress(self) -> None:
        """Load progress from file."""
        try:
            with open(self.progress_file, 'r') as f:
                loaded_progress = json.load(f)
                # Update current progress while preserving structure
                self._current_progress.update(loaded_progress)
            logger.info(f"Loaded progress from {self.progress_file}")
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            # Keep default progress state on error
    
    def update_progress(self, agent: str, current_step: int, total_steps: int, status: str) -> None:
        """Update progress.
        
        Args:
            agent: Name of the agent making progress
            current_step: Current step number
            total_steps: Total number of steps
            status: Current status message
        """
        # Reload progress to get any updates from other trackers
        self._load_progress()
        
        # Update current progress
        self._current_progress.update({
            "current_step": current_step,
            "total_steps": total_steps,
            "status": status,
            "agent": agent
        })
        
        # Add to step history
        step = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "step": current_step,
            "total": total_steps,
            "status": status
        }
        
        # Ensure steps list exists
        if "steps" not in self._current_progress:
            self._current_progress["steps"] = []
            
        # Append step to history
        self._current_progress["steps"].append(step)
        
        # Save progress
        self.save_progress()
        logger.info(f"Updated progress: {agent} - Step {current_step}/{total_steps} - {status}")
    
    def save_progress(self) -> None:
        """Save progress to file."""
        try:
            # Ensure directory exists
            self.base_dir.mkdir(parents=True, exist_ok=True)
            
            # Write progress atomically using a temporary file
            temp_file = self.progress_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(self._current_progress, f)
            temp_file.replace(self.progress_file)
            
            logger.info(f"Saved progress to {self.progress_file}")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
            raise
    
    def get_current_progress(self) -> Optional[Dict]:
        """Get current progress."""
        return self._current_progress
    
    def recover_progress(self) -> Optional[Dict]:
        """Recover progress from file."""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                logger.info(f"Recovered progress for session {self.session_id}")
                self._current_progress = progress
                return progress
        except Exception as e:
            logger.error(f"Error recovering progress: {e}")
        return None
    
    def cleanup(self) -> None:
        """Clean up progress files."""
        try:
            if self.progress_file.exists():
                self.progress_file.unlink()
                logger.info(f"Cleaned up progress file {self.progress_file}")
        except Exception as e:
            logger.error(f"Error cleaning up progress: {e}")
    
    def log_error(self, error: str) -> None:
        """Log an error in the progress file.
        
        Args:
            error: Error message to log
        """
        try:
            progress = self._current_progress
            
            # Add error information
            progress["errors"] = progress.get("errors", []) + [
                {
                    "timestamp": datetime.now().isoformat(),
                    "error": error
                }
            ]
            
            self.save_progress()
            logger.error(f"Logged error in progress: {error}")
        except Exception as e:
            logger.error(f"Error logging error in progress: {str(e)}")
    
    def get_step_history(self) -> list:
        """Get the history of steps.
        
        Returns:
            List of step information dictionaries
        """
        try:
            progress = self._current_progress
            return progress.get("steps", [])
        except Exception as e:
            logger.error(f"Error getting step history: {str(e)}")
            return []
    
    def get_errors(self) -> list:
        """Get the list of errors.
        
        Returns:
            List of error dictionaries
        """
        try:
            progress = self._current_progress
            return progress.get("errors", [])
        except Exception as e:
            logger.error(f"Error getting errors: {str(e)}")
            return []