"""
Sequence tracker for WebSocket Sync.

Tracks sequence numbers for events to enable missed event detection and sync.
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SequenceTracker:
    """
    Tracks sequence numbers for events per user.

    Enables clients to detect missed events and request sync for gaps.
    """

    def __init__(self, max_history_hours: int = 24):
        """
        Initialize sequence tracker.

        Args:
            max_history_hours: Maximum hours to keep event history
        """
        # Map of userId -> current sequence number
        self.current_sequences: Dict[str, int] = {}

        # Map of userId -> list of (sequence, event_data, timestamp)
        self.event_history: Dict[str, List[tuple]] = {}

        # Maximum history to keep
        self.max_history_hours = max_history_hours

    def get_next_sequence(self, user_id: str) -> int:
        """
        Get the next sequence number for a user.

        Args:
            user_id: User ID

        Returns:
            Next sequence number
        """
        current = self.current_sequences.get(user_id, 0)
        next_seq = current + 1
        self.current_sequences[user_id] = next_seq
        return next_seq

    def get_current_sequence(self, user_id: str) -> int:
        """
        Get the current sequence number for a user.

        Args:
            user_id: User ID

        Returns:
            Current sequence number
        """
        return self.current_sequences.get(user_id, 0)

    def record_event(self, user_id: str, sequence: int, event_data: Dict) -> None:
        """
        Record an event in the history.

        Args:
            user_id: User ID
            sequence: Sequence number
            event_data: Event data
        """
        if user_id not in self.event_history:
            self.event_history[user_id] = []

        timestamp = datetime.utcnow()
        self.event_history[user_id].append((sequence, event_data, timestamp))

        # Clean up old events
        self._cleanup_old_events(user_id)

        logger.debug(f"Recorded event {sequence} for user {user_id}")

    def get_missed_events(self, user_id: str, last_sequence: int) -> List[Dict]:
        """
        Get events that occurred after a given sequence number.

        Args:
            user_id: User ID
            last_sequence: Last sequence number the client has

        Returns:
            List of missed events
        """
        if user_id not in self.event_history:
            return []

        missed = []
        for seq, event_data, timestamp in self.event_history[user_id]:
            if seq > last_sequence:
                missed.append({
                    "sequence": seq,
                    "event": event_data,
                    "timestamp": timestamp.isoformat()
                })

        logger.info(f"Found {len(missed)} missed events for user {user_id} after sequence {last_sequence}")
        return missed

    def has_gap(self, user_id: str, last_sequence: int) -> bool:
        """
        Check if there's a gap between client's sequence and current sequence.

        Args:
            user_id: User ID
            last_sequence: Last sequence number the client has

        Returns:
            True if there's a gap, False otherwise
        """
        current = self.get_current_sequence(user_id)
        return current > last_sequence

    def get_gap_size(self, user_id: str, last_sequence: int) -> int:
        """
        Get the size of the gap between client's sequence and current sequence.

        Args:
            user_id: User ID
            last_sequence: Last sequence number the client has

        Returns:
            Number of missed events
        """
        current = self.get_current_sequence(user_id)
        return max(0, current - last_sequence)

    def _cleanup_old_events(self, user_id: str) -> None:
        """
        Remove events older than max_history_hours.

        Args:
            user_id: User ID
        """
        if user_id not in self.event_history:
            return

        cutoff_time = datetime.utcnow() - timedelta(hours=self.max_history_hours)

        # Filter out old events
        self.event_history[user_id] = [
            (seq, event, ts)
            for seq, event, ts in self.event_history[user_id]
            if ts > cutoff_time
        ]

        # Limit to last 1000 events per user to prevent memory issues
        if len(self.event_history[user_id]) > 1000:
            self.event_history[user_id] = self.event_history[user_id][-1000:]

    def cleanup_all_old_events(self) -> int:
        """
        Clean up old events for all users.

        Returns:
            Number of events cleaned up
        """
        total_cleaned = 0

        for user_id in list(self.event_history.keys()):
            before_count = len(self.event_history[user_id])
            self._cleanup_old_events(user_id)
            after_count = len(self.event_history[user_id])
            total_cleaned += (before_count - after_count)

            # Remove empty histories
            if not self.event_history[user_id]:
                del self.event_history[user_id]

        if total_cleaned > 0:
            logger.info(f"Cleaned up {total_cleaned} old event(s)")

        return total_cleaned

    def reset_user_sequence(self, user_id: str) -> None:
        """
        Reset sequence tracking for a user.

        Args:
            user_id: User ID
        """
        if user_id in self.current_sequences:
            del self.current_sequences[user_id]

        if user_id in self.event_history:
            del self.event_history[user_id]

        logger.info(f"Reset sequence tracking for user {user_id}")

    def get_stats(self) -> Dict:
        """
        Get statistics about sequence tracking.

        Returns:
            Dictionary with stats
        """
        total_events = sum(len(events) for events in self.event_history.values())

        return {
            "tracked_users": len(self.current_sequences),
            "total_events_in_history": total_events,
            "max_history_hours": self.max_history_hours,
            "users_with_history": len(self.event_history)
        }
