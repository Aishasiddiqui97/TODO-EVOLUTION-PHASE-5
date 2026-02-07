# Production Deployment Checklist

**Event-Driven Todo Chatbot - Local Kubernetes Deployment**
**Status:** 100% Implementation Complete
**Date:** February 6, 2026

---

## ✅ Pre-Deployment Checklist

### Infrastructure Requirements
- [ ] Minikube installed (v1.32+) or Docker Desktop with Kubernetes enabled
- [ ] kubectl installed (v1.28+)
- [ ] Dapr CLI installed (v1.12+)
- [ ] Docker installed (v20.10+)
- [ ] Minimum resources: 4 CPUs, 8GB RAM

### Configuration Files
- [x] All Dapr components configured (PubSub, State Store, Secrets)
- [x] All Kubernetes manifests created
- [x] All Dockerfiles created
- [x] Kustomize overlays configured (local/cloud)
- [x] Deployment scripts created

### Secrets Configuration
- [ ] OpenRouter API key obtained from https://openrouter.ai/keys
- [ ] Create Kubernetes secret for OpenRouter API key:
  ```bash
  kubectl create secret generic app-secrets \
    --from-literal=openrouter-api-key="YOUR_OPENROUTER_API_KEY" \
    -n todo-chatbot-local
  ```
- [ ] SMTP credentials configured (if using email notifications)

---

## 🚀 Deployment Steps

### Step 1: Start Kubernetes Cluster
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
```

**Expected Output:**
```
Kubernetes control plane is running at https://...
```

**Validation:**
- [ ] Cluster is running
- [ ] kubectl can connect to cluster

---

### Step 2: Initialize Dapr
```bash
# Initialize Dapr on Kubernetes
dapr init -k --wait

# Verify Dapr installation
dapr status -k
```

**Expected Output:**
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
dapr-operator          dapr-system  True     Running  1         1.12.0   ...
dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   ...
dapr-sentry            dapr-system  True     Running  1         1.12.0   ...
dapr-placement         dapr-system  True     Running  1         1.12.0   ...
```

**Validation:**
- [ ] All Dapr components are healthy
- [ ] Dapr version is 1.12.0+

---

### Step 3: Create Namespace
```bash
# Create namespace
kubectl create namespace todo-chatbot-local

# Verify namespace
kubectl get namespaces | grep todo-chatbot-local
```

**Validation:**
- [ ] Namespace created successfully

---

### Step 4: Deploy Infrastructure
```bash
# Deploy PostgreSQL
kubectl apply -f k8s/local/postgres.yaml -n todo-chatbot-local

# Deploy Redpanda (Kafka)
kubectl apply -f k8s/local/redpanda.yaml -n todo-chatbot-local

# Deploy MailHog (email testing)
kubectl apply -f k8s/local/mailhog.yaml -n todo-chatbot-local

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n todo-chatbot-local --timeout=120s
kubectl wait --for=condition=ready pod -l app=redpanda -n todo-chatbot-local --timeout=120s
kubectl wait --for=condition=ready pod -l app=mailhog -n todo-chatbot-local --timeout=60s
```

**Validation:**
- [ ] PostgreSQL pod is running
- [ ] Redpanda pod is running
- [ ] MailHog pod is running

---

### Step 5: Deploy Dapr Components
```bash
# Deploy Dapr components
kubectl apply -f k8s/dapr/pubsub-local.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/statestore-local.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/secretstore-local.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/local-secrets.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/jobs-config.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/resiliency.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/tracing.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/config.yaml -n todo-chatbot-local

# Deploy event subscriptions
kubectl apply -f k8s/dapr/subscription-chat-api.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/subscription-recurring-task.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/subscription-notification.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/subscription-audit-log.yaml -n todo-chatbot-local
kubectl apply -f k8s/dapr/subscription-websocket-sync.yaml -n todo-chatbot-local

# Verify components
dapr components -k -n todo-chatbot-local
```

**Validation:**
- [ ] All Dapr components are loaded
- [ ] All subscriptions are created

---

### Step 6: Build Docker Images
```bash
# Set Minikube Docker environment
eval $(minikube docker-env)

# Build all service images
docker build -t todo-chatbot/chat-api:latest -f backend/src/services/chat-api/Dockerfile .
docker build -t todo-chatbot/recurring-task:latest -f backend/src/services/recurring-task/Dockerfile .
docker build -t todo-chatbot/notification:latest -f backend/src/services/notification/Dockerfile .
docker build -t todo-chatbot/websocket-sync:latest -f backend/src/services/websocket-sync/Dockerfile .
docker build -t todo-chatbot/audit-log:latest -f backend/src/services/audit-log/Dockerfile .

# Verify images
docker images | grep todo-chatbot
```

**Validation:**
- [ ] All 5 images built successfully
- [ ] Images are available in Minikube Docker

---

### Step 7: Deploy Observability Stack
```bash
# Deploy Prometheus and Zipkin
kubectl apply -f k8s/observability/prometheus.yaml -n todo-chatbot-local
kubectl apply -f k8s/observability/zipkin.yaml -n todo-chatbot-local

# Wait for observability stack
kubectl wait --for=condition=ready pod -l app=prometheus -n todo-chatbot-local --timeout=60s
kubectl wait --for=condition=ready pod -l app=zipkin -n todo-chatbot-local --timeout=60s
```

**Validation:**
- [ ] Prometheus is running
- [ ] Zipkin is running

---

### Step 8: Deploy Microservices
```bash
# Deploy using Kustomize
kubectl apply -k k8s/overlays/local

# Or deploy individually
kubectl apply -f k8s/base/chat-api/ -n todo-chatbot-local
kubectl apply -f k8s/base/recurring-task/ -n todo-chatbot-local
kubectl apply -f k8s/base/notification/ -n todo-chatbot-local
kubectl apply -f k8s/base/websocket-sync/ -n todo-chatbot-local
kubectl apply -f k8s/base/audit-log/ -n todo-chatbot-local

# Wait for all services to be ready
kubectl wait --for=condition=available deployment/chat-api -n todo-chatbot-local --timeout=300s
kubectl wait --for=condition=available deployment/recurring-task -n todo-chatbot-local --timeout=300s
kubectl wait --for=condition=available deployment/notification -n todo-chatbot-local --timeout=300s
kubectl wait --for=condition=available deployment/websocket-sync -n todo-chatbot-local --timeout=300s
kubectl wait --for=condition=available deployment/audit-log -n todo-chatbot-local --timeout=300s
```

**Validation:**
- [ ] All 5 services are deployed
- [ ] All deployments are available
- [ ] All pods are running

---

## ✅ Post-Deployment Validation

### Step 9: Verify Service Health
```bash
# Check all pods
kubectl get pods -n todo-chatbot-local

# Check services
kubectl get svc -n todo-chatbot-local

# Check Dapr components
dapr components -k -n todo-chatbot-local

# Check subscriptions
kubectl get subscriptions -n todo-chatbot-local
```

**Expected Output:**
- All pods should be in "Running" state
- All services should have endpoints
- All Dapr components should be loaded
- All subscriptions should be active

**Validation:**
- [ ] All pods are running (5 services + infrastructure)
- [ ] No pods in CrashLoopBackOff or Error state
- [ ] All services have ClusterIP or NodePort assigned
- [ ] Dapr sidecars are injected (2 containers per pod)

---

### Step 10: Test Service Endpoints

#### Port Forward Services
```bash
# Chat API
kubectl port-forward svc/chat-api 8001:80 -n todo-chatbot-local &

# WebSocket Sync
kubectl port-forward svc/websocket-sync 8004:80 -n todo-chatbot-local &

# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n todo-chatbot-local &

# Zipkin
kubectl port-forward svc/zipkin 9411:9411 -n todo-chatbot-local &

# MailHog UI
kubectl port-forward svc/mailhog 8025:8025 -n todo-chatbot-local &
```

#### Health Checks
```bash
# Chat API
curl http://localhost:8001/health

# Expected: {"status":"healthy","service":"chat-api",...}

# Recurring Task Service
kubectl exec -it deployment/recurring-task -n todo-chatbot-local -- curl localhost:8002/health

# Notification Service
kubectl exec -it deployment/notification -n todo-chatbot-local -- curl localhost:8003/health

# WebSocket Sync Service
curl http://localhost:8004/health

# Audit Log Service
kubectl exec -it deployment/audit-log -n todo-chatbot-local -- curl localhost:8005/health
```

**Validation:**
- [ ] Chat API health check returns 200
- [ ] Recurring Task health check returns 200
- [ ] Notification health check returns 200
- [ ] WebSocket Sync health check returns 200
- [ ] Audit Log health check returns 200

---

### Step 11: Test API Functionality

#### Create Task via REST API
```bash
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing the API",
    "priority": "high",
    "userId": "user-001"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-...",
    "title": "Test Task",
    "priority": "high",
    "status": "pending",
    ...
  },
  "message": "Task 'Test Task' created successfully"
}
```

**Validation:**
- [ ] Task created successfully
- [ ] Task ID returned
- [ ] Response includes all task fields

#### List Tasks
```bash
curl http://localhost:8001/api/v1/tasks?userId=user-001
```

**Validation:**
- [ ] Returns list of tasks
- [ ] Includes the task created above

#### Chat with AI
```bash
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to review proposal by Friday",
    "userId": "user-001"
  }'
```

**Validation:**
- [ ] AI responds with confirmation
- [ ] Task is created via MCP tool
- [ ] Conversation ID is returned

#### Search Tasks
```bash
curl -X POST http://localhost:8001/api/v1/tasks/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me high-priority tasks",
    "userId": "user-001"
  }'
```

**Validation:**
- [ ] Search returns matching tasks
- [ ] Query parsing works correctly

---

### Step 12: Test Event Flow

#### Check Event Publishing
```bash
# View Chat API logs for event publishing
kubectl logs -l app=chat-api -n todo-chatbot-local | grep "Event published"

# View Recurring Task service logs for event consumption
kubectl logs -l app=recurring-task -n todo-chatbot-local | grep "Event received"

# View Audit Log service logs
kubectl logs -l app=audit-log -n todo-chatbot-local | grep "Audit log"
```

**Validation:**
- [ ] Events are being published by Chat API
- [ ] Events are being consumed by other services
- [ ] Audit logs are being created

---

### Step 13: Test Recurring Tasks

#### Create Recurring Task
```bash
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "recurrencePattern": "every day",
    "priority": "medium",
    "userId": "user-001"
  }'
```

#### Complete the Task
```bash
# Get task ID from response, then complete it
curl -X PATCH http://localhost:8001/api/v1/tasks/{task-id}/complete
```

#### Check for Next Instance
```bash
# Wait a few seconds, then list tasks
curl http://localhost:8001/api/v1/tasks?userId=user-001
```

**Validation:**
- [ ] Recurring task created
- [ ] Task completed successfully
- [ ] Next instance created automatically
- [ ] Recurring Task service logs show processing

---

### Step 14: Test Notifications

#### Check Notification Service
```bash
# View notification service logs
kubectl logs -l app=notification -n todo-chatbot-local -f
```

#### Access MailHog UI
```
Open browser: http://localhost:8025
```

**Validation:**
- [ ] Notification service is processing events
- [ ] Emails appear in MailHog (if configured)

---

### Step 15: Test Real-Time Sync

#### Check WebSocket Service
```bash
# View WebSocket sync logs
kubectl logs -l app=websocket-sync -n todo-chatbot-local -f
```

#### Test WebSocket Connection (using wscat)
```bash
# Install wscat if needed: npm install -g wscat
wscat -c ws://localhost:8004/ws?userId=user-001
```

**Validation:**
- [ ] WebSocket connection established
- [ ] Real-time updates received when tasks change

---

### Step 16: Monitor Observability

#### Prometheus
```
Open browser: http://localhost:9090
```

**Queries to test:**
- `dapr_http_server_request_count`
- `dapr_http_server_request_duration_ms`
- `up{job="kubernetes-pods"}`

**Validation:**
- [ ] Prometheus is scraping metrics
- [ ] Dapr metrics are available
- [ ] Service metrics are being collected

#### Zipkin
```
Open browser: http://localhost:9411
```

**Validation:**
- [ ] Distributed traces are visible
- [ ] Service dependencies are mapped
- [ ] Request flows can be traced

---

## 🔍 Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl get pods -n todo-chatbot-local

# Describe pod for events
kubectl describe pod <pod-name> -n todo-chatbot-local

# Check logs
kubectl logs <pod-name> -n todo-chatbot-local
kubectl logs <pod-name> -c daprd -n todo-chatbot-local
```

### Events Not Flowing
```bash
# Check Dapr components
dapr components -k -n todo-chatbot-local

# Check subscriptions
kubectl get subscriptions -n todo-chatbot-local

# Check Redpanda
kubectl exec -it deployment/redpanda -n todo-chatbot-local -- rpk topic list
```

### Service Errors
```bash
# View service logs
kubectl logs -l app=chat-api -n todo-chatbot-local --tail=100

# Check Dapr sidecar logs
kubectl logs -l app=chat-api -c daprd -n todo-chatbot-local --tail=100
```

---

## ✅ Final Validation Checklist

### Infrastructure
- [ ] Kubernetes cluster is running
- [ ] Dapr is initialized and healthy
- [ ] PostgreSQL is running
- [ ] Redpanda is running
- [ ] MailHog is running

### Services
- [ ] Chat API is running and healthy
- [ ] Recurring Task service is running and healthy
- [ ] Notification service is running and healthy
- [ ] WebSocket Sync service is running and healthy
- [ ] Audit Log service is running and healthy

### Functionality
- [ ] Can create tasks via REST API
- [ ] Can list tasks
- [ ] Can update tasks
- [ ] Can complete tasks
- [ ] Can delete tasks
- [ ] Can search tasks
- [ ] Can chat with AI
- [ ] Recurring tasks work
- [ ] Notifications are sent
- [ ] Real-time sync works
- [ ] Audit logs are created

### Observability
- [ ] Prometheus is collecting metrics
- [ ] Zipkin is showing traces
- [ ] Logs are accessible
- [ ] Health checks pass

### Event Flow
- [ ] Events are published
- [ ] Events are consumed
- [ ] PubSub is working
- [ ] State Store is working

---

## 🎉 Success Criteria

**System is production-ready when:**
- ✅ All 5 microservices are running
- ✅ All health checks pass
- ✅ Can create and manage tasks via API
- ✅ AI chat interface works
- ✅ Events flow between services
- ✅ Recurring tasks auto-create
- ✅ Notifications are sent
- ✅ Real-time sync works
- ✅ Observability stack is functional
- ✅ No errors in logs

---

## 📝 Notes

- **OpenAI API Key**: Required for AI chat functionality
- **Resource Usage**: Monitor CPU and memory usage
- **Scaling**: Increase replicas if needed
- **Persistence**: Redis data is ephemeral in local setup
- **Email**: MailHog is for testing only

---

**Deployment Checklist Version:** 1.0
**Last Updated:** February 6, 2026
**Status:** Ready for Production Deployment
