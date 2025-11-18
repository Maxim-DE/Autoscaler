const fs = require('fs');
const v8 = require('v8');
const os = require('os');

function getMemoryLimits() {
    let dockerMemoryLimit = 'unknown';
    
    try {
        // Для cgroups v2
        const cgroupPath = '/sys/fs/cgroup/memory.max';
        
        if (fs.existsSync(cgroupPath)) {
            const content = fs.readFileSync(cgroupPath, 'utf8').trim();
            
            if (content === 'max') {
                dockerMemoryLimit = 'no_limit_set';
            } else {
                dockerMemoryLimit = parseInt(content);
            }
        } else {
            dockerMemoryLimit = 'cgroup_not_found';
        }
        
    } catch (e) {
        dockerMemoryLimit = 'error_reading_cgroup';
    }
    
    // Лимит Node.js
    const nodeJsLimit = v8.getHeapStatistics().heap_size_limit;
    
    // Общая память системы
    const totalSystemMemory = os.totalmem();
    
    // Определяем реальный лимит
    let actualLimit;
    if (typeof dockerMemoryLimit === 'number') {
        actualLimit = Math.min(dockerMemoryLimit, nodeJsLimit);
    } else {
        actualLimit = nodeJsLimit;
    }
    
    return {
        dockerMemoryLimit: dockerMemoryLimit,
        nodeJsLimit: nodeJsLimit,
        totalSystemMemory: totalSystemMemory,
        actualLimit: actualLimit,
        inContainer: true
    };
}

// Вспомогательная функция для форматирования байтов
function formatBytes(bytes) {
    if (typeof bytes !== 'number') return String(bytes);
    if (bytes === 0) return '0 Bytes';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function getMemoryInfo() {
    const limits = getMemoryLimits();
    const memoryUsage = process.memoryUsage();
    
    const usagePercent = ((memoryUsage.heapUsed / limits.actualLimit) * 100).toFixed(2);
    
    return {
        inContainer: true,
        dockerMemoryLimit: limits.dockerMemoryLimit,
        dockerMemoryLimitHuman: formatBytes(limits.dockerMemoryLimit),
        nodeJsLimit: limits.nodeJsLimit,
        nodeJsLimitHuman: formatBytes(limits.nodeJsLimit),
        totalSystemMemory: limits.totalSystemMemory,
        totalSystemMemoryHuman: formatBytes(limits.totalSystemMemory),
        actualEffectiveLimit: limits.actualLimit,
        actualEffectiveLimitHuman: formatBytes(limits.actualLimit),
        currentHeapUsed: memoryUsage.heapUsed,
        currentHeapUsedHuman: formatBytes(memoryUsage.heapUsed),
        currentHeapTotal: memoryUsage.heapTotal,
        usagePercent: usagePercent + '%',
        usagePercentNumber: parseFloat(usagePercent)
    };
}

module.exports = {
    getMemoryLimits,
    formatBytes,
    getMemoryInfo
};