# Docker Deployment Guide

## Overview
This Docker setup runs the email agent that monitors inbox, extracts fields from attachments, and generates summary emails. The agent executes **every 30 minutes** automatically using cron.

## Prerequisites
- Docker Engine 20.10+
- Docker Compose 1.29+
- Valid `.env` file with credentials

## Quick Start

### 1. Build the Image
```bash
docker-compose build
```

### 2. Start the Container
```bash
docker-compose up -d
```

### 3. View Logs
```bash
docker-compose logs -f
```

### 4. Stop the Container
```bash
docker-compose down
```

## Configuration

### Environment Variables (.env)
Ensure your `.env` file contains:
```
OPENAI_API_KEY=your_openai_api_key
EMAIL_PASSWORD=your_email_app_password
```

### Required Files
- `config.json` - SMTP and IMAP configuration
- `FieldConfigrationFile.xlsx` - Field extraction configuration
- `.env` - Environment variables

## Cron Schedule
- **Frequency**: Every 30 minutes
- **Cron Expression**: `*/30 * * * *`
- **Timezone**: Asia/Kolkata (IST)

To modify the schedule, edit the cron expression in `Dockerfile`:
```dockerfile
RUN echo "*/30 * * * * cd /app && /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/email-agent-cron
```

## Docker Commands

### Build Without Cache
```bash
docker-compose build --no-cache
```

### View Container Status
```bash
docker-compose ps
```

### Execute Command Inside Container
```bash
docker-compose exec email-agent bash
```

### View Cron Logs
```bash
docker-compose exec email-agent tail -f /var/log/cron.log
```

### Restart Container
```bash
docker-compose restart
```

## Volumes
Data is persisted in these directories:
- `./email_attachments` - Downloaded email attachments
- `./output` - Extraction results
- `./logs` - Application logs

## Troubleshooting

### Container Exits Immediately
Check logs:
```bash
docker-compose logs email-agent
```

### Cron Not Running
Verify cron is active:
```bash
docker-compose exec email-agent ps aux | grep cron
```

### Permission Issues
Ensure entrypoint script is executable:
```bash
chmod +x entrypoint.sh
```

### Environment Variables Not Loaded
Verify `.env` file exists and is mounted:
```bash
docker-compose exec email-agent env | grep OPENAI
```

## Production Deployment

### AWS EC2 / Cloud VM
1. Install Docker and Docker Compose
2. Clone repository
3. Create `.env` file with credentials
4. Run `docker-compose up -d`
5. Setup monitoring with CloudWatch or similar

### Health Checks
The container includes a health check that verifies the cron log file exists every 5 minutes.

### Monitoring
View real-time logs:
```bash
docker-compose logs -f --tail=100
```

### Resource Limits
Add resource constraints in `docker-compose.yml`:
```yaml
services:
  email-agent:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Security Best Practices

1. **Never commit `.env` file** - Keep it in `.gitignore`
2. **Use read-only volumes** for config files
3. **Rotate credentials** regularly
4. **Enable Docker logging** for audit trails
5. **Update base image** regularly for security patches

## Maintenance

### Update Dependencies
```bash
docker-compose build --pull
docker-compose up -d
```

### Backup Data
```bash
tar -czf backup_$(date +%Y%m%d).tar.gz email_attachments/ output/
```

### Clear Old Logs
```bash
docker-compose exec email-agent truncate -s 0 /var/log/cron.log
```

## Support
For issues or questions, check application logs and cron logs for detailed error messages.
