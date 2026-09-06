import datetime
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from nextcord.enums import ScheduledEventEntityType
from nextcord.guild import Guild
from nextcord.scheduled_events import EntityMetadata


class TestCreateScheduledEvent(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.http = SimpleNamespace(create_event=AsyncMock(return_value={"id": "1"}))
        self.guild = object.__new__(Guild)
        self.guild.id = 123
        self.guild._state = SimpleNamespace(http=self.http)
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

    async def test_external_event_requires_metadata(self) -> None:
        error = None
        try:
            await self.guild.create_scheduled_event(
                name="External event",
                entity_type=ScheduledEventEntityType.external,
                start_time=self.start_time,
            )
        except ValueError as exc:
            error = str(exc)

        assert error is not None, "missing metadata should be rejected"
        assert "require a metadata location" in error

        self.http.create_event.assert_not_awaited()

    async def test_external_event_requires_metadata_location(self) -> None:
        error = None
        try:
            await self.guild.create_scheduled_event(
                name="External event",
                entity_type=ScheduledEventEntityType.external,
                start_time=self.start_time,
                metadata=EntityMetadata(),
            )
        except ValueError as exc:
            error = str(exc)

        assert error is not None, "metadata without a location should be rejected"
        assert "require a metadata location" in error

        self.http.create_event.assert_not_awaited()

    async def test_external_event_accepts_metadata_location(self) -> None:
        event = object()
        metadata = EntityMetadata(location="Conference hall")

        with patch.object(Guild, "_store_scheduled_event", return_value=event):
            result = await self.guild.create_scheduled_event(
                name="External event",
                entity_type=ScheduledEventEntityType.external,
                start_time=self.start_time,
                metadata=metadata,
            )

        assert result is event
        self.http.create_event.assert_awaited_once_with(
            123,
            reason=None,
            name="External event",
            entity_type=ScheduledEventEntityType.external.value,
            scheduled_start_time=self.start_time.isoformat(),
            entity_metadata=metadata.__dict__,
            privacy_level=2,
        )

    async def test_voice_event_does_not_require_metadata(self) -> None:
        event = object()

        with patch.object(Guild, "_store_scheduled_event", return_value=event):
            result = await self.guild.create_scheduled_event(
                name="Voice event",
                entity_type=ScheduledEventEntityType.voice,
                start_time=self.start_time,
            )

        assert result is event
        self.http.create_event.assert_awaited_once()
        assert "entity_metadata" not in self.http.create_event.await_args.kwargs


if __name__ == "__main__":
    unittest.main()
