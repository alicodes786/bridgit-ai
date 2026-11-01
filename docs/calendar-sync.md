# Calendar Sync System

This document explains the calendar sync system with event versioning and scheduled syncing.

## Overview

The calendar sync system pulls booking data from iCal feeds and keeps track of changes over time. It uses a versioning system to maintain a complete history of all booking events, which enables:

1. Accurate historical records of all bookings
2. Tracking of changes (date shifts, cancellations)
3. Maintaining integrity with cleaner assignments
4. Automated syncing every 5 minutes

## Database Structure

The system uses the following tables:

- `booking_events`: Stores the current state of all events
- `booking_event_versions`: Stores the change history of events
- `sync_status`: Tracks the status of sync operations
- `sync_history`: Records statistics about each sync

## How Changes Are Tracked

When an event changes (e.g., a guest changes their dates):

1. The system detects the change by comparing event fingerprints
2. It creates a version record with the previous state in `booking_event_versions`
3. It updates the event in `booking_events` with the new data
4. It increments the `version_number` of the event
5. It updates any affected cleaner assignments

For canceled events:

1. It creates a version record with change_type="canceled"
2. It marks the event as inactive in `booking_events`
3. It marks related cleaner assignments as inactive

## Setting Up Scheduled Syncing

The system includes a cron endpoint that can be scheduled to run every 5 minutes.

### Vercel Configuration

Add the following to your `vercel.json` file:

```json
{
  "crons": [
    {
      "path": "/api/cron/sync-ical-feeds",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

This tells Vercel to call the endpoint every 5 minutes.

### Other Hosting Providers

If you're not using Vercel, set up a cron job on your server to call:

```
https://yourdomain.com/api/cron/sync-ical-feeds?cron=true
```

## API Endpoints

- `GET /api/booking-events`: Get booking events with optional filters
- `POST /api/v2/sync-ical-feeds`: Manually trigger a sync
- `GET /api/cron/sync-ical-feeds`: Endpoint for scheduled syncs
- `GET /api/booking-event-history`: Get version history for a booking event

## Monitor & Troubleshooting

The system includes built-in monitoring:

1. Check sync status on the calendar page
2. View the last sync time
3. Sync operations that stall are automatically recovered
4. Failed syncs are recorded with error messages

## Recovering from Errors

If a sync fails:

1. The system will automatically retry on the next scheduled run
2. You can manually trigger a sync from the calendar page
3. Check the sync_status table for error messages 