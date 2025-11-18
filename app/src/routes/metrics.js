const express = require('express');
const router = express.Router();
const { getMemoryInfo, getMemoryLimits, formatBytes } = require('../utils/memory-utils');

// Эндпоинт для метрик Prometheus
router.get('/', (req, res) => {
    const { getRequestCount } = require('../middleware/metrics');
    const memoryUsage = process.memoryUsage();
    const limits = getMemoryLimits();
    const usagePercent = (memoryUsage.heapUsed / limits.actualLimit) * 100;
    
    const metrics = `
# HELP nodejs_memory_usage_bytes Memory usage in bytes
# TYPE nodejs_memory_usage_bytes gauge
nodejs_memory_usage_bytes ${memoryUsage.heapUsed}

# HELP nodejs_memory_usage_percent Memory usage percentage of limit
# TYPE nodejs_memory_usage_percent gauge
nodejs_memory_usage_percent ${usagePercent}

# HELP container_memory_limit_bytes Container memory limit in bytes
# TYPE container_memory_limit_bytes gauge
container_memory_limit_bytes ${limits.actualLimit}

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total ${getRequestCount()}  
    `;
    
    res.set('Content-Type', 'text/plain');
    res.send(metrics);
});

// Информация о памяти
router.get('/memory-info', (req, res) => {
    const memoryInfo = getMemoryInfo();
    res.json(memoryInfo);
});

// Отладочная информация о контейнере
router.get('/debug-container', (req, res) => {
    const fs = require('fs');
    
    const checks = {
        '/.dockerenv': fs.existsSync('/.dockerenv'),
        '/proc/1/cgroup': (() => {
            try {
                const content = fs.readFileSync('/proc/1/cgroup', 'utf8');
                return content.includes('docker') || content.includes('kubepods');
            } catch (e) {
                return false;
            }
        })(),
        'memory.max exists': fs.existsSync('/sys/fs/cgroup/memory.max'),
        'memory.high exists': fs.existsSync('/sys/fs/cgroup/memory.high'),
        'memory.limit_in_bytes exists': fs.existsSync('/sys/fs/cgroup/memory/memory.limit_in_bytes')
    };
    
    // Читаем что в memory.max
    if (checks['memory.max exists']) {
        try {
            checks['memory.max content'] = fs.readFileSync('/sys/fs/cgroup/memory.max', 'utf8').trim();
        } catch (e) {
            checks['memory.max content'] = 'error: ' + e.message;
        }
    }
    
    res.json(checks);
});

module.exports = router;