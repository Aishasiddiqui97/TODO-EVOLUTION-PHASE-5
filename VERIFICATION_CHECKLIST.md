# MVP Verification Checklist

Use this checklist to verify the Phase V MVP implementation is complete and working.

## ✅ Pre-Deployment Verification

### Environment Setup
- [ ] Docker Desktop installed and running
- [ ] kubectl CLI installed
- [ ] Minikube installed (for Kubernetes deployment)
- [ ] Dapr CLI installed
- [ ] OpenRouter API key obtained from https://openrouter.ai/keys
- [ ] Git Bash or WSL installed (Windows users)

### Configuration
- [ ] `backend/.env` file created from `.env.example`
- [ ] `OPENROUTER_API_KEY` set in `.env` file
- [ ] All required ports available (8000, 5432, 9092, 3500, 50001)

## ✅ Code Verification

### Shared Libraries
- [ ] `backend/src/shared/dapr_client/client.py` exists
- [ ] `backend/src/shared/events/publisher.py` exists
- [ ] `backend/src/shared/models/task.py` exists
- [ ] `backend/src/shared/utils/state_keys.py` exists
- [ ] `backend/src/shared/utils/idempotency.py` exists
- [ ] `backend/src/shared/utils/logging.py` exists

### MCP Tools
- [ ] `backend/src/mcp/tools/create_task.py` exists
- [ ] `backend/src/mcp/tools/update_task.py` exists
- [ ] `backend/src/mcp/tools/complete_task.py` exists
- [ ] `backend/src/mcp/tools/delete_task.py` exists
- [ ] `backend/src/mcp/tools/list_tasks.py` exists
- [ ] `backend/src/mcp/server.py` exists

### API Implementation
- [ ] `backend/src/main.py` exists
- [ ] `backend/src/api/routes/tasks.py` exists
- [ ] `backend/src/api/routes/chat.py` exists
- [ ] `backend/src/ai/agent.py` exists

### Dapr Components
- [ ] `k8s/dapr/pubsub-local.yaml` exists
- [ ] `k8s/dapr/statestore-local.yaml` exists
- [ ] `k8s/dapr/secretstore-local.yaml` exists
- [ ] `k8s/dapr/resiliency.yaml` exists
- [ ] All subscription files exist

### Kubernetes Manifests
- [ ] `k8s/local/postgres.yaml` exists
- [ ] `k8s/local/redpanda.yaml` exists
- [ ] `k8s/services/chat-api-deployment.yaml` exists
- [ ] `k8s/services/chat-api-service.yaml` exists

### Deployment Files
- [ ] `backend/Dockerfile` exists
- [ ] `docker-compose.yml` exists
- [ ] `deploy-local.sh` exists (Linux/Mac)
- [ ] `deploy-local.bat` exists (Windows)
- [ ] `test-api.sh` exists
- [ ] `Makefile` exists

### Documentation
- [ ] `README.md` exists
- [ ] `QUICKSTART.md` exists
- [ ] `API_EXAMPLES.md` exists
- [ ] `TROUBLESHOOTING.md` exists
- [ ] `IMPLEMENTATION_STATUS.md` exists
- [ ] `SUMMARY.md` exists

## ✅ Docker Compose Deployment

### Build and Start
```bash
docker-compose up -d
```
- [ ] All services start successfully
- [ ] No error messages in logs
- [ ] Services show as "healthy" in `docker-compose ps`

### Service Health Checks
```bash
# PostgreSQL
docker-compose exec db psql -U todouser -d todoapp -c "SELECT 1"
```
- [ ] PostgreSQL responds

```bash
# Redpanda
docker-compose exec redpanda rpk cluster health
```
- [ ] Redpanda shows healthy

```bash
# Chat API
curl http://localhost:8000/health
```
- [ ] Returns `{"status": "healthy"}`

### API Testing
```bash
# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "priority": "high"}'
```
- [ ] Returns task with ID

```bash
# List tasks
curl http://localhost:8000/api/v1/tasks
```
- [ ] Returns array with created task

```bash
# Chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my tasks"}'
```
- [ ] Returns chat response

### Event Verification
```bash
# View events in Kafka
docker-compose exec redpanda rpk topic consume task-events --num 1
```
- [ ] Shows task.created event

### Cleanup
```bash
docker-compose down -v
```
- [ ] All services stopped
- [ ] Volumes removed

## ✅ Kubernetes Deployment

### Cluster Setup
```bash
minikube start --cpus=4 --memory=8192
```
- [ ] Minikube starts successfully

```bash
dapr init -k
```
- [ ] Dapr installed in cluster

### Secret Creation
```bash
kubectl create secret generic app-secrets \
  --from-literal=openrouter-api-key="your-key"
```
- [ ] Secret created

### Infrastructure Deployment
```bash
kubectl apply -f k8s/local/
```
- [ ] PostgreSQL pod running
- [ ] Redpanda pod running

```bash
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=120s
```
- [ ] All infrastructure pods ready

### Dapr Components
```bash
kubectl apply -f k8s/dapr/
```
- [ ] All components created

```bash
kubectl get components
```
- [ ] Shows statestore, pubsub, secretstore

```bash
kubectl get subscriptions
```
- [ ] Shows all subscriptions

### Application Deployment
```bash
docker build -t chat-api:latest -f backend/Dockerfile .
minikube image load chat-api:latest
kubectl apply -f k8s/services/
```
- [ ] Image built successfully
- [ ] Image loaded to Minikube
- [ ] Deployment created

```bash
kubectl wait --for=condition=ready pod -l app=chat-api --timeout=180s
```
- [ ] Chat API pod ready

### Pod Verification
```bash
kubectl get pods
```
- [ ] All pods in Running state
- [ ] Chat API shows 2/2 containers (app + daprd)

```bash
kubectl logs -f deployment/chat-api -c chat-api --tail=20
```
- [ ] No error messages
- [ ] Shows "Starting Chat API service"
- [ ] Shows "Dapr client initialized"
- [ ] Shows "Registered 5 MCP tools"

```bash
kubectl logs -f deployment/chat-api -c daprd --tail=20
```
- [ ] Dapr sidecar running
- [ ] Components loaded

### API Testing (Port Forward)
```bash
kubectl port-forward svc/chat-api 8000:8000
```
- [ ] Port forward established

```bash
curl http://localhost:8000/health
```
- [ ] Returns healthy status

```bash
bash test-api.sh
```
- [ ] All 9 tests pass

### Event Flow Verification
```bash
# Create a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "K8s Test", "priority": "high"}'

# Check events
kubectl exec -it deployment/redpanda -- \
  rpk topic consume task-events --num 1
```
- [ ] Event appears in Kafka

### State Verification
```bash
# Create task and note ID
TASK_ID="<task-id-from-response>"

# Verify in state store
kubectl exec -it deployment/postgres -- \
  psql -U todouser -d todoapp -c \
  "SELECT * FROM state WHERE key LIKE '%${TASK_ID}%'"
```
- [ ] Task exists in state store

### Cleanup
```bash
kubectl delete -f k8s/services/
kubectl delete -f k8s/dapr/
kubectl delete -f k8s/local/
minikube stop
```
- [ ] All resources deleted

## ✅ Automated Test Suite

```bash
bash test-api.sh
```

Expected output:
```
🧪 Testing Event-Driven Todo Chatbot API
==========================================

Test 1: Health Check
--------------------
✅ Health check passed

Test 2: Root Endpoint
---------------------
✅ Root endpoint passed

Test 3: Create Task
-------------------
✅ Task created with ID: <uuid>

Test 4: List Tasks
------------------
✅ Task listing passed

Test 5: Get Task by ID
----------------------
✅ Get task by ID passed

Test 6: Update Task
-------------------
✅ Task update passed

Test 7: Complete Task
---------------------
✅ Task completion passed

Test 8: Chat Endpoint
---------------------
✅ Chat endpoint passed

Test 9: Delete Task
-------------------
✅ Task deletion passed

==========================================
✅ All tests passed!
==========================================
```

- [ ] All 9 tests pass

## ✅ Documentation Review

- [ ] README.md is clear and accurate
- [ ] QUICKSTART.md provides working instructions
- [ ] API_EXAMPLES.md examples work
- [ ] TROUBLESHOOTING.md covers common issues
- [ ] All code has proper docstrings

## ✅ Production Readiness (Future)

### Security
- [ ] Authentication implemented
- [ ] Authorization implemented
- [ ] API rate limiting
- [ ] Input validation
- [ ] CORS properly configured
- [ ] Secrets management

### Monitoring
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Alert rules
- [ ] Log aggregation
- [ ] Distributed tracing

### Testing
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Load tests
- [ ] Security tests

### Operations
- [ ] CI/CD pipeline
- [ ] Automated deployments
- [ ] Backup and restore
- [ ] Disaster recovery
- [ ] Runbooks

## 📝 Sign-off

**Verified by:** _______________
**Date:** _______________
**Environment:** [ ] Docker Compose [ ] Kubernetes
**Status:** [ ] Pass [ ] Fail

**Notes:**
_______________________________________
_______________________________________
_______________________________________

## 🎉 Completion

Once all checkboxes are marked:
- ✅ MVP is verified and working
- ✅ Ready for demonstration
- ✅ Ready for next phase development
- ✅ Ready for production hardening

**Next Steps:**
1. Implement User Story 2 (Recurring Tasks)
2. Add authentication and authorization
3. Enhance AI integration with full OpenAI Agents SDK
4. Deploy to cloud (AKS/GKE/OKE)
