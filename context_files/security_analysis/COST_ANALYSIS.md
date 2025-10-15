# AWS Cost Analysis & Optimization

**Project**: AWS AI Governance Framework  
**Date**: October 14, 2025  
**Analysis**: Detailed cost breakdown and optimization strategies

---

## 💰 Current Architecture Cost Breakdown

### Monthly Cost Estimate: **$138.00**

| Service | Configuration | Hours/Month | Unit Cost | Monthly Cost | % of Total |
|---------|--------------|-------------|-----------|--------------|------------|
| **ECS Fargate - Backend** | 2 tasks × 0.5 vCPU, 1GB RAM | 1,460 | $0.04048/hr | $29.55 | 21.4% |
| **ECS Fargate - Backend** | 2 tasks × 1GB storage | 1,460 | $0.004445/hr | $3.25 | 2.4% |
| **ECS Fargate - Worker** | 1 task × 0.5 vCPU, 1GB RAM | 730 | $0.04048/hr | $14.78 | 10.7% |
| **ECS Fargate - Worker** | 1 task × 1GB storage | 730 | $0.004445/hr | $1.62 | 1.2% |
| **RDS PostgreSQL** | db.t3.micro Multi-AZ | 730 | $0.041/hr | $29.93 | 21.7% |
| **ElastiCache Redis** | cache.t3.micro | 730 | $0.017/hr | $12.41 | 9.0% |
| **Application Load Balancer** | Standard ALB | 730 | $0.0225/hr | $16.43 | 11.9% |
| **ALB LCU** | ~10 LCUs | - | $0.008/LCU | $2.40 | 1.7% |
| **CloudFront** | 50GB data transfer | - | $0.085/GB | $4.25 | 3.1% |
| **S3 Storage** | 10GB Standard | - | $0.023/GB | $0.23 | 0.2% |
| **S3 Requests** | 100K GET, 10K PUT | - | Various | $0.50 | 0.4% |
| **Secrets Manager** | 2 secrets | - | $0.40/secret | $0.80 | 0.6% |
| **CloudWatch Logs** | 10GB ingestion, 10GB storage | - | Various | $5.50 | 4.0% |
| **CloudWatch Metrics** | 50 custom metrics | - | $0.30/metric | $1.50 | 1.1% |
| **Data Transfer Out** | 50GB to internet | - | $0.09/GB | $4.50 | 3.3% |
| **NAT Gateway** | 2 AZs | 1,460 | $0.045/hr | $6.57 | 4.8% |
| **NAT Gateway Data** | 20GB processed | - | $0.045/GB | $0.90 | 0.7% |
| **VPC Endpoints** | S3, ECR | - | $0.01/hr | $2.92 | 2.1% |
| **EBS Snapshots** | 20GB backup | - | $0.05/GB | $1.00 | 0.7% |
| **Total** | | | | **$138.04** | **100%** |

---

## 📊 Cost Distribution by Category

### Compute (35.7% - $49.20)
- **ECS Fargate**: $49.20/month
  - Backend API: 2 tasks running 24/7
  - Celery Worker: 1 task running 24/7
  - **Why it costs this much**: Fargate charges per vCPU-hour and GB-hour

### Database (31.7% - $43.74)
- **RDS PostgreSQL Multi-AZ**: $29.93/month
  - Primary + standby instance
  - Automated backups (7 days)
  - **Why it costs this much**: Multi-AZ doubles the cost for high availability
  
- **ElastiCache Redis**: $12.41/month
  - Single node for caching
  - **Why it costs this much**: Managed service overhead

- **EBS Snapshots**: $1.00/month
  - Database backups
  - **Why it costs this much**: Incremental snapshot storage

- **Secrets Manager**: $0.40/month per secret
  - Database credentials
  - Application secrets
  - **Why it costs this much**: Managed secrets service

### Networking (23.8% - $32.82)
- **Application Load Balancer**: $18.83/month
  - Load balancer hours + LCU charges
  - **Why it costs this much**: Always-on service with per-hour + per-LCU pricing
  
- **NAT Gateway**: $7.47/month
  - 2 NAT Gateways for high availability
  - Data processing charges
  - **Why it costs this much**: Per-hour charge + data processing fees
  
- **Data Transfer Out**: $4.50/month
  - Traffic from AWS to internet
  - **Why it costs this much**: First 100GB/month free, then $0.09/GB
  
- **VPC Endpoints**: $2.02/month
  - S3 and ECR endpoints
  - **Why it costs this much**: Per-hour charge per endpoint

### Storage & CDN (3.8% - $5.28)
- **CloudFront**: $4.25/month
  - 50GB data transfer
  - **Why it costs this much**: Pay per GB transferred
  
- **S3**: $0.73/month
  - 10GB storage + requests
  - **Why it costs this much**: Very cheap storage, mostly request costs
  
- **EBS**: $0.30/month
  - Temporary storage for containers
  - **Why it costs this much**: Minimal storage needs

### Monitoring (5.0% - $7.00)
- **CloudWatch Logs**: $5.50/month
  - Log ingestion and storage
  - **Why it costs this much**: $0.50/GB ingestion + $0.03/GB storage
  
- **CloudWatch Metrics**: $1.50/month
  - Custom metrics
  - **Why it costs this much**: $0.30 per metric after first 10 free

---

## 🎯 Cost Optimization Strategies

### Strategy 1: Serverless Architecture (Save ~60% = $83/month)
**New Monthly Cost: ~$55**

#### Architecture Changes
```
Current:                          Optimized:
┌─────────────────┐              ┌─────────────────┐
│  ECS Fargate    │              │  Lambda         │
│  Always On     │  →           │  On-Demand      │
│  $49/month     │              │  $5/month       │
└─────────────────┘              └─────────────────┘

┌─────────────────┐              ┌─────────────────┐
│  RDS Multi-AZ   │              │  Aurora         │
│  $30/month     │  →           │  Serverless v2  │
│                 │              │  $15/month      │
└─────────────────┘              └─────────────────┘

┌─────────────────┐              ┌─────────────────┐
│  ElastiCache    │              │  DynamoDB       │
│  $12/month     │  →           │  On-Demand      │
│                 │              │  $3/month       │
└─────────────────┘              └─────────────────┘

┌─────────────────┐              ┌─────────────────┐
│  ALB            │              │  API Gateway    │
│  $19/month     │  →           │  $3.50/month    │
└─────────────────┘              └─────────────────┘

┌─────────────────┐              ┌─────────────────┐
│  NAT Gateway    │              │  VPC Endpoints  │
│  $7/month      │  →           │  $0/month       │
└─────────────────┘              └─────────────────┘
```

#### Detailed Changes

**1. Replace ECS Fargate with Lambda ($49 → $5)**
```python
# Current: Backend API on ECS (always running)
# Cost: 2 tasks × 730 hours × $0.04048 = $29.55

# Optimized: Lambda functions
# Cost: 1M requests × 512MB × 1s avg = $5.00

# Implementation:
- Convert FastAPI endpoints to Lambda functions
- Use Lambda Powertools for Python
- Deploy with AWS SAM or Serverless Framework
- Cold start: ~500ms (acceptable for governance scans)
```

**2. Replace RDS Multi-AZ with Aurora Serverless v2 ($30 → $15)**
```sql
-- Current: db.t3.micro Multi-AZ (always running)
-- Cost: 2 instances × 730 hours × $0.041 = $29.93

-- Optimized: Aurora Serverless v2
-- Cost: 0.5 ACU × 730 hours × $0.12 = $43.80
-- BUT: Auto-pause after 5 min idle = ~$15/month actual

-- Configuration:
MinCapacity: 0.5 ACU
MaxCapacity: 2 ACU
AutoPause: After 5 minutes
SecondsUntilAutoPause: 300
```

**3. Replace ElastiCache with DynamoDB ($12 → $3)**
```javascript
// Current: Redis cache (always running)
// Cost: cache.t3.micro × 730 hours × $0.017 = $12.41

// Optimized: DynamoDB for caching
// Cost: 1M reads × $0.25 + 100K writes × $1.25 = $2.50

// Implementation:
- Use DynamoDB with TTL for cache expiration
- On-demand billing (no provisioned capacity)
- DAX for read-heavy workloads (optional)
```

**4. Replace ALB with API Gateway ($19 → $3.50)**
```yaml
# Current: Application Load Balancer (always running)
# Cost: 730 hours × $0.0225 + 10 LCU × $0.008 = $18.83

# Optimized: API Gateway HTTP API
# Cost: 1M requests × $0.0000035 = $3.50

# Benefits:
- Pay per request (not per hour)
- Built-in throttling and caching
- Native Lambda integration
- WebSocket support
```

**5. Remove NAT Gateway ($7 → $0)**
```bash
# Current: NAT Gateway for private subnet internet access
# Cost: 2 × 730 hours × $0.045 + 20GB × $0.045 = $7.47

# Optimized: VPC Endpoints only
# Cost: $0 (use S3/DynamoDB gateway endpoints - free)

# Implementation:
- Use S3 Gateway Endpoint (free)
- Use DynamoDB Gateway Endpoint (free)
- Lambda in public subnet with security groups
- No outbound internet needed
```

#### Serverless Architecture Cost Summary
| Service | Current | Optimized | Savings |
|---------|---------|-----------|---------|
| Compute | $49.20 | $5.00 | $44.20 |
| Database | $29.93 | $15.00 | $14.93 |
| Cache | $12.41 | $3.00 | $9.41 |
| Load Balancer | $18.83 | $3.50 | $15.33 |
| NAT Gateway | $7.47 | $0.00 | $7.47 |
| Other | $20.20 | $28.50 | -$8.30 |
| **Total** | **$138.04** | **$55.00** | **$83.04 (60%)** |

---

### Strategy 2: Fargate Spot + Single-AZ (Save ~40% = $55/month)
**New Monthly Cost: ~$83**

#### Architecture Changes
```
Current:                          Optimized:
┌─────────────────┐              ┌─────────────────┐
│  Fargate        │              │  Fargate Spot   │
│  On-Demand     │  →           │  70% cheaper    │
│  $49/month     │              │  $15/month      │
└─────────────────┘              └─────────────────┘

┌─────────────────┐              ┌─────────────────┐
│  RDS Multi-AZ   │              │  RDS Single-AZ  │
│  $30/month     │  →           │  $15/month      │
└─────────────────┘              └─────────────────┘
```

#### Detailed Changes

**1. Use Fargate Spot ($49 → $15)**
```json
{
  "capacityProviderStrategy": [
    {
      "capacityProvider": "FARGATE_SPOT",
      "weight": 4,
      "base": 0
    },
    {
      "capacityProvider": "FARGATE",
      "weight": 1,
      "base": 1
    }
  ]
}

// Cost: $49 × 0.30 = $14.70 (70% savings)
// Trade-off: Tasks may be interrupted (rare)
// Mitigation: Keep 1 on-demand task as base
```

**2. Single-AZ RDS ($30 → $15)**
```bash
# Remove Multi-AZ configuration
aws rds modify-db-instance \
  --db-instance-identifier grc-postgres \
  --no-multi-az

# Cost: $29.93 / 2 = $14.97
# Trade-off: No automatic failover
# Mitigation: Use automated snapshots, manual failover
```

**3. Single NAT Gateway ($7 → $3.50)**
```bash
# Use only 1 NAT Gateway instead of 2
# Cost: $7.47 / 2 = $3.74
# Trade-off: Single point of failure
# Mitigation: Acceptable for non-critical workloads
```

#### Fargate Spot Architecture Cost Summary
| Service | Current | Optimized | Savings |
|---------|---------|-----------|---------|
| ECS Fargate | $49.20 | $14.76 | $34.44 |
| RDS PostgreSQL | $29.93 | $14.97 | $14.96 |
| NAT Gateway | $7.47 | $3.74 | $3.73 |
| Other | $51.44 | $49.53 | $1.91 |
| **Total** | **$138.04** | **$83.00** | **$55.04 (40%)** |

---

### Strategy 3: EC2 Reserved Instances (Save ~35% = $48/month)
**New Monthly Cost: ~$90**

#### Architecture Changes
```
Current:                          Optimized:
┌─────────────────┐              ┌─────────────────┐
│  Fargate        │              │  EC2 t3.small   │
│  On-Demand     │  →           │  Reserved 1yr   │
│  $49/month     │              │  $10/month      │
└─────────────────┘              └─────────────────┘

┌─────────────────┐              ┌─────────────────┐
│  RDS On-Demand  │              │  RDS Reserved   │
│  $30/month     │  →           │  $18/month      │
└─────────────────┘              └─────────────────┘
```

#### Detailed Changes

**1. EC2 with Reserved Instances ($49 → $10)**
```bash
# Purchase 1-year Reserved Instance
# Instance: t3.small (2 vCPU, 2GB RAM)
# Cost: $0.0146/hr × 730 hrs = $10.66/month

# Run Docker containers directly on EC2
docker-compose up -d

# Savings: $49.20 - $10.66 = $38.54/month
# Trade-off: Manage EC2 instances yourself
```

**2. RDS Reserved Instance ($30 → $18)**
```bash
# Purchase 1-year Reserved Instance
# Instance: db.t3.micro Multi-AZ
# Cost: $0.025/hr × 730 hrs × 2 = $18.25/month

# Savings: $29.93 - $18.25 = $11.68/month
# Trade-off: 1-year commitment
```

**3. ElastiCache Reserved Node ($12 → $7)**
```bash
# Purchase 1-year Reserved Node
# Instance: cache.t3.micro
# Cost: $0.010/hr × 730 hrs = $7.30/month

# Savings: $12.41 - $7.30 = $5.11/month
# Trade-off: 1-year commitment
```

#### Reserved Instance Cost Summary
| Service | Current | Optimized | Savings |
|---------|---------|-----------|---------|
| Compute | $49.20 | $10.66 | $38.54 |
| RDS | $29.93 | $18.25 | $11.68 |
| ElastiCache | $12.41 | $7.30 | $5.11 |
| Other | $46.50 | $53.79 | -$7.29 |
| **Total** | **$138.04** | **$90.00** | **$48.04 (35%)** |

---

### Strategy 4: Hybrid Approach (Save ~50% = $69/month)
**New Monthly Cost: ~$69**

#### Best of All Worlds
```
Component          Strategy                Cost
─────────────────────────────────────────────────
Backend API        Lambda (serverless)     $5
Background Jobs    Fargate Spot            $5
Database          Aurora Serverless v2    $15
Cache             DynamoDB                $3
Load Balancer     API Gateway             $3.50
Networking        VPC Endpoints only      $0
Frontend          CloudFront + S3         $5
Monitoring        CloudWatch              $7
Secrets           Secrets Manager         $1
Storage           S3                      $1
Data Transfer     Optimized               $3
─────────────────────────────────────────────────
TOTAL                                     $48.50
```

#### Implementation Strategy
1. **API Endpoints** → Lambda (on-demand)
2. **Long-running Scans** → Fargate Spot (interruptible OK)
3. **Database** → Aurora Serverless v2 (auto-pause)
4. **Cache** → DynamoDB (on-demand)
5. **Frontend** → CloudFront + S3 (static)

---

## 📊 Cost Comparison Matrix

| Architecture | Monthly Cost | Savings | Availability | Complexity | Best For |
|--------------|--------------|---------|--------------|------------|----------|
| **Current (Fargate + RDS Multi-AZ)** | $138 | 0% | 99.99% | Medium | Production, HA required |
| **Serverless (Lambda + Aurora)** | $55 | 60% | 99.95% | High | Low traffic, cost-sensitive |
| **Fargate Spot + Single-AZ** | $83 | 40% | 99.5% | Low | Dev/staging, acceptable downtime |
| **EC2 Reserved Instances** | $90 | 35% | 99.9% | Medium | Predictable workload, 1yr+ |
| **Hybrid Approach** | $69 | 50% | 99.9% | High | Balanced cost/performance |

---

## 🎯 Recommended Optimization Path

### Phase 1: Quick Wins (Save $20/month, 1 hour)
1. ✅ Enable Fargate Spot for Celery worker → Save $10
2. ✅ Reduce RDS to Single-AZ for dev → Save $15
3. ✅ Use single NAT Gateway → Save $4
4. ✅ Set CloudWatch log retention to 7 days → Save $3
5. ✅ Enable S3 Intelligent-Tiering → Save $0.50

**New Cost: $118/month (14% savings)**

### Phase 2: Architectural Changes (Save $50/month, 1 week)
1. ✅ Migrate API to Lambda functions → Save $25
2. ✅ Replace ElastiCache with DynamoDB → Save $9
3. ✅ Use Aurora Serverless v2 → Save $15
4. ✅ Replace ALB with API Gateway → Save $15
5. ✅ Remove NAT Gateway → Save $7

**New Cost: $68/month (51% savings)**

### Phase 3: Long-term (Save $48/month, ongoing)
1. ✅ Purchase Reserved Instances (if staying with EC2/RDS)
2. ✅ Implement auto-scaling policies
3. ✅ Use Savings Plans
4. ✅ Regular cost reviews
5. ✅ Optimize data transfer

**New Cost: $55-90/month (35-60% savings)**

---

## 💡 Alternative Architectures

### Option A: Pure Serverless ($55/month)
```yaml
Frontend: S3 + CloudFront
API: Lambda + API Gateway
Database: Aurora Serverless v2
Cache: DynamoDB
Queue: SQS
Storage: S3
Monitoring: CloudWatch

Pros:
  - Lowest cost
  - Auto-scaling
  - No server management
  - Pay per use

Cons:
  - Cold starts (500ms)
  - Lambda limits (15min timeout)
  - More complex architecture
  - Vendor lock-in
```

### Option B: Container on EC2 ($65/month)
```yaml
Compute: t3.small EC2 Reserved Instance
Database: RDS t3.micro Reserved Instance
Cache: Redis on same EC2
Load Balancer: None (direct access)
Frontend: S3 + CloudFront

Pros:
  - Lowest cost with commitment
  - Full control
  - No cold starts
  - Simple architecture

Cons:
  - Manage EC2 yourself
  - No auto-scaling
  - Single point of failure
  - 1-year commitment
```

### Option C: Kubernetes on EKS ($120/month)
```yaml
Compute: EKS cluster + Fargate
Database: RDS Multi-AZ
Cache: ElastiCache
Load Balancer: ALB
Frontend: S3 + CloudFront

Pros:
  - Enterprise-grade
  - Multi-cloud portable
  - Advanced features
  - Great for scale

Cons:
  - Higher cost ($72 EKS control plane)
  - Complex setup
  - Overkill for small apps
  - Steep learning curve
```

### Option D: App Runner ($75/month)
```yaml
Compute: AWS App Runner
Database: Aurora Serverless v2
Cache: DynamoDB
Load Balancer: Built-in
Frontend: S3 + CloudFront

Pros:
  - Easiest deployment
  - Auto-scaling
  - Built-in CI/CD
  - No infrastructure management

Cons:
  - Less control
  - Limited customization
  - Newer service
  - Regional availability
```

---

## 📈 Cost Scaling Analysis

### Current Architecture Scaling
```
Users    Requests/Month    Monthly Cost
─────────────────────────────────────────
10       100K              $138
100      1M                $158 (+14%)
1,000    10M               $298 (+116%)
10,000   100M              $1,180 (+755%)
```

### Serverless Architecture Scaling
```
Users    Requests/Month    Monthly Cost
─────────────────────────────────────────
10       100K              $55
100      1M                $58 (+5%)
1,000    10M               $85 (+55%)
10,000   100M              $380 (+591%)
```

**Key Insight**: Serverless scales better with traffic!

---

## 🎯 Final Recommendations

### For Development/Testing
**Use: Fargate Spot + Single-AZ RDS**
- Cost: $83/month (40% savings)
- Easy to implement
- Acceptable downtime
- Quick to set up

### For Production (Low Traffic)
**Use: Serverless Architecture**
- Cost: $55/month (60% savings)
- Scales automatically
- Pay per use
- Best cost efficiency

### For Production (High Availability)
**Use: Current Architecture + Quick Wins**
- Cost: $118/month (14% savings)
- Maintain high availability
- Minimal changes
- Production-ready

### For Long-term Production
**Use: Hybrid Approach**
- Cost: $69/month (50% savings)
- Balance cost and performance
- Scalable architecture
- Best of both worlds

---

## ✅ Action Items

### Immediate (This Week)
1. [ ] Enable Fargate Spot for non-critical tasks
2. [ ] Set CloudWatch log retention to 7-14 days
3. [ ] Review and delete unused resources
4. [ ] Enable Cost Explorer and set up budgets

### Short-term (This Month)
1. [ ] Evaluate serverless migration for API
2. [ ] Test Aurora Serverless v2 in dev
3. [ ] Implement auto-scaling policies
4. [ ] Set up cost alerts

### Long-term (This Quarter)
1. [ ] Purchase Reserved Instances if staying with current arch
2. [ ] Migrate to serverless if traffic is low
3. [ ] Implement FinOps practices
4. [ ] Regular cost reviews

---

**Bottom Line**: You can reduce costs by 40-60% while maintaining the same functionality by choosing the right architecture for your traffic patterns and availability requirements.

**Best Quick Win**: Enable Fargate Spot → Save $10/month in 5 minutes  
**Best Long-term**: Migrate to serverless → Save $83/month over 1-2 weeks

---

**Cost Analysis Version**: 1.0  
**Last Updated**: October 14, 2025  
**Next Review**: Monthly
