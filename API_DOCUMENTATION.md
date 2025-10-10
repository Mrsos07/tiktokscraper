# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API uses API key authentication via header:

```
X-API-Key: your-api-key-here
```

Configure API keys in `.env` file.

## Endpoints

### Jobs

#### Create Job

Create a new scraping job.

**Endpoint:** `POST /jobs`

**Request Body:**
```json
{
  "mode": "profile",
  "value": "khaby.lame",
  "limit": 50,
  "no_watermark": true,
  "since": "2024-01-01T00:00:00Z",
  "until": "2024-12-31T23:59:59Z",
  "drive_folder_id": "optional-folder-id"
}
```

**Parameters:**
- `mode` (required): `"profile"` or `"hashtag"`
- `value` (required): Username (without @) or hashtag (without #)
- `limit` (optional): Number of videos to scrape (1-200, default: 50)
- `no_watermark` (optional): Attempt no-watermark download (default: true)
- `since` (optional): Filter videos created after this date
- `until` (optional): Filter videos created before this date
- `drive_folder_id` (optional): Custom Google Drive folder ID

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "profile",
  "value": "khaby.lame",
  "limit": 50,
  "no_watermark": true,
  "status": "pending",
  "progress": 0,
  "total_videos": 0,
  "successful_downloads": 0,
  "failed_downloads": 0,
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Get Job Status

Get detailed status of a specific job.

**Endpoint:** `GET /jobs/{job_id}`

**Response:** `200 OK`
```json
{
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "mode": "profile",
    "value": "khaby.lame",
    "status": "running",
    "progress": 45,
    "total_videos": 50,
    "successful_downloads": 22,
    "failed_downloads": 1
  },
  "videos": [
    {
      "id": "7123456789012345678",
      "url": "https://www.tiktok.com/@khaby.lame/video/7123456789012345678",
      "author_username": "khaby.lame",
      "status": "uploaded",
      "views": 1000000,
      "likes": 50000,
      "drive_file_id": "1abc..."
    }
  ],
  "drive_links": [
    {
      "video_id": "7123456789012345678",
      "video_link": "https://drive.google.com/file/d/1abc.../view",
      "metadata_link": "https://drive.google.com/file/d/1def.../view",
      "folder_path": "TikTok/profile/khaby.lame/2025/01"
    }
  ]
}
```

#### List Jobs

List all jobs with optional filters.

**Endpoint:** `GET /jobs`

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `running`, `completed`, `failed`, `cancelled`)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "mode": "profile",
    "value": "khaby.lame",
    "status": "completed",
    "progress": 100,
    "total_videos": 50,
    "successful_downloads": 48,
    "failed_downloads": 2,
    "created_at": "2025-01-15T10:30:00Z",
    "completed_at": "2025-01-15T11:15:00Z"
  }
]
```

#### Cancel Job

Cancel a running or pending job.

**Endpoint:** `POST /jobs/{job_id}/cancel`

**Response:** `200 OK`

#### Delete Job

Delete a job and all associated videos.

**Endpoint:** `DELETE /jobs/{job_id}`

**Response:** `204 No Content`

---

### Videos

#### List Videos

Query videos with various filters.

**Endpoint:** `GET /videos`

**Query Parameters:**
- `mode` (optional): Filter by mode (`profile`, `hashtag`)
- `value` (optional): Filter by username or hashtag
- `author_username` (optional): Filter by video author
- `hashtag` (optional): Filter by hashtag in video
- `status` (optional): Filter by status
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "total": 150,
  "videos": [
    {
      "id": "7123456789012345678",
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://www.tiktok.com/@khaby.lame/video/7123456789012345678",
      "desc": "Video description",
      "author_username": "khaby.lame",
      "author_nickname": "Khabane Lame",
      "views": 1000000,
      "likes": 50000,
      "comments": 1000,
      "shares": 5000,
      "created_at_tiktok": "2025-01-10T15:30:00Z",
      "hashtags": ["funny", "comedy"],
      "music_title": "Original Sound",
      "has_watermark": false,
      "file_size": 5242880,
      "duration": 15.5,
      "drive_file_id": "1abc...",
      "drive_folder_path": "TikTok/profile/khaby.lame/2025/01",
      "status": "uploaded"
    }
  ]
}
```

#### Get Video

Get detailed information about a specific video.

**Endpoint:** `GET /videos/{video_id}`

**Response:** `200 OK`

#### Retry Video Download

Retry downloading and uploading a failed video.

**Endpoint:** `POST /videos/{video_id}/retry`

**Response:** `200 OK`

#### Delete Video

Delete a video record (does not delete from Google Drive).

**Endpoint:** `DELETE /videos/{video_id}`

**Response:** `204 No Content`

---

### Scheduled Jobs

#### Create Scheduled Job

Create a recurring scheduled job.

**Endpoint:** `POST /scheduled-jobs`

**Request Body:**
```json
{
  "name": "Daily Scrape - @khaby.lame",
  "mode": "profile",
  "value": "khaby.lame",
  "limit": 50,
  "no_watermark": true,
  "interval_minutes": 1440,
  "enabled": true
}
```

**Parameters:**
- `name` (required): Job name
- `mode` (required): `"profile"` or `"hashtag"`
- `value` (required): Username or hashtag
- `limit` (optional): Videos per run (default: 50)
- `interval_minutes` (required): Interval in minutes (min: 5)
- `no_watermark` (optional): Default: true
- `enabled` (optional): Default: true

**Response:** `201 Created`

#### List Scheduled Jobs

**Endpoint:** `GET /scheduled-jobs`

**Query Parameters:**
- `enabled` (optional): Filter by enabled status

**Response:** `200 OK`
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "name": "Daily Scrape - @khaby.lame",
    "mode": "profile",
    "value": "khaby.lame",
    "limit": 50,
    "interval_minutes": 1440,
    "enabled": true,
    "last_run_at": "2025-01-15T10:00:00Z",
    "next_run_at": "2025-01-16T10:00:00Z",
    "total_runs": 30,
    "successful_runs": 28,
    "failed_runs": 2
  }
]
```

#### Get Scheduled Job

**Endpoint:** `GET /scheduled-jobs/{job_id}`

**Response:** `200 OK`

#### Update Scheduled Job

**Endpoint:** `PATCH /scheduled-jobs/{job_id}`

**Request Body:** Same as create

**Response:** `200 OK`

#### Toggle Scheduled Job

Enable/disable a scheduled job.

**Endpoint:** `POST /scheduled-jobs/{job_id}/toggle`

**Response:** `200 OK`

#### Delete Scheduled Job

**Endpoint:** `DELETE /scheduled-jobs/{job_id}`

**Response:** `204 No Content`

---

### Statistics

#### Get System Stats

Get overall system statistics.

**Endpoint:** `GET /stats`

**Response:** `200 OK`
```json
{
  "total_jobs": 150,
  "pending_jobs": 5,
  "running_jobs": 2,
  "completed_jobs": 140,
  "failed_jobs": 3,
  "total_videos": 7500,
  "downloaded_videos": 7200,
  "uploaded_videos": 7000,
  "failed_videos": 200,
  "total_storage_bytes": 52428800000,
  "scheduled_jobs_count": 10,
  "active_scheduled_jobs": 8
}
```

#### Health Check

**Endpoint:** `GET /stats/health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "database": true,
  "google_drive": true,
  "scheduler": true
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request**
```json
{
  "detail": "Invalid request parameters"
}
```

**404 Not Found**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error",
  "error": "Error details (if DEBUG=true)"
}
```

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "mode"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

The API implements rate limiting:
- Default: 10 requests per minute
- Burst: 20 requests

Configure in `.env`:
```
RATE_LIMIT_REQUESTS_PER_MINUTE=10
RATE_LIMIT_BURST=20
```

---

## Pagination

List endpoints support pagination:
- `limit`: Number of results per page
- `offset`: Number of results to skip

Example:
```
GET /videos?limit=50&offset=100
```

---

## Filtering

### Date Filtering

Use ISO 8601 format for dates:
```json
{
  "since": "2024-01-01T00:00:00Z",
  "until": "2024-12-31T23:59:59Z"
}
```

### Status Filtering

Valid status values:
- Jobs: `pending`, `running`, `completed`, `failed`, `cancelled`
- Videos: `pending`, `downloading`, `downloaded`, `uploading`, `uploaded`, `failed`

---

## WebSocket Support (Future)

Real-time job progress updates via WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/{job_id}');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
};
```

---

## SDK Examples

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Create job
response = requests.post(f"{API_URL}/jobs", json={
    "mode": "profile",
    "value": "khaby.lame",
    "limit": 50,
    "no_watermark": True
})
job = response.json()
job_id = job["id"]

# Check status
response = requests.get(f"{API_URL}/jobs/{job_id}")
status = response.json()
print(f"Progress: {status['job']['progress']}%")
```

### JavaScript

```javascript
const API_URL = "http://localhost:8000/api/v1";

// Create job
const response = await fetch(`${API_URL}/jobs`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    mode: "profile",
    value: "khaby.lame",
    limit: 50,
    no_watermark: true
  })
});
const job = await response.json();

// Check status
const statusResponse = await fetch(`${API_URL}/jobs/${job.id}`);
const status = await statusResponse.json();
console.log(`Progress: ${status.job.progress}%`);
```

### cURL

```bash
# Create job
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "profile",
    "value": "khaby.lame",
    "limit": 50,
    "no_watermark": true
  }'

# Get job status
curl http://localhost:8000/api/v1/jobs/{job_id}

# List videos
curl "http://localhost:8000/api/v1/videos?mode=profile&value=khaby.lame&limit=20"
```

---

## Interactive Documentation

Access interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
