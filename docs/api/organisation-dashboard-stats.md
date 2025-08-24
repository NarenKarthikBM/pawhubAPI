# Organisation Dashboard Statistics API

## Overview
The Organisation Dashboard Statistics API provides comprehensive statistics for authenticated organisations, including mission statistics, adoption management data, nearby activity metrics, and recent activity summaries.

## Endpoint
```
GET /api/organisations/dashboard/stats/
```

## Authentication
- **Required**: Organisation Token Authentication
- **Header**: `Authorization: Token <organisation_auth_token>`

## Response Format

### Success Response (200 OK)
```json
{
    "success": true,
    "message": "Dashboard statistics retrieved successfully",
    "stats": {
        "missions": {
            "total": 25,
            "active": 3,
            "upcoming": 5,
            "completed": 17
        },
        "adoptions": {
            "total_listings": 12,
            "active_listings": 8,
            "completed_adoptions": 4
        },
        "nearby_activity": {
            "sightings_count": 45,
            "emergencies_count": 8,
            "active_emergencies": 2
        },
        "recent_activity": {
            "recent_missions": 2,
            "recent_sightings": 15,
            "recent_emergencies": 3
        }
    }
}
```

## Statistics Breakdown

### Mission Statistics
- **total**: Total number of missions created by the organisation
- **active**: Currently ongoing missions (started but not ended)
- **upcoming**: Missions scheduled for the future
- **completed**: Missions that have ended

### Adoption Statistics
- **total_listings**: Total adoption listings created by the organisation
- **active_listings**: Current adoption listings (not yet adopted)
- **completed_adoptions**: Successfully completed adoptions

### Nearby Activity (within 20km radius)
- **sightings_count**: Total animal sightings reported in the area
- **emergencies_count**: Total emergency reports in the area
- **active_emergencies**: Currently active emergency reports

### Recent Activity (last 7 days)
- **recent_missions**: New missions created in the last 7 days
- **recent_sightings**: New sightings reported in the area (last 7 days)
- **recent_emergencies**: New emergencies reported in the area (last 7 days)

## Error Responses

### Authentication Error (401)
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Server Error (500)
```json
{
    "success": false,
    "error": "Failed to retrieve dashboard statistics: <error_message>"
}
```

## Usage Example

### cURL
```bash
curl -X GET "https://pawhub.ddns.net/api/organisations/dashboard/stats/" \
     -H "Authorization: Token your_organisation_token_here" \
     -H "Content-Type: application/json"
```

### JavaScript (Frontend Integration)
```javascript
const response = await fetch('/api/organisations/dashboard/stats/', {
    headers: {
        'Authorization': `Token ${organisationToken}`,
        'Content-Type': 'application/json'
    }
});

const data = await response.json();
if (data.success) {
    console.log('Dashboard Stats:', data.stats);
}
```

## Notes
- If the organisation doesn't have a location set, nearby activity statistics will return 0
- The 20km radius for nearby activity is calculated from the organisation's registered location
- Recent activity is calculated based on the last 7 days from the current timestamp
- All timestamps are in UTC
