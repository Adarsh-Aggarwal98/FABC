# Monitoring & Capacity Planning Guide

## Overview

This document explains how to use Prometheus metrics to monitor the CRM system and calculate how many concurrent users the system can handle.

---

## Table of Contents

1. [Metrics Available](#metrics-available)
2. [Accessing Metrics](#accessing-metrics)
3. [Key Performance Indicators](#key-performance-indicators)
4. [Capacity Planning Calculations](#capacity-planning-calculations)
5. [Grafana Setup (Local)](#grafana-setup-local)
6. [Prometheus Queries](#prometheus-queries)
7. [Alerting Thresholds](#alerting-thresholds)

---

## Metrics Available

### HTTP Request Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests (by method, endpoint, status_code) |
| `http_request_duration_seconds` | Histogram | Request latency in seconds |
| `http_request_size_bytes` | Histogram | Request body size in bytes |
| `http_response_size_bytes` | Histogram | Response body size in bytes |
| `http_requests_in_progress` | Gauge | Currently processing requests |

### Status Code Buckets

| Metric | Description |
|--------|-------------|
| `http_requests_2xx_total` | Successful responses |
| `http_requests_4xx_total` | Client errors (bad request, unauthorized, etc.) |
| `http_requests_5xx_total` | Server errors |

### System Metrics

| Metric | Description |
|--------|-------------|
| `system_cpu_usage_percent` | Overall CPU usage |
| `system_memory_usage_percent` | Memory usage percentage |
| `system_memory_usage_bytes` | Memory used in bytes |
| `system_memory_available_bytes` | Available memory |
| `system_disk_usage_percent` | Disk usage by mount point |
| `process_cpu_usage_percent` | API process CPU usage |
| `process_memory_bytes` | API process memory |
| `process_threads_total` | Number of threads |

### Authentication Metrics

| Metric | Description |
|--------|-------------|
| `auth_login_attempts_total` | Login attempts (success/failure) |
| `auth_token_operations_total` | Token operations (issued, refreshed, expired) |

### Business Metrics

| Metric | Description |
|--------|-------------|
| `business_service_requests_created_total` | Service requests created |
| `business_invoices_generated_total` | Invoices generated |
| `business_submissions_received_total` | Form submissions |

---

## Accessing Metrics

### Direct Endpoint (Raw Prometheus Format)

```bash
# Local development
curl http://localhost:9001/metrics

# Production
curl https://pointersconsulting.com.au/api/metrics
```

### Prometheus UI

```
# Local
http://localhost:9090

# Production
http://your-server-ip:9090
```

### Grafana Dashboard

```
# Local (if installed separately)
http://localhost:3000

# Production (via Docker)
http://your-server-ip:3001
```

---

## Key Performance Indicators

### 1. Request Rate (Throughput)

**What it measures:** How many requests per second the system handles

```promql
# Current request rate (requests/second)
sum(rate(http_requests_total[5m]))

# By endpoint
sum by (endpoint) (rate(http_requests_total[5m]))
```

### 2. Response Time (Latency)

**What it measures:** How long requests take to complete

```promql
# 50th percentile (median)
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# 95th percentile
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# 99th percentile
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

### 3. Error Rate

**What it measures:** Percentage of requests that fail

```promql
# 5xx error rate
sum(rate(http_requests_5xx_total[5m])) / sum(rate(http_requests_total[5m]))

# 4xx error rate
sum(rate(http_requests_4xx_total[5m])) / sum(rate(http_requests_total[5m]))
```

### 4. Saturation (Resource Usage)

**What it measures:** How close to capacity the system is

```promql
# CPU saturation
system_cpu_usage_percent

# Memory saturation
system_memory_usage_percent

# In-flight requests (concurrency)
sum(http_requests_in_progress)
```

---

## Capacity Planning Calculations

### Step 1: Determine Baseline Metrics

Run a load test or observe production traffic to establish:

| Metric | How to Get | Example Value |
|--------|------------|---------------|
| Average requests per user per minute | `total_requests / active_users / minutes` | 5 req/min |
| Average response time | P95 latency | 200ms |
| Request size | P95 request size | 2KB |
| Response size | P95 response size | 10KB |

### Step 2: Calculate Maximum Throughput

**Formula:**
```
Max Requests/Second = (Available CPU cores × Efficiency Factor) / Avg Response Time
```

**Example:**
- 4 CPU cores
- 70% efficiency (accounting for overhead)
- 200ms average response time

```
Max RPS = (4 × 0.70) / 0.2 = 14 requests/second = 840 requests/minute
```

### Step 3: Calculate Maximum Concurrent Users

**Formula:**
```
Max Users = Max Requests/Minute ÷ Requests per User per Minute
```

**Example:**
```
Max Users = 840 ÷ 5 = 168 concurrent users
```

### Step 4: Apply Safety Margin

Always plan for 70% capacity to handle spikes:

```
Recommended Max Users = Max Users × 0.70
                      = 168 × 0.70
                      = ~117 concurrent users
```

### Complete Capacity Estimation Table

| Server Size | CPU | RAM | Est. Max RPS | Est. Concurrent Users |
|-------------|-----|-----|--------------|----------------------|
| Small | 2 cores | 4GB | 7 rps | ~60 users |
| Medium | 4 cores | 8GB | 14 rps | ~120 users |
| Large | 8 cores | 16GB | 28 rps | ~240 users |
| X-Large | 16 cores | 32GB | 56 rps | ~480 users |

> **Note:** These are estimates. Actual capacity depends on query complexity, database performance, and network conditions.

---

## Grafana Setup (Local)

### Option 1: Download Grafana Standalone

1. **Download from:** https://grafana.com/grafana/download

2. **Windows Installation:**
   ```powershell
   # Download MSI installer and run
   # Default location: C:\Program Files\GrafanaLabs\grafana

   # Start service
   net start grafana
   ```

3. **Access:** http://localhost:3000 (admin/admin)

### Option 2: Run with Docker (Simple)

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana:latest
```

### Configure Data Source

1. Go to **Configuration > Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Set URL: `http://localhost:9090` (or your Prometheus server)
5. Click **Save & Test**

### Import Dashboard

1. Go to **Dashboards > Import**
2. Upload the JSON file from: `monitoring/grafana/dashboards/crm-dashboard.json`
3. Select your Prometheus data source
4. Click **Import**

---

## Prometheus Queries

### Essential Queries for Capacity Planning

```promql
# 1. Current Request Rate
sum(rate(http_requests_total[5m]))

# 2. Request Rate by Status Code
sum by (status_code) (rate(http_requests_total[5m]))

# 3. P95 Response Time
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# 4. Error Rate Percentage
100 * sum(rate(http_requests_5xx_total[5m])) / sum(rate(http_requests_total[5m]))

# 5. Average Request Size
sum(rate(http_request_size_bytes_sum[5m])) / sum(rate(http_request_size_bytes_count[5m]))

# 6. Average Response Size
sum(rate(http_response_size_bytes_sum[5m])) / sum(rate(http_response_size_bytes_count[5m]))

# 7. In-Progress Requests (Concurrency)
sum(http_requests_in_progress)

# 8. CPU Usage
system_cpu_usage_percent

# 9. Memory Usage
system_memory_usage_percent

# 10. Top 10 Slowest Endpoints
topk(10, histogram_quantile(0.95, sum by (endpoint, le) (rate(http_request_duration_seconds_bucket[5m]))))

# 11. Top 10 Busiest Endpoints
topk(10, sum by (endpoint) (rate(http_requests_total[5m])))

# 12. Login Success Rate
sum(rate(auth_login_attempts_total{status="success"}[5m])) / sum(rate(auth_login_attempts_total[5m]))
```

### Capacity-Related Queries

```promql
# Requests per minute (easier to understand)
sum(rate(http_requests_total[5m])) * 60

# Available headroom (if max is 1000 rpm)
1000 - (sum(rate(http_requests_total[5m])) * 60)

# CPU headroom
100 - system_cpu_usage_percent

# Memory headroom (in GB)
system_memory_available_bytes / 1024 / 1024 / 1024
```

---

## Alerting Thresholds

### Recommended Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| P95 Latency | > 1s | > 3s | Scale up or optimize queries |
| Error Rate (5xx) | > 1% | > 5% | Investigate and fix |
| CPU Usage | > 70% | > 90% | Scale up |
| Memory Usage | > 75% | > 90% | Scale up or investigate leaks |
| Request Rate | > 80% capacity | > 95% capacity | Scale up |
| Disk Usage | > 80% | > 95% | Add storage or clean up |

### When to Scale

**Scale UP when (any of these for > 10 minutes):**
- CPU consistently > 70%
- Memory consistently > 75%
- P95 latency > 1 second
- Error rate > 1%

**Scale DOWN when (all of these for > 1 hour):**
- CPU consistently < 30%
- Memory consistently < 40%
- P95 latency < 200ms
- Request rate < 30% of capacity

---

## Load Testing

### Quick Load Test with curl

```bash
# Simple load test (100 requests, 10 concurrent)
for i in {1..100}; do
  curl -s http://localhost:9001/api/health &
  if (( $i % 10 == 0 )); then wait; fi
done
wait
```

### Using Apache Bench (ab)

```bash
# 1000 requests, 50 concurrent
ab -n 1000 -c 50 http://localhost:9001/api/health
```

### Using hey (recommended)

```bash
# Install: go install github.com/rakyll/hey@latest

# 30 seconds of load, 50 concurrent users
hey -z 30s -c 50 http://localhost:9001/api/health
```

### Interpreting Load Test Results

After running a load test, check these metrics:

1. **Max RPS achieved** before degradation
2. **P95 latency** at different load levels
3. **Error rate** at different load levels
4. **CPU/Memory** usage at peak load

Create a table like this:

| Concurrent Users | RPS | P95 Latency | Error Rate | CPU | Memory |
|-----------------|-----|-------------|------------|-----|--------|
| 10 | 50 | 100ms | 0% | 20% | 30% |
| 50 | 200 | 150ms | 0% | 50% | 40% |
| 100 | 350 | 300ms | 0.1% | 75% | 50% |
| 200 | 400 | 800ms | 2% | 95% | 65% |
| 300 | 380 | 2s | 10% | 100% | 80% |

**In this example:** Maximum recommended capacity is ~100 concurrent users (before latency degrades significantly).

---

## Summary: Quick Capacity Check

Run these queries to quickly assess capacity:

```bash
# 1. Current load (requests/minute)
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total[5m]))*60'

# 2. P95 response time
curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,sum(rate(http_request_duration_seconds_bucket[5m]))by(le))'

# 3. Error rate
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_5xx_total[5m]))/sum(rate(http_requests_total[5m]))'

# 4. CPU usage
curl -s 'http://localhost:9090/api/v1/query?query=system_cpu_usage_percent'

# 5. Memory usage
curl -s 'http://localhost:9090/api/v1/query?query=system_memory_usage_percent'
```

---

## Need Help?

- **Prometheus Docs:** https://prometheus.io/docs/
- **Grafana Docs:** https://grafana.com/docs/
- **PromQL Cheat Sheet:** https://promlabs.com/promql-cheat-sheet/
