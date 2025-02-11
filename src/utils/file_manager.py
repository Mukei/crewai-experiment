"""File management utilities."""
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class FileManager:
    """Manages file operations for research tasks."""

    def __init__(self, session_id: Optional[str] = None, base_dir: str = "temp"):
        """Initialize file manager."""
        logger.info(f"Initialized FileManager with session {session_id}")
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = Path(base_dir)
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Set up required directories."""
        for dir_name in ["research", "writing", "editing"]:
            (self.base_dir / dir_name).mkdir(parents=True, exist_ok=True)

    def _save_with_metadata(self, content: str, metadata: Optional[Dict[str, Any]], file_path: Path) -> None:
        """Save content with optional metadata."""
        try:
            data = {
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving file with metadata: {e}")
            raise

    def _read_with_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Read content and metadata from file."""
        try:
            if file_path.exists():
                with open(file_path) as f:
                    data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Error reading file with metadata: {e}")
        return None

    def save_research(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Save research content with optional metadata."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.base_dir / "research" / f"{self.session_id}_{timestamp}.json"
            self._save_with_metadata(content, metadata, file_path)
            logger.info(f"Saved research to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving research: {e}")
            raise

    def save_article(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Save written article with optional metadata."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.base_dir / "writing" / f"{self.session_id}_{timestamp}.json"
            self._save_with_metadata(content, metadata, file_path)
            logger.info(f"Saved article to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            raise

    def save_review(self, content: str, approved: bool = False, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Save editor's review with optional metadata."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.base_dir / "editing" / f"{self.session_id}_{timestamp}.json"
            
            # Add status to metadata
            if metadata is None:
                metadata = {}
            metadata["status"] = "APPROVED" if approved else "NEEDS_REVISION"
            
            self._save_with_metadata(content, metadata, file_path)
            
            # If approved, also save as final version
            if approved:
                final_path = self.base_dir / "editing" / "final.json"
                self._save_with_metadata(content, metadata, final_path)
                
            logger.info(f"Saved review to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving review: {e}")
            raise

    def save_draft(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Save draft content with optional metadata.
        
        This is an alias for save_article to maintain backward compatibility.
        """
        return self.save_article(content, metadata)

    def get_latest_research(self) -> Optional[Dict[str, Any]]:
        """Get latest research content and metadata."""
        try:
            research_files = list(Path(self.base_dir / "research").glob("*.json"))
            if research_files:
                latest = max(research_files, key=lambda x: x.stat().st_mtime)
                return self._read_with_metadata(latest)
        except Exception as e:
            logger.error(f"Error getting latest research: {e}")
        return None

    def get_latest_article(self) -> Optional[Dict[str, Any]]:
        """Get latest written article and metadata."""
        try:
            article_files = list(Path(self.base_dir / "writing").glob("*.json"))
            if article_files:
                latest = max(article_files, key=lambda x: x.stat().st_mtime)
                return self._read_with_metadata(latest)
        except Exception as e:
            logger.error(f"Error getting latest article: {e}")
        return None

    def get_latest_review(self) -> Optional[Dict[str, Any]]:
        """Get latest review with metadata."""
        try:
            review_files = list(Path(self.base_dir / "editing").glob("*.json"))
            if review_files:
                latest = max(review_files, key=lambda x: x.stat().st_mtime)
                return self._read_with_metadata(latest)
        except Exception as e:
            logger.error(f"Error getting latest review: {e}")
        return None

    def get_latest_draft(self) -> Optional[Dict[str, Any]]:
        """Get latest draft content and metadata.
        
        This is an alias for get_latest_article to maintain backward compatibility.
        """
        return self.get_latest_article()

    def cleanup(self) -> None:
        """Clean up all files."""
        try:
            if self.base_dir.exists():
                shutil.rmtree(self.base_dir)
            logger.info(f"Cleaned up files in {self.base_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")

    def get_all_files(self) -> Dict[str, List[Path]]:
        """Get all files organized by type."""
        try:
            return {
                "research": list(Path(self.base_dir / "research").glob("*.json")),
                "writing": list(Path(self.base_dir / "writing").glob("*.json")),
                "editing": list(Path(self.base_dir / "editing").glob("*.json"))
            }
        except Exception as e:
            logger.error(f"Error getting files: {e}")
            return {}

    def recover_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recover session state from files.
        
        Args:
            session_id: Session ID to recover
            
        Returns:
            Dictionary containing latest research, article and review if found
        """
        try:
            # Find all files for session
            research_files = list(Path(self.base_dir / "research").glob(f"{session_id}_*.json"))
            writing_files = list(Path(self.base_dir / "writing").glob(f"{session_id}_*.json"))
            editing_files = list(Path(self.base_dir / "editing").glob(f"{session_id}_*.json"))
            
            state = {}
            
            # Get latest research
            if research_files:
                latest = max(research_files, key=lambda x: x.stat().st_mtime)
                state["research"] = self._read_with_metadata(latest)
                
            # Get latest article
            if writing_files:
                latest = max(writing_files, key=lambda x: x.stat().st_mtime)
                state["writing"] = self._read_with_metadata(latest)
                
            # Get latest review
            if editing_files:
                latest = max(editing_files, key=lambda x: x.stat().st_mtime)
                state["editing"] = self._read_with_metadata(latest)
                
            return state if state else None
            
        except Exception as e:
            logger.error(f"Error recovering session: {e}")
            return None 